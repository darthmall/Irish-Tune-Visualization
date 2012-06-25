from django.db import models


class Tune(models.Model):
    reference = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, blank=True)
    unit_note_length = models.CharField(max_length=255, blank=True)
    keyname = models.CharField(max_length=8, blank=True)
    key = models.ForeignKey('Key', blank=True, null=True)
    meter = models.CharField(max_length=255, blank=True)
    origin = models.CharField(max_length=255, blank=True)
    tempo = models.CharField(max_length=255, blank=True)
    rhythm = models.CharField(max_length=255, blank=True)
    raw_abc = models.TextField(blank=False, null=False)
    notation = models.CharField(max_length=1024, blank=True)
    source = models.CharField(max_length=255, blank=False, null=False, default="thessions.org")

    created_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.raw_abc

class Key(models.Model):
    ACCIDENTALS = (('s', 'sharps'), ('f', 'flats'))

    name = models.CharField(max_length=8)
    accidentals = models.CharField(max_length=1, choices=ACCIDENTALS, default='s')
    number_of_accidentals = models.IntegerField(default=0)
    degree = models.IntegerField(null=True, blank=True)

class PitchClass(models.Model):
    tune = models.ForeignKey('Tune', related_name='pitches')
    pitch = models.CharField(max_length=32)
    degree = models.IntegerField()
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('tune', 'pitch')

class Metadata(models.Model):
    tune = models.ForeignKey("Tune")
    tag =  models.CharField(max_length=1)
    data = models.CharField(max_length=1024)

class TuneDistance(models.Model):
    source = models.ForeignKey('Tune', related_name='source_distance')
    target = models.ForeignKey('Tune', related_name='target_distance')
    levenshtein_distance = models.IntegerField()
    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('source', 'target')

class Measure(models.Model):
    text = models.TextField(unique=True)
    musicxml = models.TextField(blank=True, default='')
    frequency = models.IntegerField(default=0)
    probability = models.FloatField(default=0.0)
    chord = models.CharField(max_length=64, blank=True)
    normalized = models.BooleanField(default=False)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

class MeasureBigram(models.Model):
    measure = models.ForeignKey('Measure', related_name='bigrams', blank=True, null=True)
    previous = models.ForeignKey('Measure', related_name='precursor_bigram', blank=True, null=True)
    frequency = models.IntegerField(default=0)
    probability = models.FloatField(default=0.0)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)
