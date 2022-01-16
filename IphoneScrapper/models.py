from django.db import models


# Create your models here.
class Phone(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    city = models.CharField(max_length=70)
    dateAnnonce = models.DateTimeField()
    origin = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + "   à " + self.city + "  le " + self.dateAnnonce.strftime("%m/%d/%Y à %H:%M:%S")
