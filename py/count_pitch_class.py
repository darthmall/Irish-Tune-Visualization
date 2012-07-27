#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from tune_viz.models import *
import music21

jigs = Tune.objects.exclude(rhythm='jig').exclude(pitches__isnull=False)[:1000]
total = jigs.count()

for i, t in enumerate(jigs):
    try:
        score = music21.converter.parseData(t.raw_abc)
        pitches = {}

        try:
            print(u'{: >7,d} / {: <7,d} {}'.format(i+1, total, t.title))
        except:
            print(u'{: >7,d} / {: <7,d}'.format(i+1, total))

        for n in score.flat.notes:
            if isinstance(n, music21.chord.Chord):
                for p in n.pitches:
                    pitches[p.name] = pitches.setdefault(p.name, 0) + 1
            else:
                pitches[n.pitch.name] = pitches.setdefault(n.pitch.name, 0) + 1

        for name, count in pitches.iteritems():
            pitch_class, created = PitchClass.objects.get_or_create(tune=t, pitch=name)
            pitch_class.count = count
            pitch_class.save()
    except:
        print(u'{: >7,d} / {: <7,d} Error parsing "{}"'.format(i+1, total, t.title))

print (u'{:,d} tunes remaining'.format(Tune.objects.exclude(pitches__isnull=False).count()))
