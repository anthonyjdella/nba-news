# Get The Latest NBA News Sent to Your Phone via SMS

In light of June 30th, 2022, the date when NBA teams can begin negotiations with free agents, now is an exciting time to be a basketball fan. We’ve already seen so much breaking news like Kevin Durant and Kyrie Irving [demanding trades](https://www.espn.com/nba/story/_/id/34174171/kevin-durant-requests-trade-brookyn-nets-sources-say), the Timberwolves giving away the farm for Rudy Golbert, and surely much more to come. 

I know many fans who are [F5ing](https://www.computerhope.com/jargon/f/f5.htm#:~:text=In%20all%20modern%20Internet%20browsers,contents%20of%20the%20page%20again.) their news feeds on their computers, so wouldn’t it be fun to do from your phone too? In this post, I’ll teach you how to write a Python application that texts you NBA news.


## Prerequisites

Before getting started, it’s important to have the following before moving on:

- [Python 3.6](https://www.python.org/downloads/) or higher installed on your machine.
- A Twilio account. If you haven’t yet, [sign up for a free Twilio trial](https://www.twilio.com/try-twilio).
- ngrok installed on your machine. ngrok is a useful tool for connecting your local server to a public URL. You can [sign up for a free account](https://ngrok.com/) and [learn how to install ngrok](https://ngrok.com/download).


## Background

Unfortunately, there is no official API provided by the NBA. Furthermore, ESPN has retired their public API as developers can [no longer generate an API key](http://www.espn.com/apis/devcenter/blog/read/publicretirement.html). But fear not, developers are crafty people, and there’s a solution! 

If you do some Google searching, you’ll see many independent third-party developers who have created their own (unofficial) NBA APIs as a workaround. But for this application, I’m going to be using an API from a company, called [SportsDataIO](https://sportsdata.io/company), which aggregates a bunch of sports data (not just NBA news) and allows developers to reach it via API calls.


## Architecture of an SMS NBA Update App

For context, this blog post is structured as follows:

1. Set Up

   1. Set up our local development environment

2. NBA News API

   1. Get NBA news data from the SportsDataIO API

3. Make an Outbound SMS

   1. Send a text message (containing NBA news)

4. Make an Inbound SMS

   1. Send a text message (containing NBA news) when the application is triggered


## Set Up

First thing we’ll do is create an empty project directory:

```bash
mkdir nba_app 
```

Then change into that directory, as that’s where our code will be.

```bash
cd nba_app
```

Create a [virtual environment](https://www.twilio.com/docs/usage/tutorials/how-to-set-up-your-python-and-flask-development-environment#start-a-new-project-with-virtualenv):

```bash
python -m venv nba
```

Activate our virtual environment:

```bash
source nba/bin/activate
```

Install dependencies to our virtual environment:

```bash
pip install python-dotenv twilio Flask requests
```

For us to get NBA data, we need to [register for a free account with SportsDataIO](https://sportsdata.io/user/register). After that, we’ll need an API key to authenticate our application with SportsDataIO. You can find this in your Account settings under Subscriptions. Copy your API key and don’t share it with anyone!

![](https://lh4.googleusercontent.com/CgZhxhGxUSaTTP-JAyzlPUbI9Tdbx5fPw1fGaAsZxRntPWPn-UGzHvfE-Na1FAWeLX0PIr7f07XNpTAlbL0zbz7n0RIyKDbcIVAFGs4YcqR59He9Tmntu_rN7sqOnn4xrQKuhF9Yh74KNq80tuPXNvc)

Let’s create a file called \`.env\` to store our API key in [environment variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html). 

Within that file, we’ll create an environment variable called SPORTSDATA_API_KEY. Replace PASTE_YOUR_API_KEY_HERE with the API key that you copied earlier.

```bash
SPORTSDATA_API_KEY=PASTE_YOUR_API_KEY_HERE
```

For example:
```bash
SPORTSDATA_API_KEY=f121212121212121212
```

Since we’ll also be working with our Twilio account, we’ll need to modify this file even more. Log into your [Twilio console](https://console.twilio.com/), then scroll down to find your Account SID and Auth Token. Add two additional lines to the .env file, but change the values to equal your unique Account SID and Auth Token.

```bash
TWILIO_ACCOUNT_SID=PASTE_YOUR_ACCOUNT_SID_HERETWILIO_AUTH_TOKEN=PASTE_YOUR_AUTH_TOKEN_HERE
```

 

For example:

```bash
TWILIO_ACCOUNT_SID=AC123123123123123123TWILIO_AUTH_TOKEN=321321321321321
```

If you’re pushing these to a Git repository, please make sure to add the .env file to your .gitignore so that these credentials are secured.


## NBA News API

Create a file called nba_news.py: this is where we will call the SportsDataIO NBA news API.

In its most basic form, we can get NBA News data with the following code:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = f'https://api.sportsdata.io/v3/nba/scores/json/News'

params = {
    'key': os.getenv('SPORTSDATA_API_KEY')
}

def get_news():
    response = requests.get(url, params=params)
    return response.json()

```

You’ll be able to see the response in JSON or in a browser by hitting the \`/News_\`_ endpoint and appending your API key as a query string. That may look like this:

```bash
https://api.sportsdata.io/v3/nba/scores/json/News?key={YOUR_API_KEY}
```

![](https://lh4.googleusercontent.com/xsWrXDMJ9FQkhMa94lmvl0Tsn7fT2vg-TX8RMlzQ7WHKoGdUt8nHv1Bglerb3ClWVFeIlMsroBaW1bUHG-EdYQvACBu5j8sLBaOpfaDgaDtADzTlDA1HZ9bnDPnwBY4eHQxn2eDWCjealFtdVu9pqtg)

If you format the JSON response, you’ll see a key called “Categories”. According to the [SportsDataIO data dictionary](https://sportsdata.io/developers/data-dictionary/nba) at the time I wrote this post, potential return values are: Top Headlines, Breaking News, Injury, Sit/Start, Waiver Wire, Risers, Fallers, Lineups, Transactions, Free Agents, Prospects/Rookies, Game Recap, Matchup Outlook.

For now, I’m interested in getting back data that are categorized as “Top-Headlines”. In order to filter this, I’m going to replace the code in \`nba_news.py\` with the following:

```python
import requests
import os

from datetime import date
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

today = date.today()


# we are hitting 2 endpoints which returns news for today & news for all days
url_news_today = f'https://api.sportsdata.io/v3/nba/scores/json/NewsByDate/{today}'
url_news_all = f'https://api.sportsdata.io/v3/nba/scores/json/News'


# we stored our API key in the .env file and are accessing it here, then storing them as parameters for our HTTP request
params = {
    'key': os.getenv('SPORTSDATA_API_KEY')
}


# we are creating a function to either get the news for today or getting all news
def get_news(date=None):
    if date == 'today':
        response = requests.get(url_news_today, params=params)
    else:
        response = requests.get(url_news_all, params=params)
    return response.json()


# we are looping through the JSON response and seeing if ‘Top-Headlines’ are in the Category key.
def check_transactions(response, target_category):
    for news in response:
        if target_category in news['Categories']:
            return True
    return False


# we return a string output that contains the title and date of a ‘Top-Headlines’ news
def print_transactions(response, target_category):
    output = ''
    for news in response:
        if target_category in news['Categories']:
            output += f"Title: {news['Title']}\n"
            output += f"Date: {news['TimeAgo']}\n"
            output += '----------------------------------------\n'
    return output


# we take in user input. if the user enters F5, we will get news from today only. if the user enters anything else, we will get news from all days.
def get_transactions(date=None):
    target_category = 'Top-Headlines'

    if date and 'f5' in date.lower():
        response = get_news('today')
        if not check_transactions(response, target_category):
            return('No transactions today, keep F5ing')
    else:
        response = get_news()
    return print_transactions(response, target_category)
```

We can test out the code by calling get_transactions(). For example, add the following to the end of the file:

```bash
if __name__ == '__main__':
    print(get_transactions())
```

Then run the following on the command line:

```bash
python nba_news.app
```

You can also test it by entering an argument containing the text ‘F5’. This will give you news for the current day. But if there isn’t any news, you’ll get a message saying that you should keep F5ing.


## Make an Outbound SMS

We’ve successfully returned the data that we need, now it’s time to test it out with an outbound SMS. Think of outbound as sending a text message “OUT” to someone’s phone number. So, we are trying to send OUT NBA news via a text message.

Within the same file, let’s create a new function called \`send_text()\` to send a text message to a phone number of your choice from your Twilio phone number. Just remember to replace 'ENTER_YOUR_TWILIO_NUMBER' with your Twilio number (found in the [Console](https://console.twilio.com/)), and 'ENTER_THE_NUMBER_YOURE_TEXTING_TO' with the phone number you’re wanting to text. 

```python
def send_text(option=None):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=get_transactions(option),
        from_='ENTER_YOUR_TWILIO_NUMBER',
        to='ENTER_THE_NUMBER_YOURE_TEXTING_TO'
    )
    print(message.body)

```

In the code above, notice that the body of our message is a function call that returns NBA news.

Below that function, call it, e.g., \`send_text()\` and optionally enter in a string argument such as ‘give me news’. Remember, that if the argument contains ‘F5’, we get news for today (anything else will return all news).

Back in your console, re-run the file:

```bash
python nba_news.py
```

If you entered your own phone number in the “to” parameter, a text message should be sent to your phone!


## Make an Inbound SMS

If there was NBA news in our response, we should have successfully sent an SMS containing Top Headlines around the league. Now we’re going to create part of our application for an Inbound SMS. Think of Inbound as an inbound SMS triggering your application. In this case, we will be sending a text to a Twilio phone number (our trigger), then having it respond by sending a reply containing news.

Create a new file in the same directory called app.py. Using [Flask](https://flask.palletsprojects.com/en/2.1.x/), a web framework for Python, we will create an app that runs on a local server. Copy the following code into app.py: 

```python
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
```

Run the application on your local server with this command in your console:

```bash
python app.py
```

Your application should be running on <http://localhost:8080>. Output will look similar to this:

```bash
* Serving Flask app 'app' (lazy loading)
* Environment: production   WARNING: This is a development server. Do not use it in a production deployment.   Use a production WSGI server instead. 
* Debug mode: on 
* Running on http//localhost:8080 (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 199-776-319
```

As of now, our application is only running on a server within your computer. But we need a public-facing URL (not <http://localhost>) to configure a [Webhook](https://www.twilio.com/docs/usage/webhooks/getting-started-twilio-webhooks) so Twilio can find it. By using a tool, called ngrok, we will [“put localhost on the Internet”](https://ngrok.com/product) so we can configure our webhook.

In another console tab, run the command:

```bash
ngrok http 8080
```

This will create a “tunnel” from the public Internet into port 8080 in our local machine, where the Flask app is listening for requests. You should see output similar to this:

![](https://lh5.googleusercontent.com/6uMr87Rfeids1K5y0GNW3X-orVN14F2pywbEkVeGJXj9vRVoRoSmIB9a_4s-H_FyCFqGnSQ7EuE8ryj4eVJU7Wn-RVTiwpfpj8tUzkTuTKJY6Eqy8ZwKIfFY4hiZ7ikCUvtPuaWbSpgxLSb8sB1nQZU)

Take note of the line that says “Forwarding”. In the image above, it shows: https&#x3A;//5bad813c2718.ngrok.io -> http&#x3A;//localhost:8080

This means that our local application is running publicly on https&#x3A;//5bad813c2718.ngrok.io/nba

Within the Console, enter in the ngrok URL as a Webhook when “A Message Comes In”.

![](https://lh4.googleusercontent.com/RYZ_usVQ4ZRxcXnGEt9lwshByluP2foZprJGwKAcFl3JGrd8fLesvvZAyVeo_iN8uy_AvnTZMnewHkbzO5BguDFiszc5VgCtHZSPGkxEtqqyPkzexvqnSEoitRBM4cTYwvWI6JeEPaxldPQItSUloFg)

Please be aware that unless you have an account, each time you run the ngrok command a new URL will be generated, so be sure to make the changes within the Twilio console.

Since our application and ngrok are running, we can send a text message to our Twilio phone number and it will respond back with NBA news!

![](https://lh4.googleusercontent.com/VSIeE8fc1TC-Um1aWUFwReFUF8KODvw9RxcnC_mCMCBn8Kz-myF8Sm9J5S4q4dSnqK9maIVLYmZZX84PjkGi95Trudplv6R46ciDBSzPA2dXjC_c7BwQsFt_iSfg3cmezgznM0L0Pa3fIqrUJR-rg1A)

If you text “F5” and no news has happened that day, you’ll receive a message like this:

![](https://lh3.googleusercontent.com/RtqkKbVf0T60b3dr6FwwCEkKKKpXr_xkPUOeeKJoUg20ybxY6vpWLNM7vHnqMhD3CV6xMbSu9u6MuUhMJJ2G9yWhKKIcj2Z-WbtdmrEYMU54MimPkk8-AFL3hsh27hHy3v-VqBiOGcv6PczBCvMutgY)


## What if you don’t like basketball but want news for other sports?

Since we are using the SportsDataIO API, they provide developers with endpoints for multiple sports. If you aren’t interested in NBA news, check out the other sports from their [API docs](https://sportsdata.io/developers/api-documentation).

Furthermore, if you want to do something with player statistics, team standings, schedules, fantasy stats, and much more, just take a look at what [SportsDataIO](https://sportsdata.io/developers) offers.


## Show Me What You Build

Now that you can F5 from your phone, you won’t miss out on any Top Headlines in the NBA world. So keep, F5ing until the season starts on October 19, 2022.

Thanks so much for reading! If you found this tutorial helpful, have any questions, or want to show me what you’ve built, let me know online. And if you want to learn more about me, check out [my intro blog post](https://www.twilio.com/blog/introducing-twilio-developer-evangelist-anthony-dellavecchia).

![](https://lh5.googleusercontent.com/QqqYPg-hhp8oQKv4XEWLDNhjs5DrmgJbm_qEWZWJLzudWG9T46R7OIGWhVDRHjosLv7aM-I3xXxzORP6VhiUjbJvZIjiO1RZx-aLdIJXwZUMXTgwR8b1FRzWKra4KTQP2gljGhKXRG1fp83uWqkYbEk)

> _Anthony Dellavecchia is a Developer Evangelist at Twilio who writes code on stage in front of a crowd. He is an experienced software developer who teaches thousands of people how to change the world with code. His goal is to help you build deep experiences and connections with technology so that they stick with you forever._

> _Check him out online @anthonyjdella -- _[_Twitter_](https://twitter.com/anthonyjdella)_ • _[_Linkedin_](https://www.linkedin.com/in/anthonydellavecchia/)_ • _[_GitHub_](https://github.com/anthonyjdella)_ • _[_TikTok_](https://tiktok.com/@anthonyjdella)_ • _[_Medium_](https://medium.com/@anthonyjdella)_ • _[_Dev.to_](https://dev.to/anthonyjdella)_ • Email • _[_anthonydellavecchia.com_](https://anthonydellavecchia.com/)_ 👈_

