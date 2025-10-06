from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
from contributions.models import Contribution
from contributions.serializers import ContributionSerializer
from contributions.utils import initiate_mobile_money_payment, send_whatsapp_update, mock_webhook_success # Import the mock success for demo

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """
        API endpoint for guests to contribute or pledge.
        """
        try:
            event = self.get_object()
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['event'] = pk
        
        is_pledge = data.pop('is_pledge', False)

        # 1. Handle Pledges
        if is_pledge:
            data['status'] = 'PLEDGED'
            serializer = ContributionSerializer(data=data)
            if serializer.is_valid():
                contribution = serializer.save()
                return Response(
                    {"message": "Pledge successfully recorded! Thank you.", "id": contribution.id}, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2. Handle Direct Payment
        data['status'] = 'PENDING'
        serializer = ContributionSerializer(data=data)
        
        if serializer.is_valid():
            contribution = serializer.save()
            transaction_ref = f"CW-{contribution.id}"
            
            # Initiate Mobile Money PUSH Request (MOCKED)
            success, message = initiate_mobile_money_payment(
                amount=contribution.amount,
                phone_number=contribution.mobile_number,
                transaction_ref=transaction_ref
            )

            if success:
                # MOCKING: Simulate the webhook hitting us 1 second later
                # In production, this would be a separate, external request.
                mock_webhook_success(transaction_ref) 
                
                return Response(
                    {"message": "Payment request sent to your phone. Please approve the Mobile Money PIN prompt.", "id": contribution.id}, 
                    status=status.HTTP_202_ACCEPTED
                )
            else:
                contribution.status = 'FAILED'
                contribution.save()
                return Response({"error": f"Payment initiation failed: {message}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)