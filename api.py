#!/usr/bin/env python2
# -*- coding: utf8 -*-
# from __future__ import unicode_literals

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

import requests
import icalendar
import arrow
import types
import config as cfg
import json

FILE = 'events.json'

#
# Functions
#

def get_recurrences(cal_name, dt_start, dt_end, evt):
    print('get_recurrences')
    rrule = evt.get('rrule')
    byday = rrule.get('byday')
    freq = rrule.get('freq')[0]

    until = rrule.get('until')
    if until is not None:
        rec_end = arrow.get(until[0])
    else:
        rec_end = arrow.get().replace(months=+1)

    events = []
    while dt_start < rec_end:
        events.append(get_event(cal_name, dt_start, dt_end, evt))
        # Increment date
        if freq == 'WEEKLY':
            dt_start = dt_start.replace(days=+7)
            dt_end = dt_end.replace(days=+7)
        elif freq == 'MONTHLY':
            dt_start = dt_start.replace(months=+1)
            dt_end = dt_end.replace(months=+1)
        elif freq == 'YEARLY':
            dt_start = dt_start.replace(years=+1)
            dt_end = dt_end.replace(years=+1)
        else:
            dt_start = dt_start.replace(days=+1)
            dt_end = dt_end.replace(days=+1)

    return events


def get_event(cal_name, dt_start, dt_end, evt):
    print('get_event')
    summary = evt.get('summary')
    location = evt.get('location')
    description = evt.get('description')
    dt_start = dt_start.to('Europe/Zurich')
    dt_end = dt_end.to('Europe/Zurich')
    return {
        'cal': cal_name,
        'name': summary,
        'dow': dt_start.datetime.strftime('%A'),
        's_day': dt_start.format('DD'),
        's_month': dt_start.format('MMM'),
        's_month_num': dt_start.format('MM'),
        's_year': dt_start.format('YYYY'),
        's_time': dt_start.format('HH:mm'),
        'e_day': dt_end.format('DD'),
        'e_month': dt_end.format('MMM'),
        'e_year': dt_end.format('YYYY'),
        'e_time': dt_end.format('HH:mm'),
        'timestamp': dt_start.timestamp,
        'location': location,
        'description': description,
    }


def get_calendar(url):
    print('get_calendar')
    name = ''
    events = []
    cal_data = requests.get(url, headers={'User-Agent': cfg.user_agent}).content
    try:
        cal_obj = icalendar.Calendar.from_ical(cal_data)
        cal_name = cal_obj.get('x-wr-calname')
        recent = arrow.now().floor('day').replace(days=-30)  # FIXME: must be yesterday ?
        for e in cal_obj.walk():
            if e.name != 'VEVENT':
                continue
            # Get dates
            try:
                dt_start = arrow.get(e.get('dtstart').dt)
                dt_end = arrow.get(e.get('dtend').dt)
            except TypeError as f:
                dt_start = arrow.Arrow.fromdate(e.get('dtstart').dt)
                dt_end = arrow.Arrow.fromdate(e.get('dtend').dt)
            # Only future or recent events
            if dt_start < recent:
                continue
            # Create and add event
            if isinstance(e.get('rrule'), types.NoneType):
                evt = get_event(cal_name, dt_start, dt_end, e)
                if evt not in events:
                    events.append(evt)
            else:
                for f in get_recurrences(cal_name, dt_start, dt_end, e):
                    if f not in events:
                        events.append(f)
    except IOError as e:
        events.append({'name': e, 'cal': cal_name})
    return events

def get_data():
    print('get_data')

    # Get all events
    events = []
    for cal in cfg.calendars:
        events += get_calendar(cal)
    events = sorted(events, key=lambda i: i['timestamp'])

    # Split according to date range
    today_start = arrow.get().replace(hour=0, minute=0, second=0)
    today_end = today_start.replace(days=+1)
    week_end = today_start.replace(days=+7)

    past_events = [x for x in events if x['timestamp'] <= today_start.timestamp]
    today_events = [x for x in events if x['timestamp'] > today_start.timestamp and x['timestamp'] <= today_end.timestamp]
    week_events = [x for x in events if x['timestamp'] > today_end.timestamp and x['timestamp'] <= week_end.timestamp]
    future_events = [x for x in events if x['timestamp'] > week_end.timestamp]

    data = {
        'past_events':   past_events,
        'today_events':  today_events,
        'week_events':   week_events,
        'future_events': future_events,
    }

    return data

#
#    MAIN
#

if __name__ == '__main__':

    events = get_data()

    f = open(FILE, 'w+')
    f.write(json.dumps(events))
    f.close()

