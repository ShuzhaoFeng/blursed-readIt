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
        subs = reddit.subreddit(noun).hot(limit=100)
    elif len(inputAdverb) != 0:
        adverb = random.choice(inputAdverb)
        subs = reddit.subreddit(adverb).hot(limit=100)
    elif len(inputAdjective) != 0:
        adjective = random.choice(inputAdjective)
        subs = reddit.subreddit(adjective).hot(limit=100)
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
        subs = reddit.subreddit(suggestion).hot(limit=100)
        return getBestPost(subs, text

def message(text):
     try:
        redditPost = getSubreddit(text=text)
        return redditPost[1]

    except:
        return "Our wisest and brightest team member is currently digging through the code to resolve this issue. https://images-ext-2.discordapp.net/external/rHrzbafIax5hHS5hxo2FbPLItjDeaGgFx9oP8tChCgg/%3Fwidth%3D640%26crop%3Dsmart%26auto%3Dwebp%26s%3D0ba6e5b5ccbc7677fd5d133820bbbc900d863356/https/preview.redd.it/bu98ackay7d81.jpg?width=634&height=925"


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
