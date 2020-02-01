# spike-tools
Utilities for experimenting with Lego Spike Hub

To install dependencies
```sh
pip3 install -r requirements.txt
```

The default device address to communicate with the hub is `/dev/ttyACM0` and otherwise can be specified with `--tty` option. The port path can be discovered with `sudo python -m serial.tools.list_ports`.

Access to serial ports usually needs a special privilige. To avoid running every command with `sudo`
you can do the follwing in Linux (needs logout to become effective). 
```sh
sudo adduser <user name> dialout
```

If the center led of the hub flashes red shortly after connecting and/or you see random characters
appearing when manually connecting to the hub via a terminal (something like `ATE1 E0 ~x~`), this
likely indicates a modem controller is trying to talk to the hub (which won't succeed). Under 
Linux this can be disbled with:
```sh
sudo systemctl disable ModemManager
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

## cp.py
Copy a file to the hub filesystem.
```
usage: cp.py [-h] [-t TTY] file [dir]
```

## convert_sound.py
Converts a sound file to a format accepted by `hub.sound.play()` method. Accepts any input format supported by `librosa`.

```
usage: convert_sound.py [-h] [-s START] [-d DURATION] file
```
