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


def update_measure(measure_text, frequencies):
    m, created = Measure.objects.get_or_create(text=measure_text)
    frequencies[m.id] = frequencies.setdefault(m.id, 0) + 1

    return m
    

def main(key, rhythm, unit_note_length, normalize):
    tunes = Tune.objects.all()

    # Filter based on the unit note length
    if unit_note_length:
        tunes = tunes.filter(unit_note_length=unit_note_length)

    # Filter by key
    if key:
        tunes = tunes.filter(key=key)

    # Filter by rhythm
    if rhythm:
        tunes = tunes.filter(rhythm=rhythm)

    total_tunes = tunes.count()
    frequencies = {}
    bigrams = {}

    for i, tune in enumerate(tunes):
        try:
            print(u'{: >7,d} / {: <7,d} {}'.format(i + 1, total_tunes, tune.title))

            measure_list = map(lambda x: x.strip('|:'), tune.notation.split('|'))

            for prev, current in iter_bigrams(measure_list):
                measure = None
                prev_measure = None
                bigram_key = [None, None]

                if prev and current:
                    prev_measure = update_measure(prev, frequencies)
                    measure = update_measure(current, frequencies)

                    bigram_key[0] = prev_measure.id
                    bigram_key[1] = measure.id

                bigram_key = tuple(bigram_key)
                bigrams[bigram_key] = bigrams.setdefault(bigram_key, 0) + 1

        except:
            print('Unexpected error: {}'.format(sys.exc_info()[0]))
            raise

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
    parser.add_argument('-l', '--length', default='1/8', type=str, dest='length', help='Unit note length')
    parser.add_argument('--normalize', action='store_true', dest='normalize')
    args = parser.parse_args()

    main(args.key, args.rhythm, args.length, args.normalize)
