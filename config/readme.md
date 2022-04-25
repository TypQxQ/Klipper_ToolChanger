# Configuration reference
This document is a reference for options available in the Klipper config file when adding the Tools module.

## Configuration examples
Can be found in the different subdirectories.
Feel free to add some for reference or send them my way and I will format, comment and add them.
- 

## Configuration order

ToolGroups must come before tools that use them. 
A Tool that is used as physical_parent must be configured before other virtual tools that use it as a parent.

## Configuration requirements

`[save_variables]` must be used as described in the Klipper documentation.
`[input_shaper]` needs to be used for input shaper to wordk.

### [toollock]

Configures the Locking mechanism and other common configuration for the Tools module.

```
#purge_on_toolchange: True
#   Here we can disable all purging. When disabled it overrides all other purge options. 
#   This can be turned off by a macro for automatic probing hot tools without probing them. 
#   For example when doing TAMV or ZTATP. The default is True.
#init_printer_to_last_tool: True
#   Initialise as it was turned off, unlock tool if none was loaded or lock if one was
#   loaded. Defaults to True
tool_lock_gcode:
#   A list of G-Code commands to execute when the tool is locked 
#   in place by the TOOL_LOCK command. This parameter must
#   be provided. This can also call a macro.
tool_unlock_gcode:
#   A list of G-Code commands to execute when the tool is unlocked 
#   in place by the TOOL_UNLOCK command. This parameter must
#   be provided. This can also call a macro.
```

### [toolgroup]

Can be used for grouping settings common to multiple tools. 
At least one (the 0) must be specified and can be empty.

```
[toolgroup 0]
#is_virtual: True
#   If True then must have a physical_parent declared and shares extruder, hotend and
#   fan with the physical_parent
#physical_parent: 0
#   Tool used as a Physical parent for all toos of this group. Only used if the tool i virtual.
#lazy_home_when_parking: 0
#   If the printer is able to home with the tool mounted.
#   When set to 1, will home unhomed XY axes if needed and will not move any axis
#   if already homed and parked. 2 Will also home Z if not homed.
#meltzonelength:0
#idle_to_standby_time: 30
#idle_to_powerdown_time: 600
#pickup_gcode
#dropoff_gcode
```

### [tool]

A tool can be a physical tool on a toolchanger, being picked up and dropped of, or it can be 
virtual on a tool. A virtual tool can be a ERCF, a roatating wheel, etc.

A virtual tool is a second layer of toolchanging. For example if using a physical e3d Revo 
with a Bondtech LGX Lite and two fans connected to a 9 port ERCF filament changer.
Then the [Tool 0] to [Tool 9] would have 0 as parent and all be virtual. When changing 
from T0 to T2, then only the ERCF script would run. But if changing from T11 to T2, 
then first a toolchange and then a ERCF filament change would occur.

A tool does not have to have a heater, extruder or fan. It can be a simple pen.

The only mandatory setting is "tool_group".

A virtual tool can inherit all and any configuration from the parent tool except for
"is_virtual" and "physical_parent". Both can be defined in a group, so basicly only 
the group needs to be specified for a group of tools 

```
[tool 0]
tool_group:
#   The Toolgroup number for this tool
#   Must be used and configured before thr tool using it.
#is_virtual: False
#   Defines this tool as physical or virtual.
#physical_parent:
#   Nr of the physical parent of this tool. Defaults not having one.
#extruder:
#   Name of extruder connected to this tool. For example "extruder" 
# or "extruder1" without the quotation marks. Defaults to having no extruder.
#fan:
#   Name of general fan configuration used as a partcooling fan. 
#   For example "partfan_t0". Defaults to having no extruder.
#zone:
#   Coordinates to when the toolhead is near the tool, used for fas aproach.
#   For example "550,5". This would be X550 Y5 in the printer coordinates.
park: 
#   Coordinates to when the tool is parked, aproach slowly from zone coordinates.
#   For example "598,5". This would be X598 Y5 in the printer coordinates.
#offset:
#   Offset of the tip of the tool to the coordinates of the head in X,Y,Z
#   For example "11.278,3.766,3.528". Defaults to "0,0,0"
#idle_to_standby_time: 0.1
#   Time in seconds from the tool being parked to setting temperature to standby 
#   if the temperature current temperature is above the standby temperature. 
#   Use 0.1 to change imediatley to standby temperature. Defaults to 0.1
#   If you use 0, then it disables the standby temperature.
#idle_to_powerdown_time: 600
#   Time in seconds from being parked to turning off the heater, setting temperature to 0. 
#   Use something like 86400 to wait 24h if you want to disable. Defaults to 600 (10 minutes).
#lazy_home_when_parking: 0
#   If the printer is able to home with the tool mounted.
#   When set to 1, will home unhomed XY axes if needed and will not move any axis
#   if already homed and parked. 2 Will also home Z if not homed.
#meltzonelength: 0
#   Length of the meltzone for retracting and inserting filament on toolchange. 18mm for e3d Revo.
#shaper_freq_x: 0
#shaper_freq_y: 0
#   Shaper frequency for this tool. For example "116.4". Defaults to "0".. See Klipper documentation for more details.
# shaper_type_x: "mzv"
# shaper_type_y: "mzv"
#   Shaper type for this tool. Defaults to "mzv". See Klipper documentation for more details.
#shaper_damping_ratio_x: 0
#shaper_damping_ratio_x: 0
#   Damping ratios of vibrations of X and Y axes used by input shaper. 
#   Defaults to "0.1". See Klipper documentation for more details.
#pickup_gcode:
#   A list of G-Code commands to execute when the tool is locked 
#   in place by the TOOL_LOCK command. This can also call a macro.
#dropoff_gcode:
#   A list of G-Code commands to execute when the tool is unlocked 
#   in place by the TOOL_UNLOCK command. This can also call a macro.
```

Not used yet:
```
#HeatMultiplyerAtFullFanSpeed = 1
#   Multiplier to be aplied to hotend temperature when fan is at maximum.
#   Will be multiplied with fan speed. Ex. 1.1 at 205*C and fan speed of 40% will set temperature to 213*C
```
