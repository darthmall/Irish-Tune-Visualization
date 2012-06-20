#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from music21 import *
from tune_viz.models import *
import itertools, numpy


def distance(s, t):
    '''Return the Levenshtein distance between s and t.'''

    d = numpy.zeros((len(s) + 1, len(t) + 1))

    for i in range(1, len(s) + 1):
        d[i, 0] = i;

    for i in range(1, len(t) + 1):
        d[0, i] = i;

    for j in range(1, len(t) + 1):
        for i in range(1, len(s) + 1):
            if s[i-1] == t[j-1]:
                d[i, j] = d[i - 1, j - 1]
            else:
                d[i, j] = min(
                    d[i - 1, j] + 1,
                    d[i, j - 1] + 1,
                    d[i - 1, j - 1] + 1)

    return d


def main():
    parser = ArgumentParser('Calculate the Levenshtein distance between pairs of tunes')
    parser.add_argument('-k', '--key', default=None, type=str, dest='key')
    parser.add_argument('-r', '--rhythm', default=None, type=str, dest='rhythm')
    args = parser.parse_args()

    tunes = Tune.objects.all()
    if args.key:
        tunes = tunes.filter(key=args.key)

    if args.rhythm:
        tunes = tunes.filter(rhythm=args.rhythm)

    for (s, t) in itertools.combinations(tunes, 2):
        print(u'{} ({}) => {} ({})'.format(s.title, s.id, t.title, t.id))
        if TuneDistance.objects.filter(source=s, target=t).count() < 1:
            l = distance(
                    converter.parseData(s.raw_abc, format='abc').flat.notesAndRests,
                    converter.parseData(t.raw_abc, format='abc').flat.notesAndRests
                )

            tune_distance = TuneDistance(source=s, target=t, levenshtein_distance=int(l[-1, -1]))
            tune_distance.save()
            print('  distance: {}'.format(tune_distance.levenshtein_distance))
        else:
            print('  skipped')

if __name__ == '__main__':
    main()