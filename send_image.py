from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from credentials import * # custom file used to store my Twilio id, auth token, Twilio phone number and my personal phone number

app = Flask(__name__) # create Flask app


@app.route('/sms', methods=['POST']) # not sure what does this do but apparently it's necessary
def sms(): # default function for twilio
    number = request.form.get('From') # get your phone number
    body = request.form.get('Body') # get your input message (so your message is now stored in 'body')
    resp = MessagingResponse() # enable response
    my_msg = "Hello "+number+", you said "+body+"." # a short message on top of the image
    my_url = ['https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg']
    return client.messages.create(to=my_cell, from_=my_twilio, body=my_msg, media_url=my_url) # send this back to user


if __name__ == '__main__':
    client = Client(account_sid, auth_token) # your Twilio id and auth token
    app.run()
