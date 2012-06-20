#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from django.db.models import Sum, Count
from tune_viz.models import *
import music21

def probability():
    aggregates = Measure.objects.all().aggregate(Sum('frequency'), Count('id'))
    total_measures = aggregates['id__count']

    for i, measure in enumerate(Measure.objects.all()):
        logmsg = '{: >7,d} / {:,d}'.format(i + 1, total_measures)
        measure.probability = float(measure.frequency) / total_measures
        logmsg += " p = {}".format(measure.probability)
        print(logmsg)
        measure.save()

def key(batchsize):
    measures = Measure.objects.filter(chord='')
    total_measures = min(batchsize, measures.count())

    measures = measures[:total_measures]

    for i, measure in enumerate(measures):
        logmsg = '{: >7,d} / {: <7,d}'.format(i + 1, total_measures)

        try:
            score = music21.converter.parseData(u'L: 1/8\n{}'.format(measure.text), format='abc')
            measure.chord = score.analyze('key')
            logmsg += " {}".format(measure.chord)
        except music21.analysis.discrete.DiscreteAnalysisException:
            measure.chord = 'x'
            logmsg += " failed to determine key"

        measure.save()
        print(logmsg)


if __name__ == '__main__':
    parser = ArgumentParser('Analysis of measures in the database')
    parser.add_argument('-k', '--key', action='store_true', dest='calculate_key',
        help='Calculate the key for each measure in the database')
    parser.add_argument('-p', '--probability', action='store_true', dest='probability',
        help='Calculate the probabibility based on frequency counts of measures in the database')
    parser.add_argument('-r', '--reset', action='store_true', dest='reset',
        help='Reset the probabilities in the database')
    parser.add_argument('-s', '--batchsize', type=int, default=1000, dest='batchsize')
    args = parser.parse_args()

    if args.reset:
        total_measures = Measure.objects.all().count()

        for i, measure in enumerate(Measure.objects.all()):
            print('{: >7,d} / {:,d} reset'.format(i + 1, total_measures))
            measure.probability = 0
            measure.save()

    if args.calculate_key:
        key(args.batchsize)
        print('{:,d} measures still missing keys'.format(Measure.objects.filter(chord='').count()))

    if args.probability:
        probability()

    print('Done.')
