import random
import json
import praw
import prawcore
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from credentials import twilio_account_sid, twilio_auth_token, my_cell, twilio_phonenum, reddit_clientID, reddit_secret
from difflib import get_close_matches

app = Flask(__name__)  # create Flask app


def get_keywords(text):
    """
    Get the key words from the text entered by the user
    Returns a list of the key words
    """
    stop_words = set(stopwords.words("english"))
    sentence = nltk.word_tokenize(text)  # remove useless words
    filtered_sentence = []
    for words in sentence:
        if words not in stop_words:
            filtered_sentence.append(words)

    return filtered_sentence


def get_keywords_nouns(filtered):
    """
    Classifies the word in the sentence in their respective parts of speech
    Returns dictionary with the words in the input sentence in their respective parts of speech
    """
    part_speech = nltk.pos_tag(
        filtered)  # Identify parts of speech of each keyword
    parts_speech_dict = {
        "Adjective": [],
        "Adverb": [],
        "Noun": [],
        "Interrogation": []
    }
    # Classify parts of speech of each work in dictionary
    for parts in part_speech:
        part_of_speech = parts[1]
        # Identift
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
    """
    Analyses the users current sentiment and finds the post that matches the most to the user's sentiment
    Returns the reddit post matching user sentiment
    """
    sentiment_input = sentiment_analysis(text=text)
    # Gets polarity value of sentence
    user_sentiment = sentiment_input.sentiment.polarity
    title_score = dict.fromkeys(titles, 0)

    #
    for title in title_score.keys():
        processing_input = sentiment_analysis(text=title)
        sentiment_text = processing_input.sentiment.polarity
        title_score[title] = sentiment_text

    # sort dictionary by value (polarity value)
    sorted_title_score = {k: v for k, v in sorted(
        title_score.items(), key=lambda item: item[1])}

    # Return negative reddit image if user negative
    if user_sentiment < 0:
        sad_title = list(sorted_title_score.keys())[0]
        post = sad_title

    # Return positive reddit image if user positive
    else:
        happy_title = list(sorted_title_score.keys())[-1]
        post = happy_title

    return post


def get_best_post(subs, text):
    """
    Searches through subreddit and get the most relevant post
    Returns title of post and image
    """
    posts_title = []
    posts_url = []
    for submissions in subs:
        if submissions.over_18:
            continue
        url = submissions.url
        # Filter for only images
        if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg") or url.endswith("gif"):
            posts_title.append(submissions.title)
            posts_url.append(submissions.url)
    posts = dict(zip(posts_title, posts_url))
    article_title = analyze_titles(posts_title, text)
    link = posts[article_title]
    return article_title, link


def get_subreddit(text):
    """
    Searches in the most relevant subreddit according to user input
    Returns title of post and image link
    """
    keywords = get_keywords(text)
    sentence_parts = get_keywords_nouns(keywords)
    input_nouns = sentence_parts["Noun"]
    input_adjective = sentence_parts["Adjective"]
    input_adverb = sentence_parts["Adverb"]
    # chooses random keywords in user input for search queries
    if len(input_nouns) != 0:
        noun = random.choice(input_nouns)
        subs = reddit.subreddit(noun).hot(
            limit=100)
    elif len(input_adverb) != 0:
        adverb = random.choice(input_adverb)
        subs = reddit.subreddit(adverb).hot(
            limit=100)
    elif len(input_adjective) != 0:
        adjective = random.choice(input_adjective)
        subs = reddit.subreddit(adjective).hot(
            limit=100)
    try:
        return get_best_post(subs, text)
    # Attempts to autocorrect the user input to match with a subreddit in subreddit.json
    except prawcore.exceptions.NotFound:
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
        with open("subreddits.json", "r") as data_file:
            fp = json.load(data_file)
            list_subreddit = list(fp)
            suggestion = get_close_matches(
                search_word, list_subreddit, n=1, cutoff=0.6)  # chooses the closest subredddit match from user input
        suggestion = suggestion[0][2:]
        subs = reddit.subreddit(suggestion).hot(
            limit=100)
        return get_best_post(subs, text)


def message(text):
    try:
        # Returns the link of the image
        reddit_post = get_subreddit(text=text)
        return [reddit_post[0], reddit_post[1]]
    except:
        # Returns a message if there is an error
        return [
            "Our wisest and brightest team member is currently digging through the code to find the bug... or you have searched something naughty.",
            "https://images-ext-2.discordapp.net/external/rHrzbafIax5hHS5hxo2FbPLItjDeaGgFx9oP8tChCgg/%3Fwidth%3D640%26crop%3Dsmart%26auto%3Dwebp%26s%3D0ba6e5b5ccbc7677fd5d133820bbbc900d863356/https/preview.redd.it/bu98ackay7d81.jpg?width=634&height=925"]


@app.route('/sms', methods=['POST'])
def sms():  # default function for twilio
    global text
    text = request.form.get('Body')  # get your input message
    resp = MessagingResponse()  # enable response
    output = message(text)
    url = output[1]
    my_msg = output[0]  # a message on top of the image
    print(str(client.messages.create(to=my_cell, from_=twilio_phonenum,
                                     body=my_msg, media_url=[url])))
    return ""


if __name__ == '__main__':
    text = ""
    client = Client(twilio_account_sid, twilio_auth_token)  # your Twilio id and auth token
    reddit = praw.Reddit(client_id=reddit_clientID, client_secret=reddit_secret,
                         user_agent="hackathon")  # your Reddit id
    app.run()
