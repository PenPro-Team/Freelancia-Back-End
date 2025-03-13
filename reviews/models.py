from django.db import models
from freelancia_back_end.models import User, Project
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Review(models.Model):
    message=models.CharField(max_length=400)
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    user_reviewr= models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    user_reviewed= models.ForeignKey(User, on_delete=models.CASCADE, related_name='other_reviews')
    project= models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_reviewr' , 'user_reviewed' , 'project')

    def __str__(self):
        return f'{self.user_reviewr.username} - {self.user_reviewed.username} - {self.project.project_name}'
    
