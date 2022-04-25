Here are the custom G-codes I use in SuperSlicer on my ToolChanger as an example.

Start G-code:
 - I don't heat the tools before actually using them so I don't degrade filament.
 - Using e3d Revo the heatup times for the tools are verry fast.
```
G10 P0 R0 S0 A0	; Don't heat the tools yet. (Using G10 so SuperSlicer and PrusaSlicer recognizes we set a tool temperature)
G10 P1 R0 S0 A0	; Don't heat the tools yet
G10 P2 R0 S0 A0	; Don't heat the tools yet
M140 S[first_layer_bed_temperature]	; Heat the bed first
M116 H0  ; Wait for bed to reach temperature with 2 degrees tolerance

M568 P[initial_extruder] R{filament_toolchange_temp[initial_extruder]} S{first_layer_temperature[initial_extruder]+extruder_temperature_offset[initial_extruder]} A1	; Set temperature for the first tool used and put in standby
G28

;Custom Mesh only on print area
BED_MESH_CALIBRATE AREA_START={first_layer_print_min[0]},{first_layer_print_min[1]} AREA_END={first_layer_print_max[0]},{first_layer_print_max[1]}

G0 Z10 F5000	       ; Ensure nozzle is at 10mm over the bed
T[initial_extruder]	 ; Select extruder first used (even if only one extruder used). Waits for temperature inside the script.

G0 X{first_layer_print_min[0]} Y{first_layer_print_min[1]} Z3 F30000
```

End G-code
```
M104 S0 		    ; turn off temperature
G10 P0 S0 R0 A0	; turn off extruder 0
G10 P1 S0 R0 A0	; turn off extruder 1
G10 P2 S0 R0 A0	; turn off extruder 2
M140 S0 		    ; turn off bed
T_1		          ; dropoff current tool
G91 		        ; relative moves
G0 Z20  		    ; move bed down another 30mm
G90 	         	; absolute moves
G0 X1 Y1 F30000	; Move toolhead out of the way
```

ToolChange G-code
  - Sets the temperature before activating the tool in case this is the first time the tool is selected.
  - On first layer it sets the temperature for the next tool to first layer temperature.
```
{if layer_num < 1}M568 P[next_extruder] R{filament_toolchange_temp[next_extruder]} S{first_layer_temperature[next_extruder]+extruder_temperature_offset[next_extruder]} A2 ;First layer temperature
{else}M568 P[next_extruder] R{filament_toolchange_temp[next_extruder]} S{temperature[next_extruder]+extruder_temperature_offset[next_extruder]} A2 ;Other layer temperature
{endif}
T{next_extruder} ; Actual ToolChange
```
