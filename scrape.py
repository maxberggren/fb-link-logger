#!/usr/bin/python
# -*- coding: utf-8 -*- 

import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import requests
import re
import warnings
import urllib2
import httplib
from socket import error as SocketError
from progressbar import ProgressBar, ETA, AnimatedMarker
import dataset
import datetime
import time
from random import shuffle
import json
import time
import sys
import os
from dateutil.parser import parse as parse_date 

catch_errors = (urllib2.HTTPError, 
                urllib2.URLError, 
                httplib.BadStatusLine, 
                httplib.IncompleteRead, 
                SocketError, 
                UnicodeEncodeError, 
                ValueError)

def get_links(url, restrict_to, deeper=True, limit=False):
    """ Get all links from a webpage """


    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, "lxml")
    
    links = set()
    for a in soup.find_all('a', href=True):
        try:
            if ((a['href'][0] == "/" 
                 or restrict_to in a['href']) 
                and len(a['href']) > 5
                and "mailto:" not in a['href']):

                if a['href'][0] == "/":
                    links.update(["http://www." + restrict_to + a['href']])
                else:
                    links.update([a['href']])

                if limit and len(links) > limit:
                    break
        except Exception:
            pass
   
    if deeper:
        next_depth_links = set()
        pbar = ProgressBar(term_width=60)

        i = 0
        for link in pbar(links):
            i += 1
            next_depth_links.update(get_links(link, 
                                              restrict_to=restrict_to, 
                                              deeper=False))
        links.update(next_depth_links)

    return list(links)



def get_stats(url):
    data = {}

    try:
        # Facebook statistics
        r = requests.get('https://api.facebook.com/method/links.getStats?urls={}&format=json'.format(url))
        result = json.loads(r.text)
        result = result[0]
        data['fb_comment_count'] = result['comment_count']
        data['fb_like_count'] = result['like_count']
        data['fb_share_count'] = result['share_count']

        # Twitter statistics
        r = requests.get('http://urls.api.twitter.com/1/urls/count.json?url={}'.format(url))
        result = json.loads(r.text)
        data['tw_count'] = result['count']

        time.sleep(1)
    except (ValueError, KeyError):
        data = None

    return data

def get_major_links(url):
    short_name = url.split("://")[-1].replace("www.", "")
    return get_links(url, restrict_to=short_name, limit=10)

def get_active_links(db):

    today = datetime.datetime.now()
    from_date = today - datetime.timedelta(hours=6)

    res = db.query('SELECT * FROM stats where timestamp > "' + str(from_date) + '" and source = "'+ site +'"')
    #res = table.find(source=site)
    urls = []
    for row in res:
        #if parse_date(row['timestamp']) > from_date:
        urls.append(row['url'])

    return list(set(urls))

if __name__ == "__main__":  
    db = dataset.connect('sqlite:///stats.sqlite')
    # sqlite:///stats.sqlite
    table = db['stats']

    # This is just for the lib to populate the 
    # appropriate table and columns.
    table.insert(dict(url="temp", 
                 source="temp",
                 timestamp=datetime.datetime.now(), 
                 fb_comment_count=0,
                 fb_like_count=0,
                 fb_share_count=0,
                 tw_count=0))

    # Remove other than the top 10k rows to
    # nog having to pay for heroku postgres.
    #result = db.query('DELETE FROM stats WHERE id NOT IN (SELECT id FROM (select id from stats order by id desc limit 10000) AS x)')

    try:
        site = "http://" + sys.argv[1]
    except:
        site = "http://dn.se"

    pbar = ProgressBar(term_width=60)

    # Get main page links
    links = get_major_links(site)
    # Get links that might be still active
    more_links = get_active_links(db)
    # Let's not query more than we have to 
    links = links + more_links
    links = list(set(links))
    print links

    for link in pbar(links):
        stats = get_stats(link)   

        last_entry = None
        for row in table.find(url=link, _limit=1, order_by='-id'):
            last_entry = row

        if not last_entry and stats:
             table.insert(dict(url=link, 
                               source=site,
                               timestamp=datetime.datetime.now(),
                               **stats))           

        if stats and last_entry: 
            if stats['fb_share_count'] > last_entry['fb_share_count']:     
                # If stats found and already in DB    
                url = last_entry['url']
                diff = stats['fb_share_count'] - last_entry['fb_share_count']
                print "{} +{} social interactions".format(url, diff)

                table.insert(dict(url=link, 
                                  source=site,
                                  timestamp=datetime.datetime.now(),
                                  **stats))
        




