from django.db import models


class MainType(models.Model):
    name = models.CharField(max_length=200)


class Type(models.Model):
    name = models.CharField(max_length=200)
    type = models.ForeignKey(MainType)
    date = models.DateField()


class Document(models.Model):
    text = models.TextField()
    type = models.ForeignKey(Type)
