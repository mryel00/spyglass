Spyglass offers a few CLI parameters for the most commonly used camera controls.
Controls not directly available through the CLI can be used with the `--controls` (`-c`) or `--controls-string` (`-cs`) parameters or the `CONTROLS` section inside the `spyglass.conf`.


## How to list available controls?

Spyglass provides a CLI parameter to list all available controls `--list-controls`. The available controls are then printed onto your shell under `Available controls:`.

Following shows an example for a Raspberry Pi Module v3:
```sh
Available controls:
NoiseReductionMode (int)      : min=0 max=4 default=0
ScalerCrop (tuple)            : min=(0, 0, 0, 0) max=(65535, 65535, 65535, 65535) default=(0, 0, 0, 0)
Sharpness (float)             : min=0.0 max=16.0 default=1.0
AwbEnable (bool)              : min=False max=True default=None
FrameDurationLimits (int)     : min=33333 max=120000 default=None
ExposureValue (float)         : min=-8.0 max=8.0 default=0.0
AwbMode (int)                 : min=0 max=7 default=0
AeExposureMode (int)          : min=0 max=3 default=0
Brightness (float)            : min=-1.0 max=1.0 default=0.0
AfWindows (tuple)             : min=(0, 0, 0, 0) max=(65535, 65535, 65535, 65535) default=(0, 0, 0, 0)
AfSpeed (int)                 : min=0 max=1 default=0
AfTrigger (int)               : min=0 max=1 default=0
LensPosition (float)          : min=0.0 max=32.0 default=1.0
AfRange (int)                 : min=0 max=2 default=0
AfPause (int)                 : min=0 max=2 default=0
ExposureTime (int)            : min=0 max=66666 default=None
AeEnable (bool)               : min=False max=True default=None
AeConstraintMode (int)        : min=0 max=3 default=0
AfMode (int)                  : min=0 max=2 default=0
AnalogueGain (float)          : min=1.0 max=16.0 default=None
ColourGains (float)           : min=0.0 max=32.0 default=None
AfMetering (int)              : min=0 max=1 default=0
AeMeteringMode (int)          : min=0 max=3 default=0
Contrast (float)              : min=0.0 max=32.0 default=1.0
Saturation (float)            : min=0.0 max=32.0 default=1.0
```


## How to apply a camera control?

There are multiple ways to apply a camera control. All methods are case insensitive.

### Shell

There are two different parameters to apply the controls:

- `--controls`/`-c` can be used multiple times, to set multiple controls. E.g. using `-c brightness=0.5 -c awbenable=false` will apply `0.5` to the `Brightness` and `False` as the new `AwbEnable` value.
- `--controls-string`/`cs` can be used only once. E.g. using `--controls-string "brightness=0.5, awbenable=16"` will apply `0.5` on the `Brightness` and `False` as the new `AwbEnable` control. Note: The `"` are required and the controls need to be separated by a `,`. This is intended only for parsing the config.

### Config

The `spyglass.conf` accepts camera controls under the `CONTROLS` option. E.g. `CONTROLS="brightness=0,awbenable=false"` will apply `0.5` to the `Brightness` and `False` as the new `AwbEnable` value.

### Webinterface

Spyglass also provides an API endpoint to change the camera controls during runtime. This endpoint is available under `http://<ip.of.your.pi>:<port>/controls` and cannot be changed.

Calling it without any parameters will show you a list of all available controls, like `--list-controls`.

E.g. `http://<ip.of.your.pi>:<port>/controls?brightness=0.5&awbenable=false` will apply `0.5` to the `Brightness` and `False` as the new `AwbEnable` value.

If you apply parameters the interface will show you the parameters Spyglass found inside the url and which controls got actually processed:
- `Parsed Controls` shows you the parameters Spyglass found during the request.
- `Processed Controls` shows you the parameters of the `Parsed Controls` Spyglass could actually set for the cam. 

E.g. `http://<ip.of.your.pi>:<port>/controls?brightness=0.5&foo=bar&foobar` will show you `Parsed Controls: [('brightness', '1'), ('foo', 'bar')]` and `Processed Controls: {'Brightness': 1}`.
