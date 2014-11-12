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

from flask import Flask, render_template, request, Response, redirect, session
import requests, icalendar, arrow
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
# Functions
#

def get_calendar(url):
    name = ''
    events = []
    cal_data = requests.get(url, headers={'User-Agent': cfg.user_agent}).content
    try:
        cal_obj = icalendar.Calendar.from_ical(cal_data)
        name = cal_obj.get('x-wr-calname')
        yesterday = arrow.now().floor('day').replace(days=-1)
        for e in cal_obj.walk():
            if e.name != 'VEVENT':
                continue
            summary = e.get('summary')
            date_start = e.get('dtstart')
            date_end = e.get('dtend')
            location = e.get('location')
            desc = e.get('description')
            if arrow.Arrow.fromdate(date_start.dt) < yesterday:
                continue
            evt = {
                'cal': name,
                'name': summary,
                's_day': date_start.dt.strftime('%d'),
                's_month': date_start.dt.strftime('%b'),
                's_year': date_start.dt.strftime('%Y'),
                's_time': date_start.dt.strftime('%H:%M'),
                'e_day': date_end.dt.strftime('%d'),
                'e_month': date_end.dt.strftime('%b'),
                'e_year': date_end.dt.strftime('%Y'),
                'e_time': date_end.dt.strftime('%H:%M'),
                'timestamp': arrow.Arrow.fromdate(date_start.dt).timestamp,
                'location': location,
                'description': desc,
            }
            if evt not in events: # Some events appear twice
                events.append(evt)
    except IOError, e:
        events.append({'name': e, 'cal': name})
    return events

#
#    PAGES
#

@app.route('/')
def home():
    session['username'] = random.getrandbits(32)
    events = []
    for cal in cfg.calendars:
        events += get_calendar(cal)
    events = sorted(events, key=lambda i: i['timestamp'])
    return render_template('index.html', data={'events': events})

#
#    MAIN
#

if __name__ == '__main__':
    app.run()

