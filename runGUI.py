#!/usr/bin/python
# -*- coding: utf-8 -*-
from GUIapp import app

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5011)
    
