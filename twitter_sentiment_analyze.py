#!/usr/bin/env python

import tweepy 
import pandas as pd
import numpy as np
import re

from textblob import TextBlob

consumer_key = 'HdNSlIGr6jGZ9LYSqyZwKAAg9'
consumer_secret = 'bLCL2VjhD9BdVzYLTIEwWh1cI1GtKZRengYo4wwMIteGFlRjIc'
access_token = '758564236708773890-mrGuoqx7qlH1F7nFomZvlmx3uy8U5cQ'
access_token_secret = 'gRyl3HtDVPpLqRRc0UKWZXb7AkHIJM3OarzkFrpwB1Fob' 

class TwitterClient(object):
    def __init__(self):  
        # setting keys for twitter account 
        self.api = self.twitter_setup()  
        self.friends = self.api.friends()
        #self.data = pd.DataFrame()
        self.storeResults = []    

    def twitter_setup(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        try:
            auth.set_access_token(access_token, access_token_secret)
        except tweepy.TweepError:
            print 'Error! Failed to get access token.'
        self.api = tweepy.API(auth)   
        return self.api

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def sentiment_analyze(self, tweet):
        ''' 
        Running sentiment analyze on the tweet 
        if tweets is positive function return 1
        if neutral return 0
        if negative return -1
        '''
        analize = TextBlob(self.clean_tweet(tweet))
        if analize.sentiment.polarity > 0:
            return 1
        elif analize.sentiment.polarity == 0:
            return 0
        else:
            return -1
    
    def get_positive_feeds_percentage(self, id):
        ''' 
        Reads last 10 timeline feeds of user
        Counts how many feeds had positive content
        And returns the result by percent(%)
        '''
        tweets = self.api.user_timeline(id, count=10)
        # load tweets into dataframe
        tweetsData = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        # runs sentiment analyze on the tweet 
        tweetsData['SA'] = np.array([self.sentiment_analyze(tweet) for tweet in tweetsData['Tweets']])
        pos_tweets = [tweet for index, tweet in enumerate(tweetsData['Tweets']) if tweetsData['SA'][index] > 0]
        return format(len(pos_tweets)*100/len(tweetsData['Tweets']))

    def client_happiness(self):
        '''
        Take 5 people whom this account follows
        Run sentiment analyze on their feeds
        Saves the names and results in DataFrame
        '''
        data = pd.DataFrame(data=[friend.name for friend in self.friends], columns=['Client'])
        for friend in tweepy.Cursor(self.api.friends).items(5):
            percentage = self.get_positive_feeds_percentage(friend.id)
            # Store the values in array
            self.storeResults.append(percentage)
            column_values = pd.Series(self.storeResults)
        data.insert(loc=1, column='Percentage(%)', value=column_values)
        return data

    def print_dataframe(self):
        data = self.client_happiness()
        print data.head(5)
        

if __name__ == "__main__":
    api = TwitterClient()
    #api.client_happiness()
    api.print_dataframe()

