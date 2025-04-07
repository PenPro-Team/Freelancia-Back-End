from django.db import models

from freelancia_back_end.models import User
from contract.models import Contract


from django.utils import timezone


class BaseReport(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        REVIEWED = 'reviewed', 'Reviewed'
        RESOLVED = 'resolved', 'Resolved'
        IGNORED = 'ignored', 'Ignored'

    class ResolutionReason(models.TextChoices):
        VIOLATION_FOUND = 'violation', 'Terms violation found'
        NO_VIOLATION = 'no_violation', 'No violation found'
        FALSE_REPORT = 'false', 'False report'
        OTHER = 'other', 'Other reason'

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    resolved_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Details about how this report was resolved"
    )
    resolution_reason = models.CharField(
        max_length=20,
        choices=ResolutionReason.choices,
        blank=True,
        null=True
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='%(class)s_resolved',
        blank=True,
        null=True,
        verbose_name="Resolved by"
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.status in [self.StatusChoices.RESOLVED, self.StatusChoices.IGNORED] and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)


class ReportUser(BaseReport):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='user_reports_received',
        verbose_name="Reported User"
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reports_made_on_users',
        verbose_name="Reporting User"
    )

    class Meta(BaseReport.Meta):
        verbose_name = 'User Report'
        verbose_name_plural = 'User Reports'

    def __str__(self):
        return f"User Report #{self.id}: {self.reporter.username} > {self.user.username}"


class ReportContract(BaseReport):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.PROTECT,
        related_name='contract_reports_received',
        verbose_name="Reported Contract"
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reports_made_on_contracts',
        verbose_name="Reporting User"
    )

    class Meta(BaseReport.Meta):
        verbose_name = 'Contract Report'
        verbose_name_plural = 'Contract Reports'

    def __str__(self):
        return f"Contract Report #{self.id}: {self.reporter.username} > {self.contract}"
