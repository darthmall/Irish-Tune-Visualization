#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from django.db.models import Count
from tune_viz.models import *
import re

modes = [None, 'Dor', 'Phr', 'Lyd', 'Mix', 'm', 'Loc']
keyname = re.compile(r'[A-G][#b]?(\w+)?')

for k in Key.objects.all():
    m = re.match(keyname, k.name)

    k.degree = modes.index(m.group(1)) + 1
    k.save()
