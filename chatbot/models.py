from django.db import models
from django.conf import settings 

class Feedback(models.Model):
    """Stores user feedback for chatbot responses."""
    RATING_CHOICES = [
        (1, 'Positive'),
        (-1, 'Negative'),
    ]

    question = models.TextField()
    response = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True 
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True) 

    def __str__(self):
        rating_display = dict(self.RATING_CHOICES).get(self.rating, 'Unknown')
        user_info = f" by {self.user.username}" if self.user else " by Anonymous"
        return f"Feedback for '{self.question[:30]}...': {rating_display}{user_info} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at'] 