# spike-tools
Utilities for experimenting with Lego Spike Hub

To install dependencies
```sh
pip3 install -r requirements.txt
```

## cp.py
Copy a file to the hub filesystem.
```
usage: cp.py [-h] [-t TTY] file [dir]
```
The default tty device is `/dev/ttyACM0`. The port path can be discovered with `sudo python -m serial.tools.list_ports`

## convert_sound.py
Converts a sound file to a format accepted by `hub.sound.play()` method. Accepts any input format supported by `librosa`.

```
usage: convert_sound.py [-h] [-s START] [-d DURATION] file
```

