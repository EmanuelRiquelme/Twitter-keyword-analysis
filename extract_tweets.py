import tweepy
import math
import pandas as pd
from tweepy import Client
from openpyxl import load_workbook
import re
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('api_key')
api_key_secret = os.environ.get('api_key_secret')
access_token = os.environ.get('access_token')
access_token_secret = os.environ.get('access_token_secret')

auth = tweepy.OAuthHandler(api_key,api_key_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

def preprocess(tweets):
    proccesed_tweets = []
    for tweet in tweets.split():
        tweet = '@user' if tweet.startswith('@') and len(tweet) > 1 else tweet
        tweet = 'http' if tweet.startswith('http') else tweet
        proccesed_tweets.append(tweet)
    return " ".join(proccesed_tweets)


def extract_tweets(words,date_since,date_until,num_tweets=300):
    tweets = tweepy.Cursor(
                            api.search_tweets,
                            words, lang="en",
                            since_id=date_since,
                            until=date_until,
                            tweet_mode='extended').items(num_tweets)
    tweet_cont,tweet_rt,tweet_heart=[],[],[]
    for tweet in tweets:
        try:
            tweet_cont.append(preprocess(tweet.full_text))
            tweet_rt.append(tweet.retweet_count)
            tweet_heart.append(tweet.retweeted_status.favorite_count)
        except AttributeError:
            tweet_heart.append(0)
    data = {
        'Tweet': tweet_cont,
        'Retweet': tweet_rt,
        'Favs':tweet_heart
            }
    df = pd.DataFrame(data)
    with pd.ExcelWriter(f'sheets/{words}.xlsx') as writer:
        df.to_excel(writer)
