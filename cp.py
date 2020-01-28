#!/usr/bin/env python3
import serial
import base64
import os
import sys
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Sends files to Spike Hub file system')
parser.add_argument('file', help='file name')
parser.add_argument('dir', nargs='?', help='destination directory', default = '')
parser.add_argument('-t', '--tty', help='Spike Hub device path', default='/dev/ttyACM0')
args = parser.parse_args()

path, file = os.path.split(args.file)
size = os.path.getsize(args.file)

ser = serial.Serial(args.tty, 115200, timeout = 0.1)
ser.write(b'\x03')
x = ser.read(1024)
ser.write("\r\n")
ser.write("import ubinascii\r\n")
ser.write("f = open('/%s/%s', 'wb')\r\n" % (args.dir, file))
x = ser.read(1024)
print(size)
with tqdm(total=size, unit='B', unit_scale=True) as pbar:
  with open(args.file, "rb") as f:
    byte = f.read(192)
    while len(byte) > 0:
      ser.write("f.write(ubinascii.a2b_base64('%s'))\r\n" % base64.b64encode(byte))
      x = ser.read(1024)
      pbar.update(len(byte))
      byte = f.read(192)
ser.write("f.close()\r\n")
ser.flush()
x = ser.read(1024)
