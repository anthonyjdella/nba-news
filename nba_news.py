import requests
import os

from datetime import date
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

today = date.today()

url_news_today = f'https://api.sportsdata.io/v3/nba/scores/json/NewsByDate/{today}'
url_news_all = f'https://api.sportsdata.io/v3/nba/scores/json/News'

params = {
	'key': os.getenv('SPORTSDATA_API_KEY')
}


def get_news(date=None):
	if date == 'today':
		response = requests.get(url_news_today, params=params)
	else:
		response = requests.get(url_news_all, params=params)
	return response.json()


def check_transactions(response, target_category):
	for news in response:
		if target_category in news['Categories']:
			return True
	return False

def print_transactions(response, target_category):
	output = ''
	for news in response:
		if target_category in news['Categories']:
			output += f"Title: {news['Title']}\n"
			output += f"Date: {news['TimeAgo']}\n"
			# output += f"Story: {news['Content']}\n"
			output += '----------------------------------------\n'
	return output


def get_transactions(date=None):
	target_category = 'Top-Headlines'

	if date and 'f5' in date.lower():
		response = get_news('today')
		if not check_transactions(response, target_category):
			return('No transactions today, keep F5ing')
	else:
		response = get_news()
	return print_transactions(response, target_category)


def send_text(option=None):
	account_sid = os.getenv('TWILIO_ACCOUNT_SID')
	auth_token = os.getenv('TWILIO_AUTH_TOKEN')
	client = Client(account_sid, auth_token)

	message = client.messages.create(
		body=get_transactions(option),
		from_=os.environ['MY_TWILIO_NUMBER'],
		to=os.environ['ANTHONYS_NUMBER']
	)
	print(message.body)
