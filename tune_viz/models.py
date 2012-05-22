from django.db import models


class Tune(models.Model):
    # ABC fields
    reference = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, blank=True, null=False)
    origin = models.CharField(max_length=255, blank=True, null=False)
    meter = models.CharField(max_length=255, blank=True, null=False)
    unit_note_length = models.CharField(max_length=255, blank=True, null=False)
    tempo = models.CharField(max_length=255, blank=True, null=False)
    transcription = models.ForeignKey('Transcriptionist', blank=True, null=True)
    notes = models.TextField(blank=True, null=False)
    group = models.CharField(max_length=255, blank=True, null=False)
    history = models.TextField(blank=True, null=False)
    key = models.CharField(max_length=8, blank=True, null=False)
    rhythm = models.CharField(max_length=255, blank=True, null=False)
    instructions = models.CharField(max_length=255, blank=True, null=False)
    body = models.TextField(blank=False, null=False)

    # Maintenance fields
    source = models.URLField()
    created_dt = models.DateTimeField(auto_now_add=True)

class Transcriptionist(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, blank=True, null=False)
    created_dt = models.DateTimeField(auto_now_add=True)

class TuneDistance(models.Model):
    lhs = models.OneToOneField('Tune', related_name='lhs_distance')
    rhs = models.OneToOneField('Tune', related_name='rhs_distance')
    distance = models.IntegerField()
    created_dt = models.DateTimeField(auto_now_add=True)
