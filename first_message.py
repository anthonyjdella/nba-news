# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages.create(
                              body='This is the best basketball player',
                              media_url='https://denver-tsl-4177.twil.io/the-joker.jpg',
                              from_=os.environ['MY_TWILIO_NUMBER'],
                              to=os.environ['ANTHONYS_NUMBER']
                          )

print(message.sid)
