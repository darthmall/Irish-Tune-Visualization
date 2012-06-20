#!/usr/bin/env python

import sys
sys.path.append('..')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tune_viz.settings')

from tune_viz.models import Key

sharps = (
    ('C', 'Am', 'GMix', 'DDor', 'EPhr', 'FLyd', 'BLoc'),
    ('G', 'Em', 'DMix', 'ADor', 'BPhr', 'CLyd', 'F#Loc'),
    ('D', 'Bm', 'AMix', 'EDor', 'F#Phr', 'GLyd', 'C#Loc'),
    ('A', 'F#m', 'EMix', 'BDor', 'C#Phr', 'DLyd', 'G#Loc'),
    ('E', 'C#m', 'BMix', 'F#Dor', 'G#Phr', 'ALyd', 'D#Loc'),
    ('B', 'G#m', 'F#Mix', 'C#Dor', 'D#Phr', 'ELyd', 'A#Loc'),
    ('F#', 'D#m', 'C#Mix', 'G#Dor', 'A#Phr', 'BLyd', 'E#Loc'),
    ('C#', 'A#m', 'G#Mix', 'D#Dor', 'E#Phr', 'F#Lyd', 'B#Loc'))

flats = (
    ('F', 'Dm', 'CMix', 'GDor', 'APhr', 'BbLyd', 'ELoc'),
    ('Bb', 'Gm', 'FMix', 'CDor', 'DPhr', 'EbLyd', 'ALoc'),
    ('Eb', 'Cm', 'BbMix', 'FDor', 'GPhr', 'AbLyd', 'DLoc'),
    ('Ab', 'Fm', 'EbMix', 'BbDor', 'CPhr', 'DbLyd', 'GLoc'),
    ('Db', 'Bbm', 'AbMix', 'EbDor', 'FPhr', 'GbLyd', 'CLoc'),
    ('Gb', 'Ebm', 'DbMix', 'AbDor', 'BbPhr', 'CbLyd', 'Floc'),
    ('Cb', 'Abm', 'GbMix', 'DbDor', 'EbPhr', 'FbLyd', 'BbLoc'))

for i, keys in enumerate(sharps):
    for keyname in keys:
        k = Key(name=keyname, number_of_accidentals=i)
        k.save()

for i, keys in enumerate(flats):
    for keyname in keys:
        k = Key(name=keyname, accidentals='f', number_of_accidentals=i + 1)
        k.save()
