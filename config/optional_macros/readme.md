# Optional macros

This macros are highly recommended to be included.

> [!NOTE]  
> You can add the whole directory to the printer.cfg by adding the relative path to the macros directory for example:

```
[include toolchanger/macros/*.cfg]
```

<br>

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Calibration Command Reference

  | Command | Description | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parameters&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
  | ------- | ----------- | ---------- |
  | `M104` | Set tool temperature. If Tool number is not provided, current tool is used. If no S parameter is provided it will dump current temperature settings for the tool.| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P. <br>`S...` Active temperature to set. |
  | `M106` | Set fan speed. If Tool number is not provided, current tool is used. If no S parameter is provided, set full fan speed. | `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P. <br>`S[0-1] or[2-255]..` Fan speed 0-1 or 2-255 |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |
  | `M109` | Waits temperature with a tolerance defaulting to +//1. Optional temperature can be defined when tool is defined, setting the tool as active with specified temperature. If heater is defined it will wait for that heater. Optional tolerance can be specified | `P[0..n]` Heater number, optional <br>`T[0..n]` Tool number <br>`W[1..n]` Tolerance in degC |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |

  | `MMU_CALIBRATE_BOWDEN` | Measure the calibration length of the bowden tube used for fast load movement. This will be performed on gate #0 | `BOWDEN_LENGTH=..` The approximate length of the bowden tube but NOT longer than the real measurement. 50mm less that real is a good starting point <br>`HOMING_MAX=..` (default 100) The distance after the sepcified BOWDEN_LENGTH to search of the extruder entrance <br>`REPEATS=..` (default 3) Number of times to average measurement over <br>`SAVE=[0\|1]` (default 1)  Whether to save the result |
  | `MMU_CALIBRATE_GATES` | Optional calibration for loading of a sepcifed gate or all gates. This is calculated as a ratio of gate #0 and thus this is usually the last calibration step | `GATE=[0..n]` The individual gate position to calibrate <br>`ALL[0\|1]` Calibrate all gates 1..n sequentially (filament must be available in each gate) <br>`LENGTH=..` Distance (mm) to measure over. Longer is better, defaults to 400mm <br>`REPEATS=..` Number of times to average over <br>`SAVE=[0\|1]` (default 1)  Whether to save the result |
