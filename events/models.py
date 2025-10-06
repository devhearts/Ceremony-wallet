from django.db import models
from contributions.models import Contribution

class Event(models.Model):
    name = models.CharField(max_length=255)
    organizer = models.CharField(max_length=100) # Placeholder for simple organizer
    budget_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def total_raised(self):
        # Only count PAID contributions
        return Contribution.objects.filter(event=self, status='PAID').aggregate(models.Sum('net_amount'))['net_amount__sum'] or 0.00

    def __str__(self):
        return self.name

class BudgetItem(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budget_items')
    item_name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_funded = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.item_name} for {self.event.name}"