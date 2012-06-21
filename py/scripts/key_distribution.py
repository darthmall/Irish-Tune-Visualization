#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from django.db.models import Count
from tune_viz.models import *
import matplotlib.pyplot as plt
import numpy as np

data = []
jigs = Tune.objects.filter(rhythm='jig')

for i in range(7):
    keysig = []
    for x in jigs.filter(key__number_of_accidentals=i, key__accidentals='s').values('key__name', 'key__accidentals').annotate(frequency=Count('key__name')):
        keysig.append(x['frequency'])

    data.append(keysig)

for i in range(6, 0, -1):
    keysig = []
    for x in jigs.filter(key__number_of_accidentals=i, key__accidentals='f').values('key__name', 'key__accidentals').annotate(frequency=Count('key__name')):
        keysig.append(x['frequency'])

    data.append(keysig)

for i, keysig in enumerate(data):
    if i > 0:
        plt.bar(np.arange(len(keysig)), keysig, bottom=data[i - 1])
    else:
        plt.bar(np.arange(len(keysig)), keysig)


plt.show()
