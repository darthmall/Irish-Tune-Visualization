#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from tune_viz.models import *
import music21

def iter_bigrams(iterable):
    i = iter(iterable)
    prev = None
    current = None

    try:
        while True:
            prev = current
            current = i.next()
            yield (prev, current)
    except StopIteration:
        current = None    

    yield (prev, current)


def update_measure(measure, frequencies):
    m = None
    text = measure._reprTextLine()

    if Measure.objects.filter(text=text).count() > 0:
        m = Measure.objects.get(text=text)
    else:
        m = Measure(text=text, musicxml=measure.musicxml)
        m.save()

    frequencies[m.id] = frequencies.setdefault(m.id, 0) + 1

    return m
    

def main(key, rhythm, normalize):
    tunes = Tune.objects.all()

    # Filter by key
    if key:
        tunes = tunes.filter(key=key)

    # Filter by rhythm
    if rhythm:
        tunes = tunes.filter(rhythm=rhythm)

    total_tunes = tunes.count()
    frequencies = {}
    bigrams = {}

    # Every tune has a start and end, so add double the number of tunes to the
    # frequency count of the null measure to twice the number of tunes
    null_measure, created = Measure.objects.get_or_create(text='')
    null_measure.frequency += 2 * total_tunes
    null_measure.save()

    for i, tune_obj in enumerate(tunes):
        try:
            jig = music21.converter.parseData(tune_obj.raw_abc, format='abc')

            print(u'{: >7,d} / {: <7,d} {}'.format(i + 1, total_tunes, jig.metadata.title))

            measure_list = jig.measureOffsetMap().values()
            measure_list.sort(cmp=lambda x, y: cmp(x[0].offset, y[0].offset))

            for i, (prev, current) in enumerate(iter_bigrams(measure_list)):
                measure = None
                prev_measure = None
                bigram_key = [None, None]

                if current:
                    measure = update_measure(current[0], frequencies)
                    bigram_key[1] = measure.id

                    tune_measure = TuneMeasure(tune=tune_obj, measure=measure, position=i)
                    tune_measure.save()

                if prev:
                    prev_measure = update_measure(prev[0], frequencies)
                    bigram_key[0] = prev_measure.id

                bigram_key = tuple(bigram_key)
                bigrams[bigram_key] = bigrams.setdefault(bigram_key, 0) + 1

        except:
            print('Unexpected error: {}'.format(sys.exc_info()[0]))

    for measure_id, count in frequencies.iteritems():
        m = Measure.objects.get(id=measure_id)
        m.frequency = count
        m.save()

    for bigram_key, count in bigrams.iteritems():
        measure = None
        previous = None

        if bigram_key[1]:
            measure = Measure.objects.get(id=bigram_key[1])
        if bigram_key[0]:
            previous = Measure.objects.get(id=bigram_key[0])

        bigram, created = MeasureBigram.objects.get_or_create(measure=measure, previous=previous)
        bigram.frequency = count
        bigram.save()


if __name__ == '__main__':
    parser = ArgumentParser('Calculate bigrams of measures for a subset of Irish tunes')
    parser.add_argument('-k', '--key', default=None, type=str, dest='key')
    parser.add_argument('-r', '--rhythm', default=None, type=str, dest='rhythm')
    parser.add_argument('--normalize', action='store_true', dest='normalize')
    args = parser.parse_args()

    main(args.key, args.rhythm, args.normalize)
