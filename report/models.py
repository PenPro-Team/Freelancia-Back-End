from django.db import models

from freelancia_back_end.models import User


class ReportUser(models.Model):
    class StatusChoices(models.TextChoices):
        pending = 'pending'
        reviewed = 'reviewed'
        resolved = 'resolved'
        ignored = 'ignored'

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports_received', verbose_name="Reported User")
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports_made', verbose_name="Reporting User")
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.pending)

    class Meta:
        verbose_name = 'ReportUser'
        verbose_name_plural = 'ReportUsers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reporter.username} > {self.user.username} : {self.title}"
