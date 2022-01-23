
import prawcore
import json
from difflib import SequenceMatcher, get_close_matches
from nltk.corpus import stopwords
import nltk
import random
from textblob import TextBlob
import praw


secret = "5g48PyXKQW7J5_j5i23emTDXvgRUcg"
clientID = "CoNV4gzO0IjtG8lYqKuyRg"
reddit = praw.Reddit(client_id=clientID,
                     client_secret=secret, user_agent="hackathon")

text = input("> ")


def getKeywords(text):
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
        # if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg") or url.endswith("gif"):
        postsTitle.append(submissions.title)
        postsUrl.append(submissions.url)
    posts = dict(zip(postsTitle, postsUrl))
    articleTitle = analyzeTitles(postsTitle, text)
    link = posts[articleTitle]
    return [articleTitle, link]


def getSubreddit(text):
    keywords = getKeywords(text)
    sentenceParts = getKeywordsNouns(keywords)
    inputNouns = sentenceParts["Noun"]
    inputAdjective = sentenceParts["Adjective"]
    inputAdverb = sentenceParts["Adverb"]

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


def message(text):
    redditPost = getSubreddit(text=text)
    return redditPost


print(message(text=text))
print(message(text=text)[1])
