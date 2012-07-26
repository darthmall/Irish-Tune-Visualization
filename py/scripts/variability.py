#!/usr/bin/env python
import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from music21.converter import parseData
from progress_bar import ProgressBar
from tune_viz.models import *
import csv

parser = ArgumentParser(description='Calculate variability positionally across tunes')
parser.add_argument('-a', '--accidentals', dest='accidentals', type=int, default=2)
parser.add_argument('-t', '--type', dest='type', type=str, default='jig')
parser.add_argument('-l', '--limit', dest='limit', type=int, default=100)
args = parser.parse_args()

tunes = Tune.objects.filter(rhythm=args.type, key__accidentals='s', key__number_of_accidentals=args.accidentals)

if args.limit > 0:
    tunes = tunes[:args.limit]

tune_count = tunes.count()

progress = ProgressBar(tune_count)
progress.width = 60
errors = 0
print progress, '{: >5,d} / {: <5,d}'.format(0, tune_count), chr(27) + '[A'

byOffset = {}
byBeat = {}

for i, tune in enumerate(tunes.values_list('raw_abc', flat=True)):
    progress.update_time(i)
    print progress, '{: >5,d} / {: <5,d}'.format(i, tune_count), 'Errors: {}'.format(errors), chr(27) + '[A'

    try:
        score = parseData(tune, format='abc')
        key = score.analyze('key')

        for note in score.flat.notesAndRests:
            degree = -1

            if note.isNote:
                degree = key.getScaleDegreeFromPitch(note.pitch.name)

            byOffset.setdefault(note.offset, []).append(degree)
            byBeat.setdefault(note.beat, []).append(degree)
    except:
        errors += 1

print progress, '{: >5,d} / {: <5,d}'.format(i, tune_count), 'Errors: {}'.format(errors)

with file('variation.beat.csv', 'wb') as datafile:
    writer = csv.writer(datafile)

    for beat, degrees in byBeat.iteritems():
        writer.writerow([beat, len(set(degrees)), len(degrees)])

with file('variation.offset.csv', 'wb') as datafile:
    writer = csv.writer(datafile)

    for offset, degrees in byOffset.iteritems():
        writer.writerow([offset, len(set(degrees)), len(degrees)])
