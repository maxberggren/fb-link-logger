web: gunicorn GUIapp.views:app --log-file=-
worker: python keepup.py python scrape.py dn.se
worker: python keepup.py python scrape.py expressen.se 