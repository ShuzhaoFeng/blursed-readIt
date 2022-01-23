import random
import json
import praw
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from credentials import *
from difflib import get_close_matches

app = Flask(__name__)  # create Flask app


def getKeywords(text):
    """
    """
    stopWords = set(stopwords.words("english"))
    sentence = nltk.word_tokenize(text)
    filteredSentence = []
    for words in sentence:
        if words not in stopWords:
            filteredSentence.append(words)

    return filteredSentence


def getKeywordsNouns(filtered):
    partSpeech = nltk.pos_tag(filtered)
    partsSpeechDict = {
        "Adjective": [],
        "Adverb": [],
        "Noun": [],
        "Interrogation": []
    }
    print(partSpeech)
    for parts in partSpeech:
        partOfSpeech = parts[1]
        if partOfSpeech.startswith("N"):
            partsSpeechDict["Noun"].append(parts[0])
        elif partOfSpeech.startswith("J"):
            partsSpeechDict["Adjective"].append(parts[0])
        elif partOfSpeech.startswith("R") or partOfSpeech.startswith("V"):
            partsSpeechDict["Adverb"].append(parts[0])
        elif partOfSpeech.startswith("W"):
            partsSpeechDict["Interrogation"].append(parts[0])

    return partsSpeechDict


def sentiment_analysis(text):
    testimonial = TextBlob(text)
    return testimonial


def analyzeTitles(titles, text):
    sentimentInput = sentiment_analysis(text=text)
    userSentiment = sentimentInput.sentiment.polarity
    titleScore = dict.fromkeys(titles, 0)
    for title in titleScore.keys():
        processing_input = sentiment_analysis(text=title)
        sentiment_text = processing_input.sentiment.polarity
        titleScore[title] = sentiment_text

    sortedTitleScore = {k: v for k, v in sorted(
        titleScore.items(), key=lambda item: item[1])}
    if userSentiment < 0:
        sadTitle = list(sortedTitleScore.keys())[0]
        post = sadTitle

    else:
        happyTitle = list(sortedTitleScore.keys())[-1]
        happyUrl = sortedTitleScore[happyTitle]
        post = happyTitle

    return post


def getBestPost(subs, text):
    postsTitle = []
    postsUrl = []
    for submissions in subs:
        title = submissions.title
        url = submissions.url
        if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg"):
            postsTitle.append(submissions.title)
            postsUrl.append(submissions.url)
    posts = dict(zip(postsTitle, postsUrl))
    articleTitle = analyzeTitles(postsTitle, text)
    link = posts[articleTitle]
    return (articleTitle, link)


def getSubreddit(text):
    """
    Searches in the most relevant subreddit from the user's 
    """
    keywords = getKeywords(text)
    sentenceParts = getKeywordsNouns(keywords)
    inputNouns = sentenceParts["Noun"]
    inputAdjective = sentenceParts["Adjective"]
    inputAdverb = sentenceParts["Adverb"]
    if len(inputNouns) != 0:
        noun = random.choice(inputNouns)
        subs = reddit.subreddit(noun).hot(limit=100, over18=False)
    elif len(inputAdverb) != 0:
        adverb = random.choice(inputAdverb)
        subs = reddit.subreddit(adverb).hot(limit=100, over18=False)
    elif len(inputAdjective) != 0:
        adjective = random.choice(inputAdjective)
        subs = reddit.subreddit(adjective).hot(limit=100, over18=False)
    try:
        return getBestPost(subs, text)

    except prawcore.exceptions.NotFound:
        noun = ""
        adverb = ""
        adjective = ""
        if len(inputNouns) != 0:
            noun = random.choice(inputNouns)
        if len(inputAdverb):
            adverb = random.choice(inputAdverb)
        if len(inputAdjective):
            adjective = random.choice(inputAdjective)
        searchWord = "r/" + noun + adverb + adjective
        with open("subreddits.json", "r") as data_file:
            fp = json.load(data_file)
            listSubreddit = list(fp)
            suggestion = get_close_matches(
                searchWord, listSubreddit, n=1, cutoff=0.6)
        suggestion = suggestion[0][2:]
        subs = reddit.subreddit(suggestion).hot(limit=100, over18=False)
        return getBestPost(subs, text

def message(text):
     try:
        redditPost = getSubreddit(text=text)
        return redditPost[1]

    except:
        return "Our wisest and brightest team member is currently digging through the code to resolve this issue. https://preview.redd.it/bu98ackay7d81.jpg?width=640&crop=smart&auto=webp&s=0ba6e5b5ccbc7677fd5d133820bbbc900d863356"


@app.route('/sms', methods=['POST'])
def sms():  # default function for twilio
    global text
    text = request.form.get('Body')  # get your input message
    resp = MessagingResponse()  # enable response
    url = message(text)
    my_msg = "*placeholder message*"  # a message on top of the image
    print(str(client.messages.create(to=my_cell, from_=twilio_phonenum,
                                  body=my_msg, media_url=[url])))
    return ""


if __name__ == '__main__':
    text = ""
    client = Client(twilio_account_sid, twilio_auth_token)  # your Twilio id and auth token
    reddit = praw.Reddit(client_id=reddit_clientID, client_secret=reddit_secret,
                         user_agent="hackathon")  # your Reddit id
    app.run()
