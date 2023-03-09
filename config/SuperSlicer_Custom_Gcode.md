Here are the custom G-codes I use in SuperSlicer on my ToolChanger as an example.

Start G-code:
 - I don't heat the tools before actually using them so I don't degrade filament.
 - Using e3d Revo the heatup times for the tools are verry fast.
```
KTCC_INIT_PRINT_STATS

; Don't heat the tools yet. (Using G10 so SuperSlicer and PrusaSlicer recognizes we set a tool temperature)
G10 P0 R0 S0 A0	; Don't heat the tools yet. (Using G10 so SuperSlicer and PrusaSlicer recognizes we set a tool temperature)
G10 P1 R0 S0 A0	; Don't heat the tools yet
G10 P2 R0 S0 A0	; Don't heat the tools yet
; Heat the bed first
M140 S[first_layer_bed_temperature]
; Wait for bed to reach temperature with 2 degrees tolerance
M116 H0 S2 ; Wait for bed to reach temperature with 2 degrees tolerance

M568 P[initial_extruder] R{filament_toolchange_temp[initial_extruder]} S{first_layer_temperature[initial_extruder]+extruder_temperature_offset[initial_extruder]} A1
G28

;Custom Mesh only on print area
BED_MESH_CALIBRATE AREA_START={first_layer_print_min[0]},{first_layer_print_min[1]} AREA_END={first_layer_print_max[0]},{first_layer_print_max[1]}

G0 Z3 F5000	; Ensure nozzle is at 3mm over the bed
SAVE_POSITION X={first_layer_print_max[0]} Y={first_layer_print_min[1]}
T[initial_extruder]	; Mount extruder first used (even if only one extruder used). Waits for temperature inside the script.

;G0 Z3 F5000	; Ensure nozzle is at 3mm over the bed
G0 X{first_layer_print_max[0]} Y{first_layer_print_min[1]} Z3 F30000
```

End G-code
```
; Custom gcode to run at end of print
M104 S0 		; turn off temperature
G10 P0 S0 R0 A0	; turn off extruder 0
G10 P1 S0 R0 A0	; turn off extruder 1
G10 P2 S0 R0 A0	; turn off extruder 2
M140 S0 		; turn off bed
T_1		; dropoff current tool
G91 		; relative moves
G0 Z20  		; move bed down another 30mm
G90 		; absolute moves
G0 X1 Y1 F30000	; Move toolhead out of the way
SAVE_POSITION         ; Reset saved position.
KTCC_DUMP_PRINT_STATS ; Print statistics to console.
```

ToolChange G-code
  - Sets the temperature before activating the tool in case this is the first time the tool is selected.
  - On first layer it sets the temperature for the next tool to first layer temperature.
```
{if layer_num < 2}M568 P[next_extruder] R{filament_toolchange_temp[next_extruder]} S{first_layer_temperature[next_extruder]+extruder_temperature_offset[next_extruder]} A2 ;First layer temperature for next extruder
{else}M568 P[next_extruder] R{filament_toolchange_temp[next_extruder]} S{temperature[next_extruder]+extruder_temperature_offset[next_extruder]} A2 ;Other layer temperature for next extruder
{endif}
T{next_extruder}```
