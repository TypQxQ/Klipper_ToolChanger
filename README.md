# Tools for klipper (KTCC - Klipper Tool Changer Code)

This are python extras, macros and example config for the
[Klipper 3D printer firmware](https://github.com/Klipper3d/klipper). I
originally created this as macros when converting my Jubilee based
toolchanger from RRF and Duet3 to Klipper.

I welcome all contribution!

This is working great but treat it as a Beta version in development.

## Features

* **Each Tool is treated as an object and has it's own configuration** -
having configurable coordinates for parking, zoning, tool offset, 
meltzonelength, extruder, fan, etc.
*  **Multiple tools can be grouped in ToolGroup.** -Most configuration can
be inherited from the group if not specified in the tool config section.
*  **Virtual tools** - A tool can be virtual and have a physical parent,
inheriting all nonspecified configuration from parent, parent group and
then toolgroup. Use case example of an ERCF on a PLA tool,a ERCF on a 
PETG tool, one tool without virtual tools for abrasive and yet another
tool with 3 markers that can switch between 3 markers by rotation.
* **Tools don't need to be extruders/hotends**, can be anything.
* **User defineable macro to Lock / Unlock** - Uses custom gcodes in config 
like the gcode_button. This can call a macro or multiple lines. 
* **User defineable macro to Pickup / Dropoff tools** - Can be inherited.
In the macro, `myself` refers to the calling toolobject so you can get 
myself.id for tool number or myself.offset[0] for X offset in the macro.
Ex. having same pickup gcode macro inherited for all tools from a group 
except for one that uses another type of toolwipe and has it's own pickup_gcode.
* **Global ToolLock parameters** - example purge_on_toolchange can be set 
to false when aligning tools with TAMV/ZTATP.
* **Fan speed** is carried over on toolchange if the tool has a fan. Also
`M106`/`M107` defaults to current_tool to set fan speed but can also use a Pnnn 
parameter to specify another tool.
* **Extruder temperature control** - 
  - Definable for any tool with a Pnnn parameter or defaults to current_tool
  - Has diffrent Active and Standby temperatures.
  - Can be set in Active, Standby or Off mode.
  - Can have delayed Standby and Off. Configured and/or customized with N and O parameters at runtime.
    - Example. Set Standby temperature 30 sec after putting the tool in standby and in Off after 30 minutes of not being activated.
    - Or set Time to standby to 0.1 for instant standby and Time to Powerdown to 604800 for a having it powered for a week.
    - Usefull when having sporadic toolchanges in a large print or many toolchanges in a small print.
  - Wait to reach temperature with tolerance. Set temperature +/- configurable tolerance.
* Current Tool is saved and restored at powerdown. Default but optional.
* Input shaper parameters for each tool.
* Position prior to toolchange can optionaly be saved and restored.
* Logging including to file functionality. You can keep the console log to a minimum and send debugging information to `ktcc.log` located in the same directory as Klipper logs.
* Logging including to file functionality. You can keep the console log to a minimum and send debugging information to `ktcc.log` located in the same directory as Klipper logs.
# Statistics per print and persistent that look like this:
```
ToolChanger Statistics:
KTCC Statistics:
7 hours 52 minutes 36 seconds spent mounting tools
6 hours 42 minutes 46 seconds spent unmounting tools
30 tool locks completed
37 tool unlocks completed
462 tool mounts completed
461 tool dropoffs completed
------------
Tool#0:
Completed 220 out of 221 mounts in 3 hours 43 minutes 21 seconds. Average of 1 minutes 0 seconds per toolmount.
Completed 219 out of 220 unmounts in 3 hours 12 minutes 33 seconds. Average of 52 seconds per toolunmount.
1 hours 4 minutes 16 seconds spent selected. 23 hours 7 minutes 14 seconds with active heater and 49 minutes 44 seconds with standby heater.
------------
Tool#1:
Completed 124 out of 124 mounts in 2 hours 5 minutes 7 seconds. Average of 1 minutes 0 seconds per toolmount.
Completed 124 out of 125 unmounts in 1 hours 49 minutes 5 seconds. Average of 52 seconds per toolunmount.
10 hours 44 minutes 21 seconds spent selected. 0 seconds with active heater and 0 seconds with standby heater.
------------
Tool#49:
Completed 8 out of 8 mounts in 1 minutes 7 seconds. Average of 8 seconds per toolmount.
Completed 8 out of 8 unmounts in 42 seconds. Average of 5 seconds per toolunmount.
4 minutes 51 seconds spent selected. 0 seconds with active heater and 0 seconds with standby heater.
------------
```

## Installation Instructions
### Install with Moonraker Autoupdate Support
This plugin assumes that you installed Klipper into your home directory (usually `/home/pi`). 

1) Clone this repo into your home directory where Klipper is installed:
```
cd ~
git clone https://github.com/TypQxQ/Klipper_ToolChanger.git
```

2) Edit `moonraker.conf` by adding the following entry:
```
[update_manager client klipper_toolchanger]
type: git_repo
path: ~/Klipper_ToolChanger
origin: https://github.com/TypQxQ/Klipper_ToolChanger.git
install_script: install.sh
is_system_service: False
```

3) Run the `install.sh` script
```
~/Klipper_ToolChanger/install.sh
```

Klipper_ToolChanger will show up in the update the next time you restart moonraker, or you can restart mooraker right away with: `sudo systemctl restart moonraker`.
If you encouter errors after an automatic Klipper update you can safetly run the `install.sh` scipt again to repair the links to the extension.

### Manual Install
Copy the python (`*.py`) files into the `\klipper\klipper\extras` directory. Assuming Klipper is installed in your home directory:
```
cp ./*.py ~/klipper/klippy/extras/
```
Then restart Klipper to pick up the extensions.

## To do:
* Add selectable automatic calculation of active times based on previous times. Ex:
  * Mean Layer time Standby mode. - Save time at every layerchange and at toolchange set to mean time of last 3 layers *2 or at last layer *1.5 with a Maximum and a minimum time. Needs to be analyzed further.
  * Save the time it was in Standby last time and apply a fuzzfactor. Put tool in standby and heatup with presumption that next time will be aproximatley after the same time as last. +/- Fuzzfactor.

## Configuration requirements
* `[input_shaper]` needs to be used for input shaper to wordk.

## G-Code commands:
* `TOOL_LOCK` - Lock command
* `TOOL_UNLOCK` - Unlock command
* `KTCC_Tn` - T0, T1, T2, etc... A select command is created for each tool. 
  * `R` - Calls SAVE_CURRENT_POSITION with the variable as a RESTORE_POSITION_TYPE. For example "T0 R1" will call "SAVE_CURRENT_POSITION RESTORE_POSITION_TYPE=1" before moving. Positioned is restored with "RESTORE_POSITION" from below.
* `KTCC_TOOL_DROPOFF_ALL` - Dropoff the current tool without picking up another tool
* `SET_AND_SAVE_FAN_SPEED` - Set the fan speed of specified tool or current tool if no `P` is supplied. Then save to be recovered at ToolChange.
  * `S` - Fan speed 0-255 or 0-1, default is 1, full speed.
  * `P` - Fan of this tool. Default current tool.
* `TEMPERATURE_WAIT_WITH_TOLERANCE` - Waits for all temperatures, or a specified tool or heater's temperature.
This command can be used without any additional parameters. Without parameters it waits for bed and current extruder. Only one of either TOOL or HEATER may be used.
  - `TOOL` - Tool number.
  - `HEATER` - Heater number. 0="heater_bed", 1="extruder", 2="extruder1", 3="extruder2", etc. Only works if named as default, this way.
  - `TOLERANCE` - Tolerance in degC. Defaults to 1*C. Wait will wait until heater is between set temperature +/- tolerance.
* `SET_TOOL_TEMPERATURE` - Set tool temperature.
  * `TOOL` - Tool number, optional. If this parameter is not provided, the current tool is used.
  * `STDB_TMP` - Standby temperature(s), optional
  * `ACTV_TMP` - Active temperature(s), optional
  * `CHNG_STATE` - Change Heater State, optional: 0 = off, 1 = standby temperature(s), 2 = active temperature(s).
  * `STDB_TIMEOUT` - Time in seconds to wait between changing heater state to standby and setting heater target temperature to standby temperature when standby temperature is lower than tool temperature.
    * Use for example 0.1 to change immediately to standby temperature.
  * `SHTDWN_TIMEOUT` - Time in seconds to wait from docking tool to shutting off the heater, optional.
    * Use for example 86400 to wait 24h if you want to disable shutdown timer.
* `SET_GLOBAL_OFFSET` - Set a global offset that can be applied to all tools
  * `X` / `Y` / `Z` - Set the X/Y/Z offset position
  * `X_ADJUST` / `Y_ADJUST` / `Z_ADJUST` - Adjust the X/Y/Z offset position incramentally
* `SET_TOOL_OFFSET` - Set the offset of an individual tool
  * `TOOL` - Tool number, optional. If this parameter is not provided, the current tool is used.
  * `X` / `Y` / `Z` - Set the X/Y/Z offset position
  * `X_ADJUST` /`Y_ADJUST` / `Z_ADJUST` - Adjust the X/Y/Z offset position incramentally  
* `SET_PURGE_ON_TOOLCHANGE` - Sets a global variable that can disable all purging (can be used in macros) when loading/unloading. For example when doing a TAMV/ZTATP tool alignement.
* `SAVE_POSITION` - Sets the Restore type and saves specified position for the toolhead. This command is usually used inside the custom g-code of the slicer software. The restore_position_on_toolchange_type will be changed to reflect the passed parameters.
  * X= X position to save, optional but Y must be specifie or this will be ignored.
  * Y= Y position to save, optional but X must be specifie or this will be ignored.
  * Z= Z position to save, optional but X and Y must be specifie or this will be ignored.
    * With no parameters it will set Restore type to 0, no restore.
    * With X and Y parameters it will save the specified X and Y. Sets restore type to 1, restore XY.
    * With X, Y and Z parameters it will save the specified X, Y and Z. Sets restore type to 2, restore XYZ.
* `SAVE_CURRENT_POSITION` - Save the current G-Code position of the toolhead. This command is usually used inside the pickup_gcode script or the custom g-code of the slicer software.
  * RESTORE_POSITION_TYPE= Type of restore, optional. If not specified, restore_position_on_toolchange_type will not be changed.
    * 0: No restore
    * 1: Restore XY
    * 2: Restore XYZ
* `RESTORE_POSITION` - Restore position to the latest saved position. This command is usually used inside the pickup_gcode script.
  * RESTORE_POSITION_TYPE= Type of restore, optional. If not specified, restore_position_on_toolchange_type will be used.
    * 0: No restore
    * 1: Restore XY
    * 2: Restore XYZ
* `KTCC_SET_GCODE_OFFSET_FOR_CURRENT_TOOL` - 
* `KTCC_LOG_TRACE` - Send a message to log at this logging level.
  * MSG= The message to be sent.
* `KTCC_LOG_DEBUG` - As above for this level.
* `KTCC_LOG_INFO` - As above for this level.
* `KTCC_LOG_ALWAYS` - As above for this level.
* `KTCC_SET_LOG_LEVEL` - Set the log level for the KTCC
  * LEVEL= Level of logging to print on screen
    * 0: Only the Always messages
    * 1: Info messages and above
    * 2: Debug messages and above
    * 3: Trace messages and above
  * LOGFILE= Level of logging to save to file, KTCC.log in same directory as other logs.
* `KTCC_DUMP_STATS` - Dump the KTCC statistics
* `KTCC_RESET_STATS` - Resets all saved statistics, you may regret this.
* `KTCC_INIT_PRINT_STATS` - Run at start of a print to reset the KTCC print statistics.
* `KTCC_DUMP_PRINT_STATS` - Run at end of a print to list statistics since last print reset.

## Values accesible from Macro for each object
- **Toollock**
  - `global_offset` - Global offset.
  - `tool_current` - -2: Unknown tool locked, -1: No tool locked, 0: and up are toolnames.
  - `saved_fan_speed` - Speed saved at each fanspeedchange to be recovered at Toolchange.
  - `purge_on_toolchange` - For use in macros to enable/disable purge/wipe code globaly.
  - `restore_position_on_toolchange_type` - The type of restore position:
    - 0: No restore
    - 1: Restore XY
    - 2: Restore XYZ
  - `saved_position` - The position saved when the latest T# command had a RESTORE_POSITION parameter to other than 0
- **Tool** - The tool calling this macro is referenced as `myself` in macros. When running for example `T3` to pickup the physical tool, in `pickup_gcode:` of one can write `{myself.name}` which would return `3`.
  - `name` - id. 0, 1, 2, etc.
  - `is_virtual` - If this tool has another layer of toolchange possible.
  - `physical_parent_id` - Parent physical tool that holds tool coordinates. Can be same as this.
  - `extruder` - extruder name as configured.
  - `fan` - fan name.
  - `lazy_home_when_parking` - When set to 1, will home unhomed XY axes if needed and will not move any axis if already homed and parked. 2 Will also home Z if not homed.
  - `meltzonelength` - Meltzonelength to unload/load filament at toolpak. See e3d documentation.
  - `zone` - Fast aproach coordinates when parking
  - `park` - Parking spot, slow aproach.
  - `offset` - Tool offset.
  - `heater_state` - 0 = off, 1 = standby temperature, 2 = active temperature. Placeholder.
  - `heater_active_temp` - Temperature to set when in active mode.
  - `heater_standby_temp` - Temperature to set when in standby mode.
  - `idle_to_standby_time` - Time in seconds from being parked to setting temperature to standby the temperature above. Use 0.1 to change imediatley to standby temperature.
  - `idle_to_powerdown_time` - Time in seconds from being parked to setting temperature to 0. Use something like 86400 to wait 24h if you want to disable. Requred on Physical tool.
- **ToolGroup**
  - `is_virtual` - As above
  - `physical_parent_id` - As above
  - `lazy_home_when_parking` - As above

## Example configuration
My full and updated configuration file backup can be found here:
https://github.com/TypQxQ/DuetBackup/tree/main/qTC-Klipper

## Updates 08/03/2023
Added per print statistics and a wrapper around G28 to disable saving statistics while homing.
The latter led to MCU Timer to close error when loading a tool at homing.
* `KTCC_INIT_PRINT_STATS` - Run at start of a print to reset the KTCC print statistics.
* `KTCC_DUMP_PRINT_STATS` - Run at end of a print to list statistics since last print reset.

## Updates 22/02/2023
This is not a simple upgrade, it has some configuration updates.
A namechange to KTCC (Klipper Tool Changer Code) is also in the works).

- **News:**
  - Virtual Tools
  - Logfile
  - Statistics

- **Changes to Configuration:**
  - LogLevel under ToolLock is deprecated.
  - Must include new section ```[ktcclog]``` before all other Toollock, tool, and the others..
  - New ```virtual_toolload_gcode:`` parameter to tools.
  - New ```virtual_toolunload_gcode:`` parameter to tools.

- **Changes to commands:**
  - T_1 => KTCC_TOOL_DROPOFF_ALL
  - T# => KTCC_T# (ex. T0 => KTCC_T0)

- **New  commands:**
  - KTCC_SET_GCODE_OFFSET_FOR_CURRENT_TOOL
  - KTCC_LOG_TRACE
  - KTCC_LOG_DEBUG
  - KTCC_LOG_INFO
  - KTCC_LOG_ALWAYS
  - KTCC_SET_LOG_LEVEL
  - KTCC_DUMP_STATS
  - KTCC_RESET_STATS
