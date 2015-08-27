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
from subprocess import call


if __name__ == "__main__":  

    while True:
        call("git add . && git commit -m 'more sqlite data' && git push heroku master".split())
        time.sleep(60*60)
        




