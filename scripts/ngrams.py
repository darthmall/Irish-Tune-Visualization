#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from tune_viz.models import *
import music21


def main(key, rhythm):
    unique_measure_count = 0
    measure_count = 0
    tunes = Tune.objects.all()

    if key:
        tunes = tunes.filter(key=key)

    if rhythm:
        tunes = tunes.filter(rhythm=rhythm)

    total_tunes = tunes.count()
    frequencies = {}

    for i, abc in enumerate(tunes.values_list('raw_abc', flat=True)):
        try:
            jig = music21.converter.parseData(abc, format='abc')

            print(u'{} / {} {}'.format(i, total_tunes, jig.metadata.title))

            for measures in jig.measureOffsetMap().itervalues():
                for measure in measures:
                    measure_count += 1
                    text = measure._reprTextLine()

                    m = None
                    if Measure.objects.filter(text=text).count() > 0:
                        m = Measure.objects.get(text=text)
                    else:
                        unique_measure_count += 1
                        m = Measure(text=text, musicxml=measure.musicxml)
                        m.save()

                    frequencies[m.id] = frequencies.setdefault(m.id, 0) + 1
        except:
            print('Unexpected error: {}'.format(sys.exc_info()[0]))

    for measure_id, count in frequencies.iteritems():
        m = Measure.objects.get(id=measure_id)
        m.count = count
        m.save()

    print('\n{} distinct measures from {} total measures'.format(unique_measure_count, measure_count))


if __name__ == '__main__':
    parser = ArgumentParser('Calculate bigrams of measures for a subset of Irish tunes')
    parser.add_argument('-k', '--key', default=None, type=str, dest='key')
    parser.add_argument('-r', '--rhythm', default=None, type=str, dest='rhythm')
    args = parser.parse_args()

    main(args.key, args.rhythm)