#!/usr/bin/env python

from argparse import ArgumentParser
from music21 import converter
from progress_bar import ProgressBar
import csv, sqlite3

TUNE_COUNT_SQL = '''SELECT count(tune.id)
    FROM tune
    JOIN key on (key.id = tune.key_id)
    WHERE tune.rhythm="jig"
        AND key.accidentals="s"
        AND key.number_of_accidentals=2
'''

TUNE_SQL = '''SELECT tune.id, tune.raw_abc
    FROM tune
    JOIN key on (key.id = tune.key_id)
    WHERE tune.rhythm="jig"
        AND key.accidentals="s"
        AND key.number_of_accidentals=2
'''

parser = ArgumentParser(description="Convert notes in tunes to CSV")
parser.add_argument('db', metavar='DATABASE', type=str)
parser.add_argument('output', metavar='CSVFILE', type=str)

args = parser.parse_args()

conn = sqlite3.connect(args.db)
c = conn.cursor()

c.execute(TUNE_COUNT_SQL)
tune_count = c.fetchone()[0]

progress = ProgressBar(tune_count)
progress.width = 80

with file(args.output, 'wb') as output:
    writer = csv.writer(output)

    for i, (tuneId, abc) in enumerate(c.execute(TUNE_SQL)):
        progress.update_time(i)
        print progress, chr(27) + '[A'

        try:
            score = converter.parseData(abc, format='abc')
            row = [tuneId]

            for note in score.flat.notesAndRests:
                duration = note.quarterLength
                ps = -1

                if note.isNote:
                    ps = note.ps

                row.append('|'.join(map(str, (duration, ps))))
        except:
            pass
        finally:
            writer.writerow(row)

progress.update_time(i + 1)
print progress