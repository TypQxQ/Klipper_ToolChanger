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

        self.saved_fan_speed = 0          # Saved partcooling fan speed when deselecting a tool with a fan.
        self.tool_current = "-2"          # -2 Unknown tool locked, -1 No tool locked, 0 and up are tools.
        self.init_printer_to_last_tool = config.getboolean(
            'init_printer_to_last_tool', True)
        self.purge_on_toolchange = config.getboolean(
            'purge_on_toolchange', True)

        # G-Code macros
        self.tool_lock_gcode_template = gcode_macro.load_template(config, 'tool_lock_gcode', '')
        self.tool_unlock_gcode_template = gcode_macro.load_template(config, 'tool_unlock_gcode', '')

        # Register commands
        self.gcode.register_command("SAVE_CURRENT_TOOL", self.cmd_SAVE_CURRENT_TOOL, desc=self.cmd_SAVE_CURRENT_TOOL_help)
        self.gcode.register_command("TOOL_LOCK", self.cmd_TOOL_LOCK, desc=self.cmd_TOOL_LOCK_help)
        self.gcode.register_command("TOOL_UNLOCK", self.cmd_TOOL_UNLOCK, desc=self.cmd_TOOL_UNLOCK_help)
        self.gcode.register_command("T_1", self.cmd_T_1, desc=self.cmd_T_1_help)
        self.gcode.register_command("SET_AND_SAVE_FAN_SPEED", self.cmd_SET_AND_SAVE_FAN_SPEED, desc=self.cmd_SET_AND_SAVE_FAN_SPEED_help)
        self.gcode.register_command("TEMPERATURE_WAIT_WITH_TOLERANCE", self.cmd_TEMPERATURE_WAIT_WITH_TOLERANCE, desc=self.cmd_TEMPERATURE_WAIT_WITH_TOLERANCE_help)
        self.gcode.register_command("SET_TOOL_TEMPERATURE", self.cmd_SET_TOOL_TEMPERATURE, desc=self.cmd_SET_TOOL_TEMPERATURE_help)

        self.gcode.register_mux_command("TEST_PY", "EXTRUDER", None,
                                    self.cmd_test_py)
        
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
            self.SaveCurrentTool(-2)
            self.gcode.respond_info("Locked")



    cmd_T_1_help = "Deselect all tools"
    def cmd_T_1(self, gcmd = None):
        self.gcode.respond_info("T_1 running. ")# + gcmd.get_raw_command_parameters())
        if self.tool_current == "-2":
            raise self.printer.command_error("cmd_T_1: Unknown tool already mounted Can't park unknown tool.")
        if self.tool_current != "-1":
            self.printer.lookup_object('tool ' + self.tool_current).Dropoff()

    cmd_TOOL_UNLOCK_help = "Save the current tool to file to load at printer startup."
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
            self.tool_current = t
            self.gcode.run_script_from_command("M117 ToolLock initialized with T%s." % self.tool_current) 


    cmd_SET_AND_SAVE_FAN_SPEED_help = "Save the fan speed to be recovered at ToolChange."
    def cmd_SET_AND_SAVE_FAN_SPEED(self, gcmd):
        fanspeed = gcmd.get_float('S', 1, minval=0, maxval=255)
        tool_id = gcmd.get_int('P', int(self.tool_current), minval=0)

        # If value is >1 asume it is given in 0-255 and convert to percentage.
        if fanspeed > 1:
            fanspeed=fanspeed / 255.0

        self.SetAndSaveFanSpeed(tool_id, fanspeed)

    #
    # Todo: 
    # Implement Fan Scale. Inspired by https://github.com/jschuh/klipper-macros/blob/main/fans.cfg
    # Can change fan scale for diffrent materials or tools from slicer. Maybe max and min too?
    #    
    def SetAndSaveFanSpeed(self, tool_id, fanspeed):
        self.gcode.respond_info("ToolLock.SetAndSaveFanSpeed: Change fan speed for T%d to %d." % (tool_id, fanspeed))
        tool = self.printer.lookup_object("tool " + str(tool_id))

        if tool.fan is none:
            self.gcode.respond_info("ToolLock.SetAndSaveFanSpeed: Tool %d has no fan." % tool_id)
        else:
            SaveFanSpeed(fanspeed)
            self.gcode.run_script_from_command(
                "SET_FAN_SPEED FAN=%s SPEED=%d" % 
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
                "MAXIMUM=" + str(target_temp + tolerance) )
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
            self.gcode.respond_info("cmd_SET_TOOL_TEMPERATURE: T%d has no extruder! Nothing to do." % tool_id )
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


    def cmd_test_py(self, gcmd):
        curtime = self.printer.get_reactor().monotonic()
        toolhead = self.printer.lookup_object('toolhead')
        homed = toolhead.get_status(curtime)['homed_axes']
        gcmd.respond_info("homed:" + str(homed))
        
    def SaveFanSpeed(self, fanspeed):
        self.saved_fan_speed = float(fanspeed)
       
    def get_tool_current(self):
        return self.tool_current

    def get_saved_fan_speed(self):
        return self.saved_fan_speed

    def get_purge_on_toolchange(self):
        return self.purge_on_toolchange

    def get_status(self, eventtime= None):
        status = {
            "tool_current": self.tool_current,
            "saved_fan_speed": self.saved_fan_speed,
            "purge_on_toolchange": self.purge_on_toolchange 
        }
        return status

def load_config(config):
    return ToolLock(config)