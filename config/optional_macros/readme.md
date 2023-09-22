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
  | `M104` | Set tool temperature. If Tool number is not provided, current tool is used. If no S parameter is provided it will dump current temperature settings for the tool.| `P[0..n]` Tool number, optional <br>  `T[0..n]` Same as P. <br> `S...` Active temperature to set. |
  | `M106` | Set fan speed. If Tool number is not provided, current tool is used. If no S parameter is provided, set full fan speed. | `T[0..n]` Tool number, optional <br>`S[0-1] or[2-255]..` Fan speed 0-1 or 2-255 <br>`MEASURED=..` User measured distance <br>`SAVE=[0\|1]` (default 1) Whether to save the result |
  | `MMU_CALIBRATE_ENCODER` | Calibration routine for MMU encoder | LENGTH=.. Distance (mm) to measure over. Longer is better, defaults to 500mm <br>`REPEATS=..` Number of times to average over <br>`SPEED=..` Speed of gear motor move. Defaults to long move speed <br>`ACCEL=..` Accel of gear motor move. Defaults to motor setting in ercf_hardware.cfg <br>`MINSPEED=..` & `MAXSPEED=..` If specified the speed is increased over each iteration between these speeds (only for experimentation) <br>`SAVE=[0\|1]` (default 1)  Whether to save the result |
  | `MMU_CALIBRATE_BOWDEN` | Measure the calibration length of the bowden tube used for fast load movement. This will be performed on gate #0 | `BOWDEN_LENGTH=..` The approximate length of the bowden tube but NOT longer than the real measurement. 50mm less that real is a good starting point <br>`HOMING_MAX=..` (default 100) The distance after the sepcified BOWDEN_LENGTH to search of the extruder entrance <br>`REPEATS=..` (default 3) Number of times to average measurement over <br>`SAVE=[0\|1]` (default 1)  Whether to save the result |
  | `MMU_CALIBRATE_GATES` | Optional calibration for loading of a sepcifed gate or all gates. This is calculated as a ratio of gate #0 and thus this is usually the last calibration step | `GATE=[0..n]` The individual gate position to calibrate <br>`ALL[0\|1]` Calibrate all gates 1..n sequentially (filament must be available in each gate) <br>`LENGTH=..` Distance (mm) to measure over. Longer is better, defaults to 400mm <br>`REPEATS=..` Number of times to average over <br>`SAVE=[0\|1]` (default 1)  Whether to save the result |
