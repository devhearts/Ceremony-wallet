from django.db import models
from events.models import Event

class Contribution(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='contributions')
    contributor_name = models.CharField(max_length=100, default='Anonymous')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid/Confirmed'),
        ('PLEDGED', 'Pledged - Awaiting Payment'),
        ('FAILED', 'Payment Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    is_anonymous = models.BooleanField(default=False)
    
    # Financial Fields
    FEE_RATE = 0.025 # 2.5% fee
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate fees before saving
        self.platform_fee = self.amount * self.FEE_RATE
        self.net_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)