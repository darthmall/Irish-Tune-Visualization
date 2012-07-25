#!/usr/bin/env python
import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from music21.converter import parseData
from progress_bar import ProgressBar
from tune_viz.models import *

parser = ArgumentParser(description='Calculate variability positionally across tunes')
parser.add_argument('-a', '--accidentals', dest='accidentals', type=int, default=2)
parser.add_argument('-t', '--type', dest='type', type=str, default='jig')
parser.add_argument('-l', '--limit', dest='limit', type=int, default=100)
args = parser.parse_args()

tunes = Tune.objects.filter(rhythm=args.type, key__accidentals='s', key__number_of_accidentals=args.accidentals)[:args.limit]
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

            offset = (note.offset, degree)
            beat = (note.beat, degree)

            byOffset[offset] = byOffset.get(offset, 0) + 1
            byBeat[beat] = byBeat.get(beat, 0) + 1
    except:
        errors += 1
        raise

print 'By Offset'
for k, v in byOffset.iteritems():
    print k, v

print 'By Beat'
for k, v in byBeat.iteritems():
    print k, v
