import praw
import os
from textblob import TextBlob
import random
import nltk
from nltk.corpus import stopwords
from difflib import SequenceMatcher, get_close_matches
import json
import prawcore
nltk.download
# secret = os.environ.get("secret")
# clientID = os.environ.get("clientID")
secret = "5g48PyXKQW7J5_j5i23emTDXvgRUcg"
clientID = "CoNV4gzO0IjtG8lYqKuyRg"
reddit = praw.Reddit(client_id=clientID,
                     client_secret=secret, user_agent="hackathon")

text = input("> ")


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


def getBestPost(subs):
    postsTitle = []
    postsUrl = []
    for submissions in subs:
        title = submissions.title
        url = submissions.url
        # if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg") or url.endswith("gif"):
        postsTitle.append(submissions.title)
        postsUrl.append(submissions.url)
    posts = dict(zip(postsTitle, postsUrl))
    articleTitle = analyzeTitles(postsTitle, text)
    link = posts[articleTitle]
    return (articleTitle, link)


def getSubreddit(text):
    keywords = getKeywords(text)
    sentenceParts = getKeywordsNouns(keywords)
    inputNouns = sentenceParts["Noun"]
    inputAdjective = sentenceParts["Adjective"]
    inputAdverb = sentenceParts["Adverb"]
    # if len(inputNouns) != 0:
    #     wordType = "noun"
    #     noun = random.choice(inputNouns)
    #     subs = reddit.subreddit(noun).hot(limit=100)
    # elif len(inputAdverb) != 0:
    #     wordType = "adverb"
    #     adverb = random.choice(inputAdverb)
    #     subs = reddit.subreddit(adverb).hot(limit=100)
    # elif len(inputAdjective) != 0:
    #     wordType = "adjective"
    #     adjective = random.choice(inputAdjective)
    #     subs = reddit.subreddit(adjective).hot(limit=100)
    # postsTitle = []
    # postsUrl = []
    # try:
    #     return getBestPost(subs)

    # except Exception:
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
    print(searchWord)
    with open("subreddits.json", "r") as data_file:
        fp = json.load(data_file)
        listSubreddit = list(fp)
        suggestion = get_close_matches(
            searchWord, listSubreddit, n=1, cutoff=0.6)
    suggestion = suggestion[0][2:]
    print(suggestion)
    subs = reddit.subreddit(suggestion).hot(limit=100)
    return getBestPost(subs)
    # except Exception:
    #     subs = reddit.subreddit("programminghumor").hot(limit=20)
    #     for submissions in subs:
    #         url = submissions.url
    #         if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg"):
    #             return url


def message(text):
    redditPost = getSubreddit(text=text)
    return redditPost


print(message(text=text))
