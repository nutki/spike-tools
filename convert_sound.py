#!/usr/bin/python3
import numpy as np
import librosa
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Converts sound files into Lego Spike Hub format.')
parser.add_argument('file', help='input file')
parser.add_argument('-s', '--start', type=float, help='start reading after this time (in seconds)', default=0)
parser.add_argument('-d', '--duration', type=float, help='only load up to this much audio (in seconds)', default=None)
args = parser.parse_args()

base, ext = os.path.splitext(args.file)

x, sr = librosa.load(args.file, sr=16000, duration=args.duration, offset=args.start)

res = np.vectorize(lambda x: np.int16(np.round((x + 1)/2 * 4095)))(x)

res.tofile(base + '.spike.bin')
