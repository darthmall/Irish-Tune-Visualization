#!/usr/bin/env python
import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from music21 import converter
from progress_bar import ProgressBar
from tune_viz.models import *
import csv

parser = ArgumentParser(description="Convert notes in tunes to CSV")
parser.add_argument('output', metavar='FILE', type=str)

args = parser.parse_args()

tunes = Tune.objects.filter(rhythm='jig', key__accidentals='s', key__number_of_accidentals=2)

progress = ProgressBar(tunes.count())
progress.width = 80


with file(args.output, 'wb') as output:
    writer = csv.writer(output)

    for i, tune in enumerate(tunes.values('id', 'raw_abc')):
        progress.update_time(i)
        print progress, chr(27) + '[A'

        try:
            score = converter.parseData(tune['raw_abc'], format='abc')
            row = [tune['id']]

            for note in score.flat.notesAndRests:
                duration = note.quarterLength
                ps = 0

                if note.isNote:
                    ps = note.ps

                row.append('|'.join(map(str, (duration, ps))))
        except:
            pass
        finally:
            writer.writerow(row)

progress.update_time(i + 1)
print progress