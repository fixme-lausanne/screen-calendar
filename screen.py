#!/usr/bin/env python2
# -*- coding: utf8 -*-
#from __future__ import unicode_literals

'''
This file is part of FIXME Screen Calendar.

FIXME Events is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FIXME Events is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with FIXME Events. If not, see <http://www.gnu.org/licenses/>.
'''

from flask import Flask, render_template, request, Response, url_for, redirect, session
from urllib import urlencode
import random, sys
import config as cfg

from IPython import embed
# embed()

app = Flask(__name__)
if cfg.secret_key == '':
    print 'configure secret_key!'
    sys.exit(0)
app.debug = True # FIXME: remove on production
app.secret_key = cfg.secret_key

#
#    PAGES
#

@app.route('/')
def home():
    session['username'] = random.getrandbits(32)
    return render_template('index.html', data={
        'css': url_for('static', filename='style.css'),
    })

#
#    MAIN
#

if __name__ == '__main__':
    app.run()

