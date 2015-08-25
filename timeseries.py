#!/usr/bin/python
# -*- coding: utf-8 -*- 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import sqlalchemy as sq
import numpy as np
import datetime

engine = sq.create_engine("sqlite:///stats.sqlite")
df = pd.read_sql_table("stats", engine)
df = df.set_index(pd.DatetimeIndex(df['timestamp']))

today = datetime.date.today()
from_date = today - datetime.timedelta(weeks=2)
df = df[from_date:]

def f(x):
    x['tvalue'] = x.index
    x['delta'] = (x['tvalue']-x['tvalue'].shift()).fillna(0)
    x['fb_share_delta'] = (x['fb_share_count']-x['fb_share_count'].shift()).fillna(0)
    x['fb_share_delta'] = x['fb_share_delta'] / x['delta'].astype(np.int64).astype(np.float64)
    x['fb_share_delta'] = (x['fb_share_delta'] / float(1e-12)).fillna(0)

    return x

df = df[['url', 'fb_share_count']].groupby('url').apply(f)
print df[df['url'] == "http://www.dn.se/ekonomi/sparexpert-har-ar-spararna-som-borde-dra-sig-ur-borsen/"]
"""
for source, df in df.groupby(['url']):
    if source == "http://www.dn.se/ledare/signerat/peter-wolodarski-hat-kan-snabbt-forgifta-ett-samhallsklimat/":
        print source, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #print zip(df.index.astype(np.int64), df['tw_count'].values)
        df['tvalue'] = df.index
        df['delta'] = (df['tvalue']-df['tvalue'].shift()).fillna(0)
        df['fb_share_delta'] = (df['fb_share_count']-df['fb_share_count'].shift()).fillna(0)
        df['fb_share_delta'] = df['fb_share_delta'] / df['delta'].astype(np.int64).astype(np.float64)
        df['fb_share_delta'] = (df['fb_share_delta'] / float(1e-12)).fillna(0)
        print df


        fig, ax = plt.subplots()

        df['fb_share_delta'].plot(ax=ax, legend=False, style='-o')
        for line in ax.lines:
            line.set_linewidth(2)
            line.set_markersize(8)
            line.set_markeredgecolor('none')
            xdata, ydata = line.get_data()

        ax.legend(loc='upper center', bbox_to_anchor=(0.51, 1.11),
                  ncol=6, fancybox=False, shadow=False, fontsize=8,
                  frameon=False)

        #ax.set_ylim(0.15,0.7)
        #fig.savefig("graphs/timeseries.png")
        #print "Saving graph by day"

"""