from django.db import models


class Tune(models.Model):
    reference = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, blank=True, null=False)
    unit_note_length = models.CharField(max_length=255, blank=True, null=False)
    key = models.CharField(max_length=8, blank=True, null=False)
    meter = models.CharField(max_length=255, blank=True, null=False)
    origin = models.CharField(max_length=255, blank=True, null=False)
    tempo = models.CharField(max_length=255, blank=True, null=False)
    rhythm = models.CharField(max_length=255, blank=True, null=False)
    raw_abc = models.TextField(blank=False, null=False)
    source = models.CharField(max_length=255, blank=False, null=False, default="thessions.org")

    created_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.raw_abc

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
    text = models.TextField(blank=False, null=False, unique=True)
    musicxml = models.TextField(blank=False, null=False, unique=True)
    count = models.IntegerField(blank=False, null=False, default=0)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

