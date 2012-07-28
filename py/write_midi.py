#!/usr/bin/env python

from argparse import ArgumentParser
from progress_bar import ProgressBar
from music21 import converter
import sqlite3

parser = ArgumentParser(description="Create MIDI files from ABC data")
parser.add_argument('-a', '--accidentals', dest='accidentals', type=int, default=2)
parser.add_argument('-t', '--type', dest='type', type=str, default='jig')
parser.add_argument('db', metavar='DATABASE', type=str)

args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()

c.execute('SELECT count(tune.id) FROM tune JOIN key ON (key.id = tune.key_id) WHERE tune.rhythm="jig" AND key.accidentals="s" AND key.number_of_accidentals=2')
(tune_count,) = c.fetchone()

progress = ProgressBar(tune_count)
progress.width = 80

for i, (tuneId, abc) in enumerate(c.execute('SELECT tune.id, tune.raw_abc FROM tune JOIN key ON (key.id = tune.key_id) WHERE tune.rhythm="jig" AND key.accidentals="s" AND key.number_of_accidentals=2')):
    progress.update_time(i)
    print progress, chr(27) + '[A'

    try:
        score = converter.parseData(abc, format='abc')
        score.write('midi', 'midi/{}.mid'.format(tuneId))
    except:
        pass
