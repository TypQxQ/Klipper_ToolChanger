# Required and Optional macros

The required macros change how Klipper uses those commands to make use of the toolchanger. They are all backwards compatible. This macros are highly recommended to be included.

The optional macros are to add more commands for higher compatibility with for example RRF G-code.

> [!NOTE]  
> You can add the whole directory to the printer.cfg by adding the relative path to the macros directory for example:

```
[include toolchanger/macros/*.cfg]
```

<br>

## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Required macros

  | Command | Description | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parameters&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
  | ------- | ----------- | ---------- |
  | `M104` | Set tool temperature. If Tool number is not provided, current tool is used. If no S parameter is provided it will dump current temperature settings for the tool.| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P. <br>`S...` Active temperature to set. |
  | `M106` | Set fan speed. If Tool number is not provided, current tool is used. If no S parameter is provided, set full fan speed. | `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P. <br>`S[0-1]` or `S[2-255]` Fan speed 0-1 or 2-255 |
  | `M107` | Turn off fan. If Tool number is not provided, current tool is used| `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P |
  | `M109` | Waits temperature with a tolerance defaulting to +//1. Optional temperature can be defined when tool is defined, setting the tool as active with specified temperature. If heater is defined it will wait for that heater. Optional tolerance can be specified. Only waits if target temperature is >40*C  | `H[0..n]` Heater number, optional <br>`T[0..n]` Tool number <br>`P[0..n]` Alternative to T <br>`W[-50]` Tolerance in degC |

<br>
  
## ![#f03c15](/doc/f03c15.png) ![#c5f015](/doc/c5f015.png) ![#1589F0](/doc/1589F0.png) Optional macros

  | Command | Description | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Parameters&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; |
  | ------- | ----------- | ---------- |
  | `G10` | Alias to M568  |  |
  | `M116` | Alias to M109  |  |
  | `M568` |Set tool temperature. If Tool number is not provided, current tool is used | `P[0..n]` Tool number, optional <br> `T[0..n]` Alternative to P. <br>`S...` Set active temperature, optional <br>`R...` Set standby temperature, optional <br>`A...` Set Heater state, optional<br> (0= off), (1 = standby temperature), (2 = active temperature) <br>`N...` Standby timeout is the time to linger at Active temp. after setting the heater to standby. Could be used for a tool with long heatup times and is only put in standby short periods of thme throughout a print and should stay at active temperature longer time. <br>`O...` Timer from Standby to off. Used for example so a tool used only on first few layers shuts down after 30 minutes of inactivity and won't stay at 175*C standby for the rest of a 72h print. |
  | `M204` | Set acceleration to either S or lowest of supplied P and T. | `S...` Acceleration, optional<br> `P...` Print acceleration, RRF compatible<br> `T...` Travel acceleration, RRF compatible |
  | `M566` | Set Square Corner Velocity in RRF style. Only the lower of required X or Y will be used| `X...` X axis<br> `Y...` Y axis |
