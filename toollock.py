# Toollock and general Tool support
#
# Copyright (C) 2022  Andrei Ignat <andrei@ignat.se>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class ToolLock:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = config.get_printer().lookup_object('gcode')
        gcode_macro = self.printer.load_object(config, 'gcode_macro')

        self.global_offset = [0, 0, 0]    # Global offset to apply to all tools
        self.saved_fan_speed = 0          # Saved partcooling fan speed when deselecting a tool with a fan.
        self.tool_current = "-2"          # -2 Unknown tool locked, -1 No tool locked, 0 and up are tools.
        self.init_printer_to_last_tool = config.getboolean(
            'init_printer_to_last_tool', True)
        self.purge_on_toolchange = config.getboolean(
            'purge_on_toolchange', True)
        self.saved_position = None
        self.restore_position_on_toolchange = 0   # 0: Don't restore; 1: Restore XY; 2: Restore XYZ

        # G-Code macros
        self.tool_lock_gcode_template = gcode_macro.load_template(config, 'tool_lock_gcode', '')
        self.tool_unlock_gcode_template = gcode_macro.load_template(config, 'tool_unlock_gcode', '')

        # Register commands
        handlers = [
            'SAVE_CURRENT_TOOL', 'TOOL_LOCK', 'TOOL_UNLOCK',
            'T_1', 'SET_AND_SAVE_FAN_SPEED', 'TEMPERATURE_WAIT_WITH_TOLERANCE', 
            'SET_TOOL_TEMPERATURE', 'SET_GLOBAL_OFFSET', 'SET_TOOL_OFFSET',
            'SET_PURGE_ON_TOOLCHANGE', 'SAVE_POSITION', 'SAVE_CURRENT_POSITION', 
            'RESTORE_POSITION']
        for cmd in handlers:
            func = getattr(self, 'cmd_' + cmd)
            desc = getattr(self, 'cmd_' + cmd + '_help', None)
            self.gcode.register_command(cmd, func, False, desc)

        self.printer.register_event_handler("klippy:ready", self.Initialize_Tool_Lock)
        
    cmd_TOOL_LOCK_help = "Lock the ToolLock."
    def cmd_TOOL_LOCK(self, gcmd = None):
        self.ToolLock()

    def ToolLock(self, ignore_locked = False):
        self.gcode.respond_info("TOOL_LOCK running. ")
        if not ignore_locked and int(self.tool_current) != -1:
            self.gcode.respond_info("TOOL_LOCK is already locked with tool " + self.tool_current + ".")
        else:
            self.tool_lock_gcode_template.run_gcode_from_command()
            self.SaveCurrentTool("-2")
            self.gcode.respond_info("Locked")

    cmd_T_1_help = "Deselect all tools"
    def cmd_T_1(self, gcmd = None):
        self.gcode.respond_info("T_1 running. ")# + gcmd.get_raw_command_parameters())
        if self.tool_current == "-2":
            raise self.printer.command_error("cmd_T_1: Unknown tool already mounted Can't park unknown tool.")
        if self.tool_current != "-1":
            self.printer.lookup_object('tool ' + str(self.tool_current)).Dropoff()

    cmd_TOOL_UNLOCK_help = "Unlock the ToolLock."
    def cmd_TOOL_UNLOCK(self, gcmd = None):
        self.gcode.respond_info("TOOL_UNLOCK running. ")
        self.tool_unlock_gcode_template.run_gcode_from_command()
        self.SaveCurrentTool(-1)
        self.gcode.run_script_from_command("M117 ToolLock Unlocked.")


    def PrinterIsHomedForToolchange(self, lazy_home_when_parking =0):
        curtime = self.printer.get_reactor().monotonic()
        toolhead = self.printer.lookup_object('toolhead')
        homed = toolhead.get_status(curtime)['homed_axes'].lower()
        if all(axis in homed for axis in ['x','y','z']):
            return True
        elif lazy_home_when_parking == 0 and not all(axis in homed for axis in ['x','y','z']):
            return False
        elif lazy_home_when_parking == 1 and 'z' not in homed:
            return False

        axes_to_home = ""
        for axis in ['x', 'y', 'z']:
            if axis not in homed: 
                axes_to_home += axis
        self.gcode.run_script_from_command("G28 " + axes_to_home.upper())
        return True

    def SaveCurrentTool(self, t):
        self.tool_current = str(t)
        save_variables = self.printer.lookup_object('save_variables')
        save_variables.cmd_SAVE_VARIABLE(self.gcode.create_gcode_command(
            "SAVE_VARIABLE", "SAVE_VARIABLE", {"VARIABLE": "tool_current", 'VALUE': t}))

    cmd_SAVE_CURRENT_TOOL_help = "Save the current tool to file to load at printer startup."
    def cmd_SAVE_CURRENT_TOOL(self, gcmd):
        t = gcmd.get_int('T', None, minval=-2)
        if t is not None:
            self.SaveCurrentTool(t)

    def Initialize_Tool_Lock(self):
        if not self.init_printer_to_last_tool:
            return None

        self.gcode.respond_info("Initialize_Tool_Lock running.")
        save_variables = self.printer.lookup_object('save_variables')
        try:
            self.tool_current = save_variables.allVariables["tool_current"]
        except:
            self.tool_current = "-1"
            save_variables.cmd_SAVE_VARIABLE(self.gcode.create_gcode_command(
                "SAVE_VARIABLE", "SAVE_VARIABLE", {"VARIABLE": "tool_current", 'VALUE': self.tool_current }))

        if str(self.tool_current) == "-1":
            self.cmd_TOOL_UNLOCK()
            self.gcode.run_script_from_command("M117 ToolLock initialized unlocked")

        else:
            t = self.tool_current
            self.ToolLock(True)
            self.SaveCurrentTool(str(t))
            self.gcode.run_script_from_command("M117 ToolLock initialized with T%s." % self.tool_current) 

    cmd_SET_AND_SAVE_FAN_SPEED_help = "Save the fan speed to be recovered at ToolChange."
    def cmd_SET_AND_SAVE_FAN_SPEED(self, gcmd):
        fanspeed = gcmd.get_float('S', 1, minval=0, maxval=255)
        tool_id = gcmd.get_int('P', int(self.tool_current), minval=0)

        # The minval above doesn't seem to work.
        if tool_id < 0:
            self.gcode.respond_info("cmd_SET_AND_SAVE_FAN_SPEED: Invalid tool:"+str(tool_id))
            return None

        self.gcode.respond_info("ToolLock.cmd_SET_AND_SAVE_FAN_SPEED: Change fan speed for T%s to %f." % (str(tool_id), fanspeed))

        # If value is >1 asume it is given in 0-255 and convert to percentage.
        if fanspeed > 1:
            fanspeed=float(fanspeed / 255.0)

        self.SetAndSaveFanSpeed(tool_id, fanspeed)

    #
    # Todo: 
    # Implement Fan Scale. Inspired by https://github.com/jschuh/klipper-macros/blob/main/fans.cfg
    # Can change fan scale for diffrent materials or tools from slicer. Maybe max and min too?
    #    
    def SetAndSaveFanSpeed(self, tool_id, fanspeed):
        tool = self.printer.lookup_object("tool " + str(tool_id))

        if tool.fan is None:
            self.gcode.respond_info("ToolLock.SetAndSaveFanSpeed: Tool %s has no fan." % str(tool_id))
        else:
            self.SaveFanSpeed(fanspeed)
            self.gcode.run_script_from_command(
                "SET_FAN_SPEED FAN=%s SPEED=%f" % 
                (tool.fan, 
                fanspeed))

    cmd_TEMPERATURE_WAIT_WITH_TOLERANCE_help = "Waits for all temperatures, or a specified (TOOL) tool or (HEATER) heater's temperature within (TOLERANCE) tolerance."
#  Waits for all temperatures, or a specified tool or heater's temperature.
#  This command can be used without any additional parameters.
#  Without parameters it waits for bed and current extruder.
#  Only one of either P or H may be used.
#
#  TOOL=nnn Tool number.
#  HEATER=nnn Heater number. 0="heater_bed", 1="extruder", 2="extruder1", etc.
#  TOLERANCE=nnn Tolerance in degC. Defaults to 1*C. Wait will wait until heater is between set temperature +/- tolerance.
    def cmd_TEMPERATURE_WAIT_WITH_TOLERANCE(self, gcmd):
        curtime = self.printer.get_reactor().monotonic()
        heater_name = None
        tool_id = gcmd.get_int('TOOL', None, minval=0)
        heater_id = gcmd.get_int('HEATER', None, minval=0)
        tolerance = gcmd.get_int('TOLERANCE', 1, minval=0, maxval=50)

        if tool_id is not None and heater_id is not None:
            self.gcode.respond_info("cmd_TEMPERATURE_WAIT_WITH_TOLERANCE: Can't use both P and H parameter at the same time.")
            return None
        elif tool_id is None and heater_id is None:
            tool_id = self.tool_current
            if int(self.tool_current) >= 0:
                heater_name = self.printer.lookup_object("tool " + self.tool_current).get_status()["extruder"]
            #wait for bed
            self._Temperature_wait_with_tolerance(curtime, "heater_bed", tolerance)

        else:                                               # Only heater or tool is specified
            if tool_id is not None:
                heater_name = self.printer.lookup_object(   # Set the heater_name to the extruder of the tool.
                    "tool " + str(tool_id)).get_status(curtime)["extruder"]
            elif heater_id == 0:                            # Else If 0, then heater_bed.
                heater_name = "heater_bed"                      # Set heater_name to "heater_bed".

            elif heater_id == 1:                            # Else If h is 1 then use for first extruder.
                heater_name = "extruder"                        # Set heater_name to first extruder which has no number.
            else:                                           # Else is another heater number.
                heater_name = "extruder" + str(heater_id - 1)   # Because bed is heater_number 0 extruders will be numbered one less than H parameter.
        if heater_name is not None:
            self._Temperature_wait_with_tolerance(curtime, heater_name, tolerance)


    def _Temperature_wait_with_tolerance(self, curtime, heater_name, tolerance):
        target_temp = int(self.printer.lookup_object(       # Get the heaters target temperature.
                    heater_name).get_status(curtime)["target"]
                          )
        
        if target_temp > 40:                                # Only wait if set temperature is over 40*C
            self.gcode.respond_info("Wait for heater " + heater_name + " to reach " + str(target_temp) + " with a tolerance of " + str(tolerance) + ".")
            self.gcode.run_script_from_command(
                "TEMPERATURE_WAIT SENSOR=" + heater_name + 
                " MINIMUM=" + str(target_temp - tolerance) + 
                " MAXIMUM=" + str(target_temp + tolerance) )
            self.gcode.respond_info("Wait for heater " + heater_name + " complete.")
        #else:
        #    self.gcode.respond_info("Not waiting for heater " + heater_name + " to reach " + str(target_temp) + " with a tolerance of " + str(tolerance) + ".")


    cmd_SET_TOOL_TEMPERATURE_help = "Waits for all temperatures, or a specified (TOOL) tool or (HEATER) heater's temperature within (TOLERANCE) tolerance."
#  Set tool temperature.
#  TOOL= Tool number, optional. If this parameter is not provided, the current tool is used.
#  STDB_TMP= Standby temperature(s), optional
#  ACTV_TMP= Active temperature(s), optional
#  CHNG_STATE = Change Heater State, optional: 0 = off, 1 = standby temperature(s), 2 = active temperature(s).
#  STDB_TIMEOUT = Time in seconds to wait between changing heater state to standby and setting heater target temperature to standby temperature when standby temperature is lower than tool temperature.
#      Use for example 0.1 to change immediately to standby temperature.
#  SHTDWN_TIMEOUT = Time in seconds to wait from docking tool to shutting off the heater, optional.
#      Use for example 86400 to wait 24h if you want to disable shutdown timer.
    def cmd_SET_TOOL_TEMPERATURE(self, gcmd):
        curtime = self.printer.get_reactor().monotonic()
        tool_id = gcmd.get_int('TOOL', self.tool_current, minval=0)
        stdb_tmp = gcmd.get_int('STDB_TMP', None, minval=0)
        actv_tmp = gcmd.get_int('ACTV_TMP', None, minval=0)
        chng_state = gcmd.get_int('CHNG_STATE', None, minval=0, maxval=2)
        stdb_timeout = gcmd.get_float('STDB_TIMEOUT', None, minval=0)
        shtdwn_timeout = gcmd.get_float('SHTDWN_TIMEOUT', None, minval=0)

        if tool_id < 0:
            self.gcode.respond_info("cmd_SET_TOOL_TEMPERATURE: Tool " + str(tool_id) + " is not valid.")
            return None

        if self.printer.lookup_object("tool " + str(tool_id)).get_status()["extruder"] is None:
            self.gcode.respond_info("cmd_SET_TOOL_TEMPERATURE: T%s has no extruder! Nothing to do." % str(tool_id) )
            return None

        tool = self.printer.lookup_object("tool " + str(tool_id))
        set_heater_cmd = {}

        if stdb_tmp is not None:
            set_heater_cmd["heater_standby_temp"] = stdb_tmp
        if actv_tmp is not None:
            set_heater_cmd["heater_active_temp"] = actv_tmp
        if stdb_timeout is not None:
            set_heater_cmd["heater_standby_temp"] = stdb_timeout
        if shtdwn_timeout is not None:
            set_heater_cmd["idle_to_powerdown_time"] = shtdwn_timeout
        if chng_state is not None:
            tool.set_heater(heater_state= chng_state)
        if len(set_heater_cmd) > 0:
            tool.set_heater(**set_heater_cmd)

    cmd_SET_TOOL_OFFSET_help = "Set an individual tool offset"
    def cmd_SET_TOOL_OFFSET(self, gcmd):
        tool_id = gcmd.get_int('TOOL', self.tool_current, minval=0)
        x_pos = gcmd.get_float('X', None)
        x_adjust = gcmd.get_float('X_ADJUST', None)
        y_pos = gcmd.get_float('Y', None)
        y_adjust = gcmd.get_float('Y_ADJUST', None)
        z_pos = gcmd.get_float('Z', None)
        z_adjust = gcmd.get_float('Z_ADJUST', None)

        if tool_id < 0:
            self.gcode.respond_info("cmd_SET_TOOL_TEMPERATURE: Tool " + str(tool_id) + " is not valid.")
            return None

        tool = self.printer.lookup_object("tool " + str(tool_id))
        set_offset_cmd = {}

        if x_pos is not None:
            set_offset_cmd["x_pos"] = x_pos
        elif x_adjust is not None:
            set_offset_cmd["x_adjust"] = x_adjust
        if y_pos is not None:
            set_offset_cmd["y_pos"] = y_pos
        elif y_adjust is not None:
            set_offset_cmd["y_adjust"] = y_adjust
        if z_pos is not None:
            set_offset_cmd["z_pos"] = z_pos
        elif z_adjust is not None:
            set_offset_cmd["z_adjust"] = z_adjust
        if len(set_offset_cmd) > 0:
            tool.set_offset(**set_offset_cmd)

    cmd_SET_GLOBAL_OFFSET_help = "Set the global tool offset"
    def cmd_SET_GLOBAL_OFFSET(self, gcmd):
        x_pos = gcmd.get_float('X', None)
        x_adjust = gcmd.get_float('X_ADJUST', None)
        y_pos = gcmd.get_float('Y', None)
        y_adjust = gcmd.get_float('Y_ADJUST', None)
        z_pos = gcmd.get_float('Z', None)
        z_adjust = gcmd.get_float('Z_ADJUST', None)

        if x_pos is not None:
            self.global_offset[0] = float(x_pos)
        elif x_adjust is not None:
            self.global_offset[0] = float(self.global_offset[0]) + float(x_adjust)
        if y_pos is not None:
            self.global_offset[1] = float(y_pos)
        elif y_adjust is not None:
            self.global_offset[1] = float(self.global_offset[1]) + float(y_adjust)
        if z_pos is not None:
            self.global_offset[2] = float(z_pos)
        elif z_adjust is not None:
            self.global_offset[2] = float(self.global_offset[2]) + float(z_adjust)

        self.gcode.respond_info("Global offset now set to: %f, %f, %f." % (float(self.global_offset[0]), float(self.global_offset[1]), float(self.global_offset[2])))

    cmd_SET_PURGE_ON_TOOLCHANGE_help = "Set the global variable if the tool should be purged or primed with filament at toolchange."
    def cmd_SET_PURGE_ON_TOOLCHANGE(self, gcmd = None):
        param = gcmd.get('VALUE', 'FALSE')

        if param.upper() == 'FALSE' or param == '0':
            self.purge_on_toolchange = False
        else:
            self.purge_on_toolchange = True

    def SaveFanSpeed(self, fanspeed):
        self.saved_fan_speed = float(fanspeed)
       
    cmd_SAVE_POSITION_help = "Save the specified G-Code position."
    def cmd_SAVE_POSITION(self, gcmd):
        param_X = gcmd.get_float('X', None)
        param_Y = gcmd.get_float('Y', None)
        param_Z = gcmd.get_float('Z', None)
        
        if param_X is None or param_Y is None:
            self.restore_position_on_toolchange = 0
            return
        elif param_Z is None:
            self.restore_position_on_toolchange = 1
        else:
            self.restore_position_on_toolchange = 2

        self.saved_position = [param_X, param_Y, param_Z]


    cmd_SAVE_CURRENT_POSITION_help = "Save the current G-Code position."
    def cmd_SAVE_CURRENT_POSITION(self, gcmd):
        self.SaveCurrentPosition()

    def SaveCurrentPosition(self):
        gcode_move = self.printer.lookup_object('gcode_move')
        self.saved_position = gcode_move._get_gcode_position()

    cmd_RESTORE_POSITION_help = "Restore a previously saved G-Code position if it was specified in the toolchange T# command."
    def cmd_RESTORE_POSITION(self, gcmd):
        self.gcode.respond_info("cmd_RESTORE_POSITION running: " + str(self.restore_position_on_toolchange))

        param = gcmd.get_int('RESTORE_POSITION', None, minval=0, maxval=2)

        if param is not None:
            if param == 0 or param == 1 or param == 2:
                self.restore_position_on_toolchange = param

        if self.restore_position_on_toolchange == 0:
            return

        if self.saved_position is None:
            raise gcmd.error("No saved g-code position.")

        try:
            p = self.saved_position
            if self.restore_position_on_toolchange == 1:
                v=str("G1 X%.3f Y%.3f" % (p[0], p[1]))
            elif self.restore_position_on_toolchange == 2:
                v=str("G1 X%.3f Y%.3f Z%.3f" % (p[0], p[1], p[2]))
            # Restore position
            self.gcode.respond_info("cmd_RESTORE_POSITION running: " + v)
            self.gcode.run_script_from_command(v)
        except:
            raise gcmd.error("Could not restore position.")


    def get_status(self, eventtime= None):
        status = {
            "global_offset": self.global_offset,
            "tool_current": self.tool_current,
            "saved_fan_speed": self.saved_fan_speed,
            "purge_on_toolchange": self.purge_on_toolchange,
            "restore_position_on_toolchange": self.restore_position_on_toolchange,
            "saved_position": self.saved_position
        }
        return status

def load_config(config):
    return ToolLock(config)
