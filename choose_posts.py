
import prawcore
import json
from difflib import get_close_matches
from nltk.corpus import stopwords
import nltk
import random
from textblob import TextBlob
import praw

# secret = os.environ.get("secret")
# clientID = os.environ.get("clientID")
secret = "5g48PyXKQW7J5_j5i23emTDXvgRUcg"
clientID = "CoNV4gzO0IjtG8lYqKuyRg"
reddit = praw.Reddit(client_id=clientID,
                     client_secret=secret, user_agent="hackathon")


def getKeywords(text):
    """
    Get the key words from the text entered by the user
    Returns a list of the key words
    """
    stopWords = set(stopwords.words("english"))
    sentence = nltk.word_tokenize(text)  # remove useless words
    filteredSentence = []
    for words in sentence:
        if words not in stopWords:
            filteredSentence.append(words)

    return filteredSentence


def getKeywordsNouns(filtered):
    """
    Classifies the word in the sentence in their respective parts of speech
    Returns dictionary with the words in the input sentence in their respective parts of speech
    """
    partSpeech = nltk.pos_tag(
        filtered)  # Identify parts of speech of each keyword
    partsSpeechDict = {
        "Adjective": [],
        "Adverb": [],
        "Noun": [],
        "Interrogation": []
    }
    # Classify parts of speech of each work in dictionary
    for parts in partSpeech:
        partOfSpeech = parts[1]
        # Identift
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
    """
    Analyses the users current sentiment and finds the post that matches the most to the user's sentiment
    Returns the reddit post matching user sentiment
    """
    sentimentInput = sentiment_analysis(text=text)
    # Gets polarity value of sentence
    userSentiment = sentimentInput.sentiment.polarity
    titleScore = dict.fromkeys(titles, 0)

    #
    for title in titleScore.keys():
        processing_input = sentiment_analysis(text=title)
        sentiment_text = processing_input.sentiment.polarity
        titleScore[title] = sentiment_text

    # sort dictionary by value (polarity value)
    sortedTitleScore = {k: v for k, v in sorted(
        titleScore.items(), key=lambda item: item[1])}

    # Return negative reddit image if user negative
    if userSentiment < 0:
        sadTitle = list(sortedTitleScore.keys())[0]
        post = sadTitle

    # Return positive reddit image if user positive
    else:
        happyTitle = list(sortedTitleScore.keys())[-1]
        post = happyTitle

    return post


def getBestPost(subs, text):
    """
    Searches through subreddit and get the most relevant post

    Returns title of post and image
    """
    postsTitle = []
    postsUrl = []
    for submissions in subs:
        url = submissions.url
        # Filter for only images
        if url.endswith("jpeg") or url.endswith("png") or url.endswith("jpg") or url.endswith("gif"):
            postsTitle.append(submissions.title)
            postsUrl.append(submissions.url)
    posts = dict(zip(postsTitle, postsUrl))
    articleTitle = analyzeTitles(postsTitle, text)
    link = posts[articleTitle]
    return (articleTitle, link)


def getSubreddit(text):
    """
    Searches in the most relevant subreddit according to user input

    Returns title of post and image link

    """
    keywords = getKeywords(text)
    sentenceParts = getKeywordsNouns(keywords)
    inputNouns = sentenceParts["Noun"]
    inputAdjective = sentenceParts["Adjective"]
    inputAdverb = sentenceParts["Adverb"]
    # chooses random keywords in user input for search queries
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
    # Attempts to autocorrect the user input to match with a subreddit in subreddit.json
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
                searchWord, listSubreddit, n=1, cutoff=0.6)  # chooses the closest subredddit match from user input
        suggestion = suggestion[0][2:]
        subs = reddit.subreddit(suggestion).hot(limit=100, over18=False)
        return getBestPost(subs, text)


def message(text):
    try:

        # Returns the link of the image
        redditPost = getSubreddit(text=text)
        return redditPost[1]
    except:
        # Returns a message if there is an error
        return "Our wisest and brightest team member is currently digging through the code to resolve this issue. https://images-ext-2.discordapp.net/external/rHrzbafIax5hHS5hxo2FbPLItjDeaGgFx9oP8tChCgg/%3Fwidth%3D640%26crop%3Dsmart%26auto%3Dwebp%26s%3D0ba6e5b5ccbc7677fd5d133820bbbc900d863356/https/preview.redd.it/bu98ackay7d81.jpg?width=634&height=925"
