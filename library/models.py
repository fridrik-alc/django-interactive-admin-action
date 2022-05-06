from django.db import models


class StatusChoices(models.IntegerChoices):
    available = 0
    on_loan = 1
    lost = 2


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey("Author", models.CASCADE)
    status = models.IntegerField(choices=StatusChoices.choices)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
