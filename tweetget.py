import os
import json

import psycopg2
from twitter import *

def _get_credentials():
    with open('config.json', 'r') as config:
        if config:
            conf = json.load(config)
        else:
            conf['token'] = os.environ['twitter_token']
            conf['token_secret'] = os.environ['twitter_token_secret']
            conf['consumer'] = os.environ['twitter_consumer']
            conf['consumer_secret'] = os.environ['twitter_consumer_secret']
    return conf

def _get_oauth(conf):
    '''
    :param conf: dict of Twitter API credentials. See get_credentials()
    '''
    return OAuth(conf['token'], conf['token_secret'], conf['consumer'], conf['consumer_secret'])


def add_tweet(tweet):
    '''
    Postgresql server startup, see more at initd.org/psycopg/docs/usage.html
    '''
    conn = psycopg2.connect("dbname=tweets user=postgres")
    cur = conn.cursor()
    # Declaring variables in order to make life easier
    twitter_id = tweet['user']['id']
    twitter_name = tweet['user']['screen_name']
    text = tweet['text']

    url = "https://twitter.com/statuses/"+ str(tweet['id'])
    profilepic = str(tweet['user']['profile_image_url'])
    # The next few lines are seeing if an already exists in the table to store ID's and handles
    # if the ID does not exist, it inserts it in, if it already exists though, there's no need
    cmd = "SELECT * FROM twitter_ids WHERE twitter_id=%s"
    cur.execute(cmd, [twitter_id])
    there = cur.fetchone()
    if not there:
        cmd = "INSERT INTO twitter_ids(twitter_id,handle,profilepic) VALUES (%s,%s,%s)"
        cur.execute(cmd, (twitter_id, twitter_name, profilepic))
        conn.commit()
    # This is inserting every single tweet into the tweets database
    # twitter_id is a bigint variable made to store the ID's of specific people on twitter
    # tweet is just the text of the tweet itself
    cmd = "INSERT INTO tweets(twitter_id,tweet,url) VALUES (%s,%s,%s)"
    cur.execute(cmd, (twitter_id, text, url))
    conn.commit()
    cur.close()
    conn.close()

def keywordadd(tweet, keyword):
    '''
    This adds to the keyword table, helpful for predictit stuff
    '''

    conn = psycopg2.connect("dbname=tweets user=postgres")
    cur = conn.cursor()
    twitter_id = tweet['user']['id']
    # Same deal as before, searching to see if there is already a row with
    # the specifications it needs, if not, make that row.
    cmd = "SELECT * FROM tweets_keyword WHERE twitter_id=%s AND keyword=%s"
    cur.execute(cmd, (twitter_id, keyword))
    there = cur.fetchone()
    if not there:
        cmd = "INSERT INTO tweets_keyword(twitter_id,keyword,amount) VALUES(%s,%s,%s)"
        cur.execute(cmd, (twitter_id, keyword, 0))
        conn.commit()
    # This is adding one to the amount of the keyword row.
    cmd = "UPDATE tweets_keyword SET amount= amount+1 WHERE twitter_id=%s AND keyword=%s"
    cur.execute(cmd, (twitter_id, keyword))
    conn.commit()
    cur.close()
    conn.close()

def main():
    conf = _get_credentials()
    golden_shower = TwitterStream(auth=_get_oauth(conf), domain='userstream.twitter.com')
    for msg in golden_shower.user():
        tweet = json.loads(json.dumps(msg))
        if 'text' in tweet:
            print("New tweet from "+tweet['user']['name'])
            add_tweet(tweet)
            if "love" in tweet['text'].lower():     # Let's see how much twitter loves
                keywordadd(tweet, "love")
            if "trump" in tweet['text'].lower():
                keywordadd(tweet, "Trump") 

if __name__ == '__main__':
    main()
