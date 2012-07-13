#!/usr/bin/env python
import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from tune_viz.models import *
import music21

m17 = music21.features.jSymbolic.getExtractorByTypeAndNumber('M', 17)
m18 = music21.features.jSymbolic.getExtractorByTypeAndNumber('M', 18)
m19 = music21.features.jSymbolic.getExtractorByTypeAndNumber('M', 19)
p8 = music21.features.jSymbolic.getExtractorByTypeAndNumber('P', 8)

tunes = Tune.objects.filter(rhythm='reel', pitch_variety__isnull=True)[:500]
total = tunes.count()

status = '{: >7,d} / {: <7,d} {}'

for i, tune in enumerate(tunes):
    try:
        score = music21.converter.parseData(tune.raw_abc, format='abc')
        print(status.format(i + 1, total, tune.id))

        # try:
        #     tune.melodicDirection = m17(score).extract().vector[0]
        # except:
        #     print('Unable to calculate melodic direction for {}'.format(tune.id))

        # try:
        #     tune.melodicArcDuration = m18(score).extract().vector[0]
        # except:
        #     print('unable to calculate arc duration for {}'.format(tune.id))

        # try:
        #     tune.melodicArcSize = m19(score).extract().vector[0]
        # except:
        #     print('Unable to calculate arc size for {}'.format(tune.id))

        try:
            tune.pitch_variety = p8(score).extract().vector[0]
        except:
            print('Unable to calculate pitch variety for {}'.format(tune.id))

        tune.save()
    except:
        print(status.format(i + 1, total, '{} (Error)'.format(tune.id)))

print('Done. {} tunes remaining.'.format(Tune.objects.filter(rhythm='reel', pitch_variety__isnull=True).count()))
