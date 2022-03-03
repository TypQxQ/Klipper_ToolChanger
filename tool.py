# Tool support
#
# Copyright (C) 2022  Andrei Ignat <andrei@ignat.se>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

class Tool:
    def __init__(self, config = None):
        # If called without config then createa a dummy object.
        if config is None:
            self.name = None
            self.is_virtual = None
            self.physical_parent_id = None
            self.extruder = None
            self.fan = None
            self.meltzonelength = 0
            self.lazy_home_when_parking = None
            self.zone = None
            self.park = None
            self.offset = None
            self.pickup_gcode = None
            self.dropoff_gcode = None
            self.heater_state = None
            self.heater_active_temp = None
            self.heater_standby_temp = None
            self.placeholder_standby_temp = None
            self.idle_to_standby_time = None
            self.idle_to_powerdown_time = None
            return None

        # And from here we create the real object.
        self.printer = config.get_printer()
        self.gcode = config.get_printer().lookup_object('gcode')
        gcode_macro = self.printer.load_object(config, 'gcode_macro')
        self.toollock = self.printer.lookup_object('toollock')

        self.name = config.get_name().split()[-1]

        if not unicode(self.name, 'utf-8').isnumeric():
            raise config.error(
                    "Name of section '%s' contains illegal characters. Use only integer tool number."
                    % (config.get_name()))
        else:
            self.name = int(self.name)

        # ToolType, defaults to 0. Check if tooltype is defined.
        self.toolgroup = 'toolgroup ' + str(config.getint('tool_group'))
        if config.has_section(self.toolgroup):
            self.toolgroup = self.printer.lookup_object(self.toolgroup)
        else:
            raise config.error(
                    "Tooltype of '%s' is not defined. It must be configured before the tool."
                    % (config.get_name()))

        self.is_virtual = config.getboolean('is_virtual', 
                                            self.toolgroup.get_status()["is_virtual"])

        # Parent tool is used as a Physical parent for all tools of this group. Only used if the tool i virtual.
        self.physical_parent_id = config.getint('physical_parent', 
                                                self.toolgroup.get_status()["physical_parent_id"])

        if self.physical_parent_id is None:
            self.physical_parent_id = -1

        # Used as sanity check for tools that are virtual with same physical as themselves.
        if self.is_virtual and self.physical_parent_id == -1:
            raise config.error(
                    "Section Tool '%s' cannot be virtual without a valid physical_parent."
                    % (config.get_name()))

        
        if int(self.physical_parent_id) == int(self.name):
            self.physical_parent_id = -1;

        if self.physical_parent_id >= 0:
            pp = self.printer.lookup_object("tool " + str(self.physical_parent_id))
        else:
            pp = Tool()     # Initialize physical parent as a dummy object.

        pp_status = pp.get_status()

        self.extruder = config.get('extruder', pp_status['extruder'])      # Name of extruder connected to this tool. Defaults to None.
        self.fan = config.get('fan', pp_status['fan'])                     # Name of general fan configuration connected to this tool as a part fan. Defaults to "none".
        self.meltzonelength = config.get('meltzonelength', 
                                         pp_status['meltzonelength'])      # Length of the meltzone for retracting and inserting filament on toolchange. 18mm for e3d Revo


        self.lazy_home_when_parking = config.get('lazy_home_when_parking', pp_status['lazy_home_when_parking'])   # -1 = none, 1= Only load filament, 2= Wipe in front of carriage, 3= Pebble wiper, 4= First Silicone, then pebble. Defaults to None.
        if self.lazy_home_when_parking is None:
            self.lazy_home_when_parking = self.toolgroup.get_status()["lazy_home_when_parking"]      # Toolgroup initializes as -1 while all other as None.

        self.zone = config.get('zone', pp_status['zone'])                  # Name of general fan configuration connected to this tool as a part fan. Defaults to "none".
        self.park = config.get('park', pp_status['park'])                  # Name of general fan configuration connected to this tool as a part fan. Defaults to "none".
        self.offset = config.get('offset', pp_status['offset'])            # Name of general fan configuration connected to this tool as a part fan. Defaults to "none".

        if self.zone is None or self.park is None or self.offset is None:
            raise config.error(
                    "Section Tool '%s' misses requred parameter."
                    % (config.get_name()))

        self.heater_state = 0                   # 0 = off, 1 = standby temperature, 2 = active temperature. Placeholder. Requred on Physical tool.
        self.heater_active_temp = 0             # Temperature to set when in active mode. Placeholder. Requred on Physical and virtual tool if any has extruder.
        self.heater_standby_temp = 0            # Temperature to set when in standby mode.  Placeholder. Requred on Physical and virtual tool if any has extruder.
        self.placeholder_standby_temp = 0       # Required placeholder if this tool has virtual tools. Holds last used standby temp of physical heater.

        self.idle_to_standby_time = config.get(
            'idle_to_standby_time', 30)                                     # Time in seconds from being parked to setting temperature to standby the temperature above. Use 0.1 to change imediatley to standby temperature. Requred on Physical tool
        self.idle_to_powerdown_time = config.get(
            'idle_to_powerdown_time', 600)                                  # Time in seconds from being parked to setting temperature to 0. Use something like 86400 to wait 24h if you want to disable. Requred on Physical tool.
        

        # The plain gcode string is to load for virtual tool having this tool as parent.
        self.pickup_gcode = config.get('pickup_gcode', None)
        self.dropoff_gcode = config.get('dropoff_gcode', None)


        # Get the pickup_gcode parameter from the parent and if none then from the toolgroup. If none is defined in parent and toolgroup then it returns empty.
        temp_pickup_gcode = pp.get_pickup_gcode()
        if temp_pickup_gcode is None:
            temp_pickup_gcode =  self.toolgroup.get_pickup_gcode()
        # Get the pickup_gcode parameter the tool and use the one from the toolgroup as default.
        self.pickup_gcode_template = gcode_macro.load_template(config, 'pickup_gcode', temp_pickup_gcode)

        temp_dropoff_gcode = pp.get_dropoff_gcode()
        if temp_dropoff_gcode is None:
            temp_dropoff_gcode = self.toolgroup.get_dropoff_gcode()
        self.dropoff_gcode_template = gcode_macro.load_template(config, 'dropoff_gcode', temp_dropoff_gcode)

        self.timer_idle_to_standby = ToolStandbyTempTimer(self.printer, self.name, 1)
        self.timer_idle_to_powerdown_time = ToolStandbyTempTimer(self.printer, self.name, 0)

        # Register commands
        self.gcode.register_command("T" + str(self.name), self.cmd_SelectTool, desc=self.cmd_SelectTool_help)


    cmd_SelectTool_help = "Select Tool"
    def cmd_SelectTool(self, gcmd):
        current_tool_id = int(self.toollock.get_tool_current())

        self.gcode.respond_info("T" + str(self.name) + " Selected.")
        self.gcode.respond_info("Current Tool is T" + str(current_tool_id) + ".")
        self.gcode.respond_info("This tool is_virtual is " + str(self.is_virtual) + ".")


        if current_tool_id == self.name:              # If trying to select the already selected tool:
            return None                                   # Exit

        if current_tool_id < -1:
            raise self.printer.command_error("TOOL_PICKUP: Unknown tool already mounted Can't park it before selecting new tool.")

        if self.extruder is not None:               # If the new tool to be selected has an extruder.
#            self.gcode.run_script_from_command("M568 P%d A2" % int(self.name))
            pass

        if current_tool_id >= 0:                    # If there is a current tool already selected and it's a dropable.
            current_tool = self.printer.lookup_object('tool ' + str(current_tool_id))
                                                        # If the next tool is not another virtual tool on the same physical tool.
            
            self.gcode.respond_info("self.physical_parent_id:" + str(self.physical_parent_id) + ".")
            self.gcode.respond_info("current_tool.get_status()['physical_parent_id']:" + str(current_tool.get_status()["physical_parent_id"]) + ".")

            if int(self.physical_parent_id ==  -1 or
                        self.physical_parent_id) !=  int( 
                        current_tool.get_status()["physical_parent_id"]
                        ):
                self.gcode.respond_info("Will Dropoff():")
                current_tool.Dropoff()
                current_tool_id = -1

        # Now we asume tool has been deselected if needed be.

        if not self.is_virtual:
            self.gcode.respond_info("cmd_SelectTool: T" + str(self.name) + "- Not Virtual - Pickup")
            self.Pickup()
            #    SUB_TOOL_PICKUP_START {rawparams}                                    # Start Pickup tool
            #    SUB_TOOL_PICKUP_WIPE {rawparams}                                     # Wipe tool
            #    SUB_TOOL_PICKUP_END {rawparams}                                      # End Pickup tool code
            #    SUB_TOOL_PICKUP_DEPRESURIZE_HOTEND                                   # Depresurize tool
        else:
            if current_tool_id >= 0:                 # If still has a selected tool: (This tool is a virtual tool with same physical tool as the last)
                current_tool = self.printer.lookup_object('tool ' + str(current_tool_id))
                self.gcode.respond_info("cmd_SelectTool: T" + str(self.name) + "- Virtual - Tool is not Dropped - ")
                if self.physical_parent_id >= 0 and self.physical_parent_id == current_tool.get_status()["physical_parent_id"]:
                    self.gcode.respond_info("cmd_SelectTool: T" + str(self.name) + "- Virtual - Same physical tool - Pickup")
                    current_tool.UnloadVirtual()
                    self.LoadVirtual()
                    return ""
                else:
                    self.gcode.respond_info("cmd_SelectTool: T" + str(self.name) + "- Virtual - Not Same physical tool")
                    # Shouldn't reach this?
                    #self.Pickup()
                    #          SUB_TOOL_PICKUP_START T={tool_id}                                        # Pickup the physical tool for the virtual ERCF tool.
                    #                                                                             # Run ERCF code
                    #          RESPOND MSG="ERCF not implemented yet. Changing to ERCF with diffrent physical tool. From {current_tool_id} to {tool_id} with physical tool {tool.ercf_physical_tool|string}."
                    #          SUB_TOOL_PICKUP_WIPE {rawparams}                                   # Wipe tool
                    #          SUB_TOOL_PICKUP_END {rawparams}                                    # End Pickup tool code
                    #          SUB_TOOL_PICKUP_DEPRESURIZE_HOTEND                                 # Depresurize tool
            else:
                self.gcode.respond_info("cmd_SelectTool: T" + str(self.name) + "- Virtual - Tool is droped")
                self.Pickup()
                      #        SUB_TOOL_PICKUP_START T={tool_id}                                        # Pickup the physical tool for the virtual ERCF tool.
                      #                                                                           # Run ERCF code
                      #        RESPOND MSG="ERCF not implemented yet. Changing to ERCF with diffrent physical tool. From {current_tool_id} to {tool_id} with physical tool {tool.ercf_physical_tool|string}."
                      #        SUB_TOOL_PICKUP_WIPE {rawparams}                                   # Wipe tool
                      #        SUB_TOOL_PICKUP_END {rawparams}                                    # End Pickup tool code
                      #        SUB_TOOL_PICKUP_DEPRESURIZE_HOTEND                                 # Depresurize tool

        self.gcode.run_script_from_command("M117 T%d Loaded" % int(self.name))
        self.toollock.SaveCurrentTool(self.name)

    def Pickup(self):
        # Check if homed
        if not self.toollock.PrinterIsHomedForToolchange():
            raise self.printer.command_error("Tool.Pickup: Printer not homed and Lazy homing option is: " + self.lazy_home_when_parking)
            return None

        # If has an extruder then activate that extruder.
        if self.extruder is not None:
            self.gcode.run_script_from_command(
                "ACTIVATE_EXTRUDER extruder=%s" % 
                self.extruder)

        # Run the gcode for pickup.
        try:
            context = self.pickup_gcode_template.create_template_context()
            context['myself'] = self.get_status()
            self.pickup_gcode_template.run_gcode_from_command(context)
        except Exception:
            logging.exception("Pickup gcode: Script running error")

        # Restore fan if has a fan.
        if self.fan is not None:
            self.gcode.run_script_from_command(
                "SET_FAN_SPEED FAN=" + self.fan + " SPEED=" + str(self.toollock.get_saved_fan_speed()) )

        self.toollock.SaveCurrentTool(self.name)
        self.gcode.run_script_from_command("M117 T%d picked up." % self.name)



    def Dropoff(self):
        # Check if homed
        if not self.toollock.PrinterIsHomedForToolchange():
            self.gcode.respond_info("Tool.Dropoff: Printer not homed and Lazy homing option is: " + self.lazy_home_when_parking)
            return None

        # Save fan if has a fan. Is not actually needed as it is run with every M106 command
        #if self.fan is not None:
        #    fanspeed = self.printer.lookup_object('fan_generic extruder_partfan').get_status(eventtime)["speed"]
        #    self.toollock.SaveFanSpeed(fanspeed)
        #    self.gcode.run_script_from_command(
        #        "SET_FAN_SPEED FAN=%s SPEED=0" % 
        #        self.fan)
        # Run the gcode for dropoff.
        try:
            context = self.dropoff_gcode_template.create_template_context()
            context['myself'] = self.get_status()
            self.dropoff_gcode_template.run_gcode_from_command(context)
        except Exception:
            logging.exception("Dropoff gcode: Script running error")

        self.toollock.SaveCurrentTool(-1)   # Dropoff successfull

    def LoadVirtual(self):
        self.gcode.respond_info("LoadVirtual: Virtual tools not implemented yet. T%d." % self.name )
        self.toollock.SaveCurrentTool(self.name)

    def UnloadVirtual(self):
        self.gcode.respond_info("UnloadVirtual: Virtual tools not implemented yet. T%d." % self.name )

    def set_heater(self, **kwargs):
        heater = self.printer.lookup_object(self.extruder).get_heater()

        for i in kwargs:
            if i == "heater_active_temp":
                self.heater_active_temp = kwargs[i]
                if int(self.heater_state) == 2:
                    heater.set_temp(self.heater_active_temp)
            elif i == "heater_standby_temp":
                self.heater_standby_temp = kwargs[i]
            elif i == "idle_to_standby_time":
                self.idle_to_standby_time = kwargs[i]
            elif i == "idle_to_powerdown_time":
                self.idle_to_powerdown_time = kwargs[i]
            elif i == "heater_state":
                self.heater_state = kwargs[i]

        # Change Active mode:
        if "heater_state" in kwargs:
            chng_state = kwargs["heater_state"]
            if chng_state == 0:                                                                         # If Change to Shutdown
                self.timer_idle_to_standby.set_timer(0)
                self.timer_idle_to_powerdown_time.set_timer(0.1)
                #self._set_Tool_Standby_Timers(0, 0.1)                                            # Disable standy temperature and run shutdown timer.
            elif chng_state == 2:
                #self._set_Tool_Standby_Timers(0, 0)                                            # Disable standy temperature and standby to shutdown timer.
                self.timer_idle_to_standby.set_timer(0)
                self.timer_idle_to_powerdown_time.set_timer(0)
                heater.set_temp(self.heater_active_temp)
            elif chng_state == 1:                                                                       # Else If Standby
                curtime = self.printer.get_reactor().monotonic()
                if int(self.heater_state) == 1 or int(self.heater_standby_temp) > int(heater.get_status(curtime)["temperature"]):
                    self.timer_idle_to_standby.set_timer(0,1)
                    self.timer_idle_to_powerdown_time.set_timer(self.idle_to_powerdown_time)
                    #self._set_Tool_Standby_Timers(0.1, self.idle_to_powerdown_time)                                  # Run standby timer and start shutdown timer.
                else:                                                                                   # Else (Standby temperature is lower than the current temperature)
                    self.timer_idle_to_standby.set_timer(self.idle_to_standby_time)
                    self.timer_idle_to_powerdown_time.set_timer(self.idle_to_powerdown_time)
                    #self._set_Tool_Standby_Timers(self.idle_to_standby_time, self.idle_to_powerdown_time)       # Start the standby and shutdown temperature timers.

    #def _set_Tool_Standby_Timers(self, stdb_timeout, shtdwn_timeout):
    #    self.timer_idle_to_standby.set_timer(stdb_timeout)
    #    self.timer_idle_to_powerdown_time.set_timer(shtdwn_timeout)
        #self.gcode.run_script_from_command(                                                         # Start the standby and shutdown temperature timers.
        #            "UPDATE_DELAYED_GCODE ID=T" + str(self.name) + 
        #            "_standby DURATION=" + str(stdb_timeout))

        #self.gcode.run_script_from_command(                                                         # Start the standby and shutdown temperature timers.
        #            "UPDATE_DELAYED_GCODE ID=T" + str(self.name) + 
        #            "_powerdown DURATION=" + str(shtdwn_timeout))


    def get_pickup_gcode(self):
        return self.pickup_gcode

    def get_dropoff_gcode(self):
        return self.dropoff_gcode


    def get_status(self, eventtime= None):
        status = {
            "name": self.name,
            "is_virtual": self.is_virtual,
            "physical_parent_id": self.physical_parent_id,
            "extruder": self.extruder,
            "fan": self.fan,
            "lazy_home_when_parking": self.lazy_home_when_parking,
            "meltzonelength": self.meltzonelength,
            "zone": str(self.zone).split(','),
            "park": str(self.park).split(','),
            "offset": str(self.offset).split(','),
            "heater_state": self.heater_state,
            "heater_active_temp": self.heater_active_temp,
            "heater_standby_temp": self.heater_standby_temp,
            "placeholder_standby_temp": self.placeholder_standby_temp,
            "idle_to_standby_time": self.idle_to_standby_time,
            "idle_to_powerdown_time": self.idle_to_powerdown_time
        }
        return status

    # Based on DelayedGcode.
class ToolStandbyTempTimer:
    def __init__(self, printer, tool_id, temp_type):
        self.printer = printer
        self.tool_id = tool_id
        self.duration = 0.
        self.temp_type = temp_type      # 0= Time to shutdown, 1= Time to standby.

        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        self.timer_handler = None
        self.inside_timer = self.repeat = False
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
    def _handle_ready(self):
        self.timer_handler = self.reactor.register_timer(
            self._standby_tool_temp_timer_event, self.reactor.NEVER)
    def _standby_tool_temp_timer_event(self, eventtime):
        self.inside_timer = True
        try:
            tool = self.printer.lookup_object(tool_id)
            temperature = 0
            if self.temp_type == 1:
                temperature = tool.get_status()["heater_standby_temp"]
            heater = self.printer.lookup_object(self.tool.extruder).get_heater()
            heater.set_temp(temperature)
        except Exception:
            logging.exception("Failed to set Standby temp for tool T" + self.tool_id + ".")
        nextwake = self.reactor.NEVER
        if self.repeat:
            nextwake = eventtime + self.duration
        self.inside_timer = self.repeat = False
        return nextwake
    def set_timer(self, duration):
        self.duration = float(duration)
        if self.inside_timer:
            self.repeat = (self.duration != 0.)
        else:
            waketime = self.reactor.NEVER
            if self.duration:
                waketime = self.reactor.monotonic() + self.duration
            self.reactor.update_timer(self.timer_handler, waketime)
    def get_status(self, eventtime= None):
        status = {
            "tool": self.tool,
            "temp_type": self.temp_type,
            "duration": self.duration
        }
        return status

    # Todo: 
    # Inspired by https://github.com/jschuh/klipper-macros/blob/main/layers.cfg
class MeanLayerTime:
    def __init__(self, printer):
        # Run before toolchange to set time like in StandbyToolTimer.
        # Save time for last 5 (except for first) layers
        # Provide a mean layer time.
        # Have Tool have a min and max 2standby time.
        # If mean time for 3 layers is higher than max, then set min time.
        # Reset time if layer time is higher than max time. Pause or anything else that has happened.
        # Function to reset layer times.
        pass


def load_config_prefix(config):
    return Tool(config)
