#TODO: WHEN X CREATED AN EVENT
import json
import Queue
import threading
import requests
import ConfigParser
from requests_oauthlib import OAuth1
from flask import Flask, render_template, request

def get_data(handle):
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    app_key             = Config.get('Twitter','app_key')
    app_secret          = Config.get('Twitter','app_secret')
    access_token        = Config.get('Twitter','access_token')
    access_token_secret = Config.get('Twitter','access_token_secret')

    def getTweets(max_id):
        url                 = 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name='+handle+'&count=200'
        if max_id:
            url += '&max_id='+max_id
        auth                = OAuth1(app_key,app_secret,access_token,access_token_secret)
        result              =  requests.get(url,auth=auth)
        # print result.text
        result = result.json()
        result = [{'id':x['id'],'time':x['created_at']} for x in result]

        if max_id:
            return result[1:]
        return result
    days={'Sun':0,'Mon':1,'Tue':2,'Wed':3,'Thu':4,'Fri':5,'Sat':6,}
    def extract_time(S):
        day = days[S[:3]]
        hour = int(S[11:13])
        return day,hour
    # extract_time('Sun Jun 01 06:19:10 +0000 2014')

    # twitter= result.json()
    # print twitter[199]['id']
    max_id=None
    count=5
    twitter=[]

    while count>0:
        twitter[len(twitter):] = getTweets(max_id)
        max_id=str(twitter[len(twitter)-1]['id'])
        count=count-1
        print len(twitter)
    # print twitter

    count=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
           [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

    for i in twitter:
        day,hour=extract_time(i['time'])
        count[day][hour]+=1
    return count

app = Flask(__name__)

@app.route('/')
def index():
    handle = request.args.get('handle')
    if handle:
        count = get_data(handle)
    return render_template('index.html', **locals())
