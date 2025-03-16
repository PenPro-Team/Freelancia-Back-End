from django.db import models

from freelancia_back_end.models import User

# Create your models here.

class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    main_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.title}"

class PortfolioImage(models.Model):
    id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE , related_name='images')
    image = models.ImageField()

    def __str__(self):
        return f"{self.portfolio.user} {self.portfolio.title}"