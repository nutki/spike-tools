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

## spikejsonrpc.py
A module to communicate with the Spike Hub using JSON RPC. Can be used to manage program slots of the on brick selector.

```
usage: spikejsonrpc.py [-h] [-t TTY] [--debug]
                       {list,ls,fwinfo,mv,upload,cp,rm,start,stop,display} ...

Tools for Spike Hub RPC protocol

positional arguments:
  {list,ls,fwinfo,mv,upload,cp,rm,start,stop,display}
    list (ls)           List stored programs
    fwinfo              Show firmware version
    mv                  Changes program slot
    upload (cp)         Uploads a program
    rm                  Removes the program at a given slot
    start               Starts a program
    stop                Stop program execution
    display             Displays image on the LED matrix

optional arguments:
  -h, --help            show this help message and exit
  -t TTY, --tty TTY     Spike Hub device path
  --debug               Enable debug
```
