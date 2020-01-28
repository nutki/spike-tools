#!/usr/bin/env python3
import serial
import base64
import os
import sys
import argparse
from tqdm import tqdm
import time

parser = argparse.ArgumentParser(description='Sends files to Spike Hub file system')
parser.add_argument('file', help='file name')
parser.add_argument('dir', nargs='?', help='destination directory', default = '')
parser.add_argument('-t', '--tty', help='Spike Hub device path', default='/dev/ttyACM0')
args = parser.parse_args()

path, file = os.path.split(args.file)
size = os.path.getsize(args.file)

ser = serial.Serial(args.tty, 115200, timeout = 0.1)

def wait_for_prompt():
  buf = b''
  start_time = time.time()
  elapsed = 0
  while elapsed < 1:
    c = ser.in_waiting
    ser.timeout = 1 - elapsed
    x = ser.read(c if c else 1)
    buf = (buf + x)[-5:]
    if buf == b'\n>>> ':
      return
    elapsed = time.time() - start_time
  raise ConnectionError('failed to get to the command prompt (last characters: %s)' % buf)

def write_command(cmd):
  ser.write(cmd + b'\r\n')
  wait_for_prompt()

ser.write(b'\x03')
wait_for_prompt()
write_command(b'')
write_command(b"import ubinascii")
write_command(b"f = open('/%s/%s', 'wb')" % (args.dir.encode('utf8'), file.encode('utf8')))
print('Copying "%s" to "%s/%s"' % (args.file, args.dir, file))
with tqdm(total=size, unit='B', unit_scale=True) as pbar:
  with open(args.file, "rb") as f:
    byte = f.read(192)
    while len(byte) > 0:
      write_command(b"f.write(ubinascii.a2b_base64('%s'))" % base64.b64encode(byte))
      pbar.update(len(byte))
      byte = f.read(192)
write_command(b"f.close()")
ser.write(b'\x04')
ser.flush()
