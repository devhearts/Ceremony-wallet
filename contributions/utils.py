import requests
# Placeholder for your actual Twilio/WhatsApp setup
# from twilio.rest import Client 

# --- PLACEHOLDER API KEYS/SECRETS ---
# NOTE: In a real app, these must be loaded from environment variables (.env)
MM_API_ENDPOINT = "http://mock-mobile-money-api.com/v1/transfer" 
WHATSAPP_API_KEY = "YOUR_TWILIO_ACCOUNT_SID"

# --- CORE FUNCTIONS ---

def initiate_mobile_money_payment(amount, phone_number, transaction_ref):
    """
    Mocks the initiation of a Mobile Money PUSH request.
    In a real app, this sends an HTTP request to a local payment gateway.
    """
    print(f"--- MOCK MM PUSH: Pushing {amount} to {phone_number} Ref: {transaction_ref} ---")
    
    # Mocking the actual network request
    # try:
    #     response = requests.post(
    #         MM_API_ENDPOINT,
    #         json={'amount': float(amount), 'phone': phone_number, 'ref': transaction_ref, 'callback_url': 'YOUR_WEBHOOK_URL'}
    #     )
    #     response.raise_for_status()
    #     return True, "Payment request initiated successfully."
    # except requests.RequestException as e:
    #     return False, f"Payment API failed: {e}"

    # For this skeleton, we assume successful initiation:
    return True, "Payment request initiated successfully."

def send_whatsapp_update(contribution, message_type='CONFIRMATION'):
    """Mocks sending a WhatsApp message via an external service."""
    # Real implementation uses the Twilio/WhatsApp API client
    
    event_name = contribution.event.name
    contributor = contribution.contributor_name if not contribution.is_anonymous else 'Anonymous'
    
    if message_type == 'CONFIRMATION' and contribution.status == 'PAID':
        organizer_msg = (
            f"🎉 New Contribution! UGX {contribution.net_amount:,.0f} received (Net) from {contributor} "
            f"for '{event_name}'. New Total: UGX {contribution.event.total_raised():,.0f}. [Link to Dashboard]"
        )
        contributor_msg = (
            f"✅ Success! Your UGX {contribution.amount:,.0f} contribution "
            f"to '{event_name}' is confirmed. Thank you! [Public Link]"
        )

        print(f"\n[WHATSAPP TO ORGANIZER]: {organizer_msg}")
        print(f"[WHATSAPP TO CONTRIBUTOR]: {contributor_msg}")

        # twilio_client.messages.create(...)

    elif message_type == 'REMINDER':
        # This is for scheduled Cron jobs, not the instant payment flow
        reminder_msg = (
            f"🔔 Gentle reminder: You pledged UGX {contribution.amount:,.0f} for '{event_name}'. "
            f"Click here to finalize payment: [Link]"
        )
        print(f"\n[WHATSAPP PLEDGE REMINDER]: {reminder_msg}")
        # twilio_client.messages.create(...)

# --- PAYMENT WEBHOOK (MOCK) ---
# The most crucial piece of the architecture.
from .models import Contribution
def mock_webhook_success(transaction_ref):
    """
    Mocks the Webhook handler that is called by the Mobile Money Gateway 
    when the guest enters their PIN and the transaction is successful.
    """
    try:
        # Extract ID from transaction_ref (e.g., 'CW-5')
        contribution_id = int(transaction_ref.split('-')[1]) 
        contribution = Contribution.objects.get(pk=contribution_id)

        if contribution.status == 'PENDING':
            contribution.status = 'PAID'
            contribution.save()
            
            # CRITICAL: Trigger the real-time update here
            send_whatsapp_update(contribution, 'CONFIRMATION')
            print(f"\n*** WEBHOOK SUCCESS: Contribution {contribution_id} marked as PAID. Updates sent. ***")
            return True
        return False
    except Contribution.DoesNotExist:
        print("ERROR: Contribution not found in mock webhook.")
        return False