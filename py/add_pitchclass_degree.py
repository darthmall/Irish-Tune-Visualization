#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from tune_viz.models import *
import music21

total = PitchClass.objects.count()

for i, pc in enumerate(PitchClass.objects.all()):
    print('{: >7,d} / {: <7,d}'.format(i + 1, total))

    pc.degree = music21.pitch.convertNameToPitchClass(pc.pitch)
    pc.save()