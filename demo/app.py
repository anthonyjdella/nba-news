from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from nba_news import get_headlines

app = Flask(__name__)

@app.route('/nba', methods=['GET', 'POST'])
def incoming_sms():
    user_input = request.values.get('Body', None)
    headlines = get_headlines(user_input)

    resp = MessagingResponse()
    resp.message(headlines)

    return str(resp)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
