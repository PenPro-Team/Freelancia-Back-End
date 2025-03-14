from django.db import models
from freelancia_back_end.models import User, Project
 

# Create your models here.


class Contract(models.Model):
    class StatusChoices(models.TextChoices):
        pending = 'pending'
        aproved = 'aproved'
        canceled = 'canceled'
    contract_terms = models.TextField()
    dedline=models.PositiveIntegerField( default=0)
    budget=models.PositiveIntegerField( default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    freelancer= models.ForeignKey(User, on_delete=models.CASCADE, related_name='freelancer')
    client= models.ForeignKey(User, on_delete=models.CASCADE, related_name='client')
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    contract_state = models.CharField(max_length=20,choices= StatusChoices.choices ,default='pending')



    class Meta:
        unique_together = ('freelancer', 'client', 'project')

    def __str__(self):
        return f'{self.client} contract with {self.freelancer} to do {self.project}'
