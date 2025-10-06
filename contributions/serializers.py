from rest_framework import serializers
from .models import Contribution

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = '__all__'
        read_only_fields = ['platform_fee', 'net_amount', 'status', 'created_at']