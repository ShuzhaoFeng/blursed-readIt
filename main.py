import random
import json
import praw
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from credentials import *
from difflib import get_close_matches

app = Flask(__name__)  # create Flask app


@app.route('/sms', methods=['POST'])
def sms():  # default function for twilio
    global text
    text = request.form.get('Body')  # get your input message
    resp = MessagingResponse()  # enable response
    my_msg = "*placeholder message*"  # a message on top of the image
    my_url = [str(message(text=text)[1])]
    return client.messages.create(to=my_cell, from_=twilio_phonenum,
                                  body=my_msg, media_url=my_url)  # send this back to user


def get_keywords(text):
    stop_words = set(stopwords.words("english"))
    sentence = nltk.word_tokenize(text)
    filtered_sentence = []
    for words in sentence:
        if words not in stop_words:
            filtered_sentence.append(words)

    return filtered_sentence


def get_keywords_nouns(filtered):
    part_speech = nltk.pos_tag(filtered)
    parts_speech_dict = {
        "Adjective": [],
        "Adverb": [],
        "Noun": [],
        "Interrogation": []
    }
    print(part_speech)
    for parts in part_speech:
        part_of_speech = parts[1]
        if part_of_speech.startswith("N"):
            parts_speech_dict["Noun"].append(parts[0])
        elif part_of_speech.startswith("J"):
            parts_speech_dict["Adjective"].append(parts[0])
        elif part_of_speech.startswith("R") or part_of_speech.startswith("V"):
            parts_speech_dict["Adverb"].append(parts[0])
        elif part_of_speech.startswith("W"):
            parts_speech_dict["Interrogation"].append(parts[0])

    return parts_speech_dict


def sentiment_analysis(text):
    testimonial = TextBlob(text)
    return testimonial


def analyze_titles(titles, text):
    sentiment_input = sentiment_analysis(text=text)
    user_sentiment = sentiment_input.sentiment.polarity
    title_score = dict.fromkeys(titles, 0)
    for title in title_score.keys():
        processing_input = sentiment_analysis(text=title)
        sentiment_text = processing_input.sentiment.polarity
        title_score[title] = sentiment_text

    sorted_title_score = {k: v for k, v in sorted(
        title_score.items(), key=lambda item: item[1])}
    if user_sentiment < 0:
        sad_title = list(sorted_title_score.keys())[0]
        post = sad_title

    else:
        happy_title = list(sorted_title_score.keys())[-1]
        happy_url = sorted_title_score[happy_title]
        post = happy_title

    return post


def get_best_post(subs):
    global text
    posts_title = []
    posts_url = []
    for submissions in subs:
        # if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg") or url.endswith("gif"):
        posts_title.append(submissions.title)
        posts_url.append(submissions.url)
    posts = dict(zip(posts_title, posts_url))
    article_title = analyze_titles(posts_title, text)
    link = posts[article_title]
    return [article_title, link]


def get_subreddit(text):
    keywords = get_keywords(text)
    sentence_parts = get_keywords_nouns(keywords)
    input_nouns = sentence_parts["Noun"]
    input_adverb = sentence_parts["Adverb"]
    input_adjective = sentence_parts["Adjective"]

    noun = ""
    adverb = ""
    adjective = ""
    if len(input_nouns) != 0:
        noun = random.choice(input_nouns)
    if len(input_adverb):
        adverb = random.choice(input_adverb)
    if len(input_adjective):
        adjective = random.choice(input_adjective)
    search_word = "r/" + noun + adverb + adjective
    print(search_word)
    with open("subreddits.json", "r") as data_file:
        fp = json.load(data_file)
        list_subreddit = list(fp)
        suggestion = get_close_matches(
            search_word, list_subreddit, n=1, cutoff=0.6)
    suggestion = suggestion[0][2:]
    print(suggestion)
    subs = reddit.subreddit(suggestion).hot(limit=100)
    return get_best_post(subs)


def message(text):
    reddit_post = get_subreddit(text=text)
    return reddit_post


if __name__ == '__main__':
    text = ""
    client = Client(twilio_account_sid, twilio_auth_token)  # your Twilio id and auth token
    reddit = praw.Reddit(client_id=reddit_clientID, client_secret=reddit_secret,
                         user_agent="hackathon")  # your Reddit id
    app.run()

