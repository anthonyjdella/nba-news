from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from nba_news import get_transactions

app = Flask(__name__)


@app.route("/nba", methods=['GET', 'POST'])
def incoming_sms():
    user_input = request.values.get('Body', None)
    transactions = get_transactions(user_input)

    resp = MessagingResponse()
    resp.message(transactions)

    return str(resp)


if __name__ == "__main__":
    app.run(host='localhost', debug=True, port=8080)
