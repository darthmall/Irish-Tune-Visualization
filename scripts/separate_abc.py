#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from argparse import ArgumentParser
from tune_viz.models import *
import re

# Used to identify ABC header fields
ABC_HEADER = re.compile(r'^[XTCOAMLQPZNGHKRBDFSImrsUVWw]:')

    
def main(key, rhythm):
    tunes = Tune.objects.all()

    # Filter by key
    if key:
        tunes = tunes.filter(key=key)

    # Filter by rhythm
    if rhythm:
        tunes = tunes.filter(rhythm=rhythm)

    total_tunes = tunes.count()
    
    for i, tune in enumerate(tunes):
        print(u'{: >7,d} / {: <7,d} {}'.format(i+1, total_tunes, tune.title))
        lines = []

        for line in tune.raw_abc.split('\n'):
            if not ABC_HEADER.match(line):
                lines.append(line.strip())

        tune.notation = ''.join(lines)
        tune.save()


if __name__ == '__main__':
    parser = ArgumentParser('Calculate bigrams of measures for a subset of Irish tunes')
    parser.add_argument('-k', '--key', default=None, type=str, dest='key')
    parser.add_argument('-r', '--rhythm', default=None, type=str, dest='rhythm')
    args = parser.parse_args()

    main(args.key, args.rhythm)
