from django.db import models


class Document(models.Model):
    summary = models.CharField(max_length=254)
    text = models.TextField()

    date = models.DateField()
    added_time = models.DateTimeField()

    number = models.IntegerField()

    float = models.FloatField()

    bool = models.BooleanField(default=False)

    unicode = models.CharField(max_length=254)

    slash = models.CharField(max_length=20)
