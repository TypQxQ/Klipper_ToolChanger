# More complex example

This are  example files with macros to get you started.
* It uses T0 as a physical tool having T1-T8 as virtual tools.
* T9 and T10 are physical tools without virtual tools.
* T49 is a physical tool without a heater, fan or extruder. Only has a Z probe.

The files should be added to your printer.cfg like:

```
[include custom/tools.cfg]
[include custom/tools.cfg]
```

This is for use with a Jubilee style printer.
