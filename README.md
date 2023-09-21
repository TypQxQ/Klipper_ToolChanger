<p align="center">
  <img src="assets/toolchanger.jpg?raw=true" alt='A Toolchenager' width='40%'>
  <h1 align="center">Tools for klipper (KTCC - Klipper Tool Changer Code)</h1>
</p>

<p align="center">
Universal Toolchanger driver for Klipper
</p>

This are python modules, macros and example config for the
[Klipper 3D printer firmware](https://github.com/Klipper3d/klipper) to be able to work as a toolchanger. 
<p align="center">
  <a aria-label="Downloads" href="https://github.com/TypQxQ/Klipper_ToolChanger/releases">
    <img src="https://img.shields.io/github/release/TypQxQ/Klipper_ToolChanger?display_name=tag&style=flat-square">
  </a>
  <a aria-label="Stars" href="https://github.com/TypQxQ/Klipper_ToolChanger/stargazers">
    <img src="https://img.shields.io/github/stars/TypQxQ/Klipper_ToolChanger?style=flat-square">
  </a>
  <a aria-label="Forks" href="https://github.com/TypQxQ/Klipper_ToolChanger/network/members">
    <img src="https://img.shields.io/github/forks/TypQxQ/Klipper_ToolChanger?style=flat-square">
  </a>
  <a aria-label="License" href="https://github.com/TypQxQ/Klipper_ToolChanger/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/TypQxQ/Klipper_ToolChanger?style=flat-square">
  </a>
</p>

At it's simplest you need to specify extruder, fan, offset for each extruder tool.
Then add your macros for pickup, dropoff, toollock and toolunlock.

It doesn't matter if you lock the tool by a servo, stepper or moving the toolhead in a special way. Just as long as it can be written in GCODE.
Pickups are also custom Gcode. You can uses the parameters stored for each tool to aproach he ZONE fast, slow in 
to PARKING place and lock. Or it have a robotic arm place the tool. It's all posible. :D

[This](https://www.youtube.com/watch?v=cbRXn7R7JZM&t=52s) is a more complex example of it running on a toolchanger with an aditional ERCF under one tool. T0-8 uses first tool with virtual tools for the ERCF, calling the toolchanges recursively.

Inspiration comes mainly from how RRF enables toolchanging and from the HappyHare project.
I welcome any and all input and contributions. Don't be afraid to make a pull request :D

Thank you!

## Readme Table of Contents
**[Major feature](#---major-features)**<br>
**[Installation](#---installation)**<br>
\- [1-Install with Moonraker Autoupdate Support](#1-install-with-moonraker-autoupdate-support)<br>
\- [2-Manual Install](#2-manual-install)<br>
**[Configuration requirements](#---configuration-requirements)**<br>
**[G-Code commands](#---g-code-commands)**<br>
**[Values accesible from Macro for each object](#---values-accesible-from-macro-for-each-object)**<br>
**[Example configuration](#---example-configuration)**<br>

#### Other Docs:

**[Command Reference](./doc/command_ref.md)**<br>

<br>
 
## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Major features:
<ul>
  <li>Support any type of toolchanger and any type of tool</li>
  <li>Tools don't need to be extruders/hotends, can be anything.</li>
  <li>Each Tool is treated as an object and has it's own configuration having configurable coordinates for parking, tool offset, extruder, part cooling fan, etc.</li>
  <li>Tools don't need to be extruders/hotends, can be anything.</li>
  <li>Virtual tools - One tool can have multiple tools. Your T0-T8 can be on same extruder, fan and heater but having an MMU while T9 is another extruder and T10-T12 is another tool with 3 markers that can switched by a servo and finally T13 is a pick and place tool.</li>
  <li>Multiple tools can be grouped in ToolGroup. -Most configuration can be inherited from the group and overwritten when needed by the tool config section.</li>
  <li>Partcooling Fan speed is carried over on toolchange if the tool has a fan. M106/M107 defaults to fan of current_tool  but can also specify another tool.</li>
  <li>Extensive extruder temperature control:</li>
  <ul>
    <li>A tool heater can be set as Active, Standby or Off mode</li>
    <li>Diffrent Active and Standby temperatures for any tool. Switches to Active when selected and to Standby when Parked.</li>
    <li>Configurable delay from Standby to off when parked. If tool isn't used for 30 minutes it cools down until used again.</li>
    <li>Wait to reach temperature with configurable tolerance.</li>
    <li>Position prior to toolchange can optionaly be saved and restored after toolchange. Configurable axis.</li>
  </ul>
  <li>Current Tool persists at powerdown. Default but optional.</li>
  <li>Tool remaping. Remap a tool to another, no need to reslice.</li>
  <li>Sophisticated logging options (console and ktcc.log file)</li>
  <li>Moonraker update-manager support</li>
  <li>Persitance of state and statistics across restarts.</li>
  <li>Vast customization options!</li>
</ul>

<br>

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Installation

### 1\. Install with Moonraker Autoupdate Support
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

### 2\. Manual Install
Copy the python (`*.py`) files into the `\klipper\klipper\extras` directory. Assuming Klipper is installed in your home directory:
```
cp ./*.py ~/klipper/klippy/extras/
```
Then restart Klipper to pick up the extensions.

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Configuration requirements
* `[input_shaper]` needs to be used for input shaper to wordk.

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) G-Code commands:
Reffer to the [Command Reference](./doc/command_ref.md).<br>

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Values accesible from Macro for each object
- **Toollock**
  - `global_offset` - Global offset.
  - `tool_current` - -2: Unknown tool locked, -1: No tool locked, 0: and up are toolnames.
  - `saved_fan_speed` - Speed saved at each fanspeedchange to be recovered at Toolchange.
  - `purge_on_toolchange` - For use in macros to enable/disable purge/wipe code globaly.
  - `restore_axis_on_toolchange` - The axis to restore position:
    - : No restore
    - XY: Restore XY
    - XYZ: Restore XYZ
    - Etc
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

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Example configuration
My full and updated configuration file backup can be found here:
https://github.com/TypQxQ/DuetBackup/tree/main/qTC-Klipper

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Updates 21/09/2023
Added individual axis to position saving and restoring commands. Commited by viesturz.

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Updates 09/03/2023
Added Tool Remap. Point one or more tools to another one. Including fan and temperature. This is persistent at reboot.
* `KTCC_DISPLAY_TOOL_MAP` - Display the current mapping of tools to other KTCC tools.
* `KTCC_REMAP_TOOL` - The command to remap a tool or reset the remaping.
* `KTCC_CHECK_TOOL_REMAP` - Display all tool remaps.

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Updates 08/03/2023
Added per print statistics and a wrapper around G28 to disable saving statistics while homing.
The latter led to MCU Timer to close error when loading a tool at homing.
* `KTCC_INIT_PRINT_STATS` - Run at start of a print to reset the KTCC print statistics.
* `KTCC_DUMP_PRINT_STATS` - Run at end of a print to list statistics since last print reset.

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Updates 22/02/2023
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
