#!/usr/bin/python
# -*- coding: utf-8 -*-

from GUIapp import app
from flask import Flask, jsonify, make_response, request, render_template, redirect, url_for
from werkzeug import secure_filename
 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import sqlalchemy as sq
import numpy as np
import datetime
from sqlite_cache import SqliteCache

cache = SqliteCache("cache.sqlite") 

@app.route('/', methods=['GET'])
@app.route('/<source>', methods=['GET'])
def hej(source="dn.se"):   

    if cache.get(source): # Found in cache
        xs, columns, today = cache.get(source)
    else:
        engine = sq.create_engine("sqlite:///stats.sqlite")
        df = pd.read_sql_table("stats", engine)
        df = df.set_index(pd.DatetimeIndex(df['timestamp']))
        df = df[df['source'] == "http://" + source]

        if df.empty:
            return render_template("index.html", xs=None, columns=None, today=None)

        today = datetime.date.today()
        from_date = today - datetime.timedelta(days=1)

        def f(x):
            # Set index to column
            x['tvalue'] = x.index
            # Timedelta between rows
            x['tdelta'] = (x['tvalue']-x['tvalue'].shift()).fillna(0)
            # Facebook sharedelta between rows
            x['sum'] = x['fb_share_count'] + x['fb_like_count'] + x['fb_comment_count'] + x['tw_count']
            x['sum_delta'] = (x['sum'] - x['sum'].shift()).fillna(0)
            # Calc shares per minute
            x['fb_share_per_minute'] = x['sum_delta'] / x['tdelta'].astype(np.int64).astype(np.float64)
            x['fb_share_per_minute'] = (x['fb_share_per_minute'] / float(1e-12)).fillna(0)

            return x

        df = df.groupby('url').apply(f)

        def get_top_articles(d, n=30):
            grouping = d.groupby("url")
            merged = grouping['fb_share_per_minute'].agg([np.max])
            merged_sorted = merged.sort(['amax'], ascending=False)
            merged_sorted = merged_sorted.head(n).iloc[2:]
            return merged_sorted.index.values

        def resample(ts, how="1H"):
            rs = ts.resample(how, how=np.max)
            rs = rs.fillna(method='backfill')
            return rs

        fig, ax = plt.subplots(figsize=(17,12))
        top_articles = get_top_articles(df, n=25)
        colors = cm.Paired(np.linspace(0, 1, len(top_articles)))

        xs = {url: 'x' + str(i+1) for i, url in enumerate(top_articles)}
        inv_xs = {v: k for k, v in xs.items()}

        timeseries = []
        data = []
        for url, color in zip(top_articles, colors):

            def correct_timestamps(timestamps):
                correct_timestamps = []
                for ts in timestamps:
                    ts = str(ts)
                    day = ts.split("T")[0]
                    hour = ts.split("T")[1][0:5]
                    correct_timestamps.append(day + " " + hour)

                return correct_timestamps 

            timestamps = resample(df[df['url'] == url]['fb_share_per_minute']).index.values
            timestamps = correct_timestamps(timestamps)
            data.append([xs[url]] + timestamps)

            url_title = [url.split("/")[-2]]
            cpms = [str(d) for d in list(resample(df[df['url'] == url]['fb_share_per_minute']).values)]
            timeseries.append([url] + cpms)
            
        columns = data + timeseries 
        cache.set(source, (xs, columns, today), timeout=60*60) 

    return render_template("index.html", xs=xs, columns=columns, today=today)

