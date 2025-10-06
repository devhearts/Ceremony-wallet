from rest_framework import serializers
from .models import Event, BudgetItem

class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['item_name', 'cost', 'is_funded']

class EventSerializer(serializers.ModelSerializer):
    budget_items = BudgetItemSerializer(many=True, read_only=True)
    total_raised = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['total_raised', 'created_at']