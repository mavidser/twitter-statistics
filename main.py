from __future__ import print_function
import sys
import twitter as twitter_api
import json
import Queue
import threading
import requests
import ConfigParser
from requests_oauthlib import OAuth1
from flask import Flask, render_template, request

def median(l):
    half = len(l) / 2
    l.sort()
    if len(l)==0:
        return -1
    if len(l) % 2 == 0:
        return (l[half-1] + l[half]) / 2.0
    else:
        return l[half]

def get_data(handle):
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    app_key             = Config.get('Twitter','app_key')
    app_secret          = Config.get('Twitter','app_secret')
    access_token        = Config.get('Twitter','access_token')
    access_token_secret = Config.get('Twitter','access_token_secret')
    api = twitter_api.Api(consumer_key=app_key,
                      consumer_secret=app_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)

    def getUserTweets(max_id=None):
        try:
            result = api.GetUserTimeline(screen_name=handle, count=200, include_rts = False, max_id=max_id)
            result = [{'id':x.id,'time':x.created_at,'rt':x.retweet_count} for x in result]

            if max_id:
                return result[1:]
            return result
        except Exception as e:
            print('Error:', e, file=sys.stderr)
            return None

    days={'Sun':0,'Mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6,}
    def extract_time(S):
        day = days[S[:3]]
        hour = int(S[11:13])
        return day,hour
    # extract_time('Sun Jun 01 06:19:10 +0000 2014')

    max_id=None
    count=5
    twitter=[]

    while True:
        tw = getUserTweets(max_id)
        if tw and len(tw)>0:
            twitter[len(twitter):] = tw
            count=count-1
            max_id=str(twitter[len(twitter)-1]['id'])
            print('Count:',len(twitter))
        else:
            break

    rt=[[[] for j in xrange(24)] for i in xrange(7)]

    for i in twitter:
        day,hour=extract_time(i['time'])
        rt[day][hour].append(i['rt'])

    for i,item in enumerate(rt):
        for j,jtem in enumerate(rt[i]):
            rt[i][j]=median(rt[i][j])

    return rt

app = Flask(__name__)

@app.route('/')
def index():
    handle = request.args.get('handle')
    if handle:
        count = get_data(handle)
    return render_template('index.html', **locals())

app.run(debug=True)
