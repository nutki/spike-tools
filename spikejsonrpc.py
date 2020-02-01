#!/usr/bin/env python3
import serial
import base64
import os
import sys
import argparse
from tqdm import tqdm
import time
import json
import random
import string
import logging
from datetime import datetime

letters = string.ascii_letters + string.digits + '_'
def random_id(len = 4):
  return ''.join(random.choice(letters) for _ in range(4))

class RPC:
  def __init__(self, tty = '/dev/ttyACM0'):
    self.ser = serial.Serial(tty, 115200)
    self.recv_buf = bytearray()

  def recv_message(self, timeout = 1):
    start_time = time.time()
    elapsed = 0
    while True:
      pos = self.recv_buf.find(b'\x0d')
      if pos >= 0:
        result = self.recv_buf[:pos]
        self.recv_buf = self.recv_buf[pos+1:]
        try:
          return json.loads(result)
        except json.JSONDecodeError:
          logging.debug("Cannot parse JSON: %s" % result)
      c = self.ser.in_waiting
      if c == 0 and elapsed > timeout:
        break
      self.ser.timeout = 1 - timeout
      self.recv_buf = self.recv_buf + self.ser.read(c if c else 1)
      elapsed = time.time() - start_time
    return None

  def send_message(self, name, params = {}):
    while True:
      if not self.recv_message(timeout=0):
        break
    id = random_id()
    msg = {'m':name, 'p': params, 'i': id}
    msg_string = json.dumps(msg)
    logging.debug('sending: %s' % msg_string)
    self.ser.write(msg_string.encode('utf-8'))
    self.ser.write(b'\x0D')
    return self.recv_response(id)

  def recv_response(self, id):
    while True:
      m = self.recv_message()
      if 'i' in m and m['i'] == id:
        logging.debug('response: %s' % m)
        if 'e' in m:
          error = json.loads(base64.b64decode(m['e']).decode('utf-8'))
          raise ConnectionError(error)
        return m['r']
      logging.debug('while waiting for response: %s' % m)

# Program Methods
  def program_execute(self, n):
    return self.send_message('program_execute', {'slotid': n})

  def program_terminate(self):
    return self.send_message('program_terminate')

  def get_storage_information(self):
    return self.send_message('get_storage_status')

  def start_write_program(self, name, size, slot, created, modified):
    meta = {'created': created, 'modified': modified, 'name': name }
    return self.send_message('start_write_program', {'slotid':slot, 'size': size, 'meta': meta})

  def write_package(self, data, transferid):
    return self.send_message('write_package', {'data': str(base64.b64encode(data), 'utf-8'), 'transferid': transferid})

  def move_project(self, from_slot, to_slot):
    return self.send_message('move_project', {'old_slotid': from_slot, 'new_slotid': to_slot})

  def remove_project(self, from_slot):
    return self.send_message('remove_project', {'slotid': from_slot })

# Light Methods
  def display_set_pixel(self, x, y, brightness = 9):
    return self.send_message('scratch.display_set_pixel', { 'x':x, 'y': y, 'brightness': brightness})

  def display_clear(self):
    return self.send_message('scratch.display_clear')

  def display_image(self, image):
    return self.send_message('scratch.display_image', { 'image':image })

  def display_image_for(self, image, duration_ms):
    return self.send_message('scratch.display_image_for', { 'image':image, 'duration': duration_ms })

  def display_text(self, text):
    return self.send_message('scratch.display_text', {'text':text})

# Hub Methods
  def get_firmware_info(self):
    return self.send_message('get_firmware_info')


if __name__ == "__main__":
  def handle_list():
    info = rpc.get_storage_information()
    storage = info['storage']
    slots = info['slots']
    print("%2s %-40s %6s %6s %20s" % ("#", "Name", "Size", "Id", "Last Modified"))
    for i in range(20):
      if not str(i) in slots:
        print("%2s" % i)
      else:
        sl = slots[str(i)]
        modified = datetime.utcfromtimestamp(sl['modified']/1000).strftime('%Y-%m-%d %H:%M:%S')
        print("%2s %-40s %5db %6s %20s" % (i, sl['name'], sl['size'], sl['id'], modified))
    print("%s/%s%s Free" % (storage['total'], storage['free'], storage['unit']))
    pass
  def handle_fwinfo():
    info = rpc.get_firmware_info()
    fw = '.'.join(str(x) for x in info['version'])
    rt = '.'.join(str(x) for x in info['runtime'])
    print("Firmware version: %s; Runtime version: %s" % (fw, rt))
  def handle_upload():
    with open(args.file, "rb") as f:
      size = os.path.getsize(args.file)
      name = args.name if args.name else args.file
      now = int(time.time() * 1000)
      start = rpc.start_write_program(name, size, args.to_slot, now, now)
      bs = start['blocksize']
      id = start['transferid']
      with tqdm(total=size, unit='B', unit_scale=True) as pbar:
        b = f.read(bs)
        while b:
          rpc.write_package(b, id)
          pbar.update(len(b))
          b = f.read(bs)


  parser = argparse.ArgumentParser(description='Tools for Spike Hub RPC protocol')
  parser.add_argument('-t', '--tty', help='Spike Hub device path', default='/dev/ttyACM0')
  parser.add_argument('--debug', help='Enable debug', action='store_true')
  parser.set_defaults(func=lambda: parser.print_help())
  sub_parsers = parser.add_subparsers()

  list_parser = sub_parsers.add_parser('list', aliases=['ls'], help='List stored programs')
  list_parser.set_defaults(func=handle_list)

  fwinfo_parser = sub_parsers.add_parser('fwinfo', help='Show firmware version')
  fwinfo_parser.set_defaults(func=handle_fwinfo)

  mvprogram_parser = sub_parsers.add_parser('mv', help='Changes program slot')
  mvprogram_parser.add_argument('from_slot', type=int)
  mvprogram_parser.add_argument('to_slot', type=int)
  mvprogram_parser.set_defaults(func=lambda: rpc.move_project(args.from_slot, args.to_slot))

  cpprogram_parser = sub_parsers.add_parser('upload', aliases=['cp'], help='Uploads a program')
  cpprogram_parser.add_argument('file')
  cpprogram_parser.add_argument('to_slot', type=int)
  cpprogram_parser.add_argument('name', nargs='?')
  cpprogram_parser.set_defaults(func=handle_upload)

  rmprogram_parser = sub_parsers.add_parser('rm', help='Removes the program at a given slot')
  rmprogram_parser.add_argument('from_slot', type=int)
  rmprogram_parser.set_defaults(func=lambda: rpc.remove_project(args.from_slot))

  startprogram_parser = sub_parsers.add_parser('start', help='Starts a program')
  startprogram_parser.add_argument('slot', type=int)
  startprogram_parser.set_defaults(func=lambda: rpc.program_execute(args.slot))

  stopprogram_parser = sub_parsers.add_parser('stop', help='Stop program execution')
  stopprogram_parser.set_defaults(func=lambda: rpc.program_terminate())

  display_parser = sub_parsers.add_parser('display', help='Displays image on the LED matrix')
  display_parser.add_argument('image')
  display_parser.set_defaults(func=lambda: rpc.display_image(args.image))

  args = parser.parse_args()
  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
  rpc = RPC(args.tty)
  args.func()
