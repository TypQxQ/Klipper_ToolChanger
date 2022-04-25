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

### [toollock]

Configures the Locking mechanism and other common configuration for the Tools module.

```
#purge_on_toolchange: True
#   Here we can disable all purging. When disabled it overrides all other purge options. 
#   This can be turned off by a macro for automatic probing hot tools without probing them. 
#   For example when doing TAMV or ZTATP. The default is True.
#init_printer_to_last_tool: True
#   Initialise as it was turned off, unlock tool if none was loaded or lock if one was loaded. Defaults to True
#wipetype: 0                        # WipeType number as defined by [toolwipetype n]. Overwrites setting in [toolgroup n] defaults to -1 which is No Wipe if not defined anywhere.
tool_lock_gcode:
#   A list of G-Code commands to execute when the tool is locked 
#   in place by the TOOL_LOCK command. This parameter must
#   be provided.
tool_unlock_gcode:
#   A list of G-Code commands to execute when the tool is unlocked 
#   in place by the TOOL_UNLOCK command. This parameter must
#   be provided.
```

### [toolgroup 0]

Can be used for grouping settings common to multiple tools. 
At least one (the 0) must be specified and can be empty.

```
[toolgroup 0]
#is_virtual: True            # If True then must have a physical_parent declared and shares extruder, hotend and fan with the physical_parent
#physical_parent: 0          # Tool used as a Physical parent for all toos of this group. Only used if the tool i virtual.
#idle_to_standby_time: 30
#idle_to_powerdown_time: 600
```
