from twilio.rest import Client

def send_test_sms():
    account_sid = 'your_actual_account_sid'
    auth_token = 'your_actual_auth_token'
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body="This is a test message from Twilio!",
            from_='+your_twilio_number',
            to='+user_phone_number'
        )
        print(f"Sent test message: {message.sid}")
    except Exception as e:
        print(f"Failed to send test SMS: {e}")

send_test_sms()
