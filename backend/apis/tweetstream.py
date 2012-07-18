
from lib.twitter import Twitter
from models import twitter
from lib import publish

@publish.api("add-tweetstream", body = True)
def add_tweetstream(body):
    twitter.TweetStream(station_id = body["station_id"], 
                        search_url = body["search_url"]).put()
    return body

@publish.api("stat-tweetstreams")
def add_tweetstream():
    response = {}
    for tweetstream in twitter.TweetStream.query().fetch():      
        count = sum(  [len(tweets.tweets) for tweets in twitter.Tweets.query( twitter.Tweets.stream == tweetstream.key ).fetch()] )
        response[tweetstream.station_id] = {"last-update": str(tweetstream.last_update), "tweets-count":  count}
    return response