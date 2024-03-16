from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    subjects = models.CharField(max_length=255)
    bookshelves = models.CharField(max_length=255)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        return self.title