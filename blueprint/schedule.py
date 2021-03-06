# -*- coding: utf-8 -*-
import re
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import request, redirect, url_for
from flask import render_template
from flask import Blueprint, jsonify, session
from datetime import datetime, timedelta

from common import db

bp_schedule = Blueprint('bp_schedule', __name__,
                    template_folder='templates')

@bp_schedule.route('s')
def schedules():
    items = []
    schedules = db.schedules.find()
    for schedule in schedules:
        items.append({
            'id': str(schedule['_id']),
            'title': schedule['user'],
            'start': schedule['from_date'].strftime('"%Y-%m-%d"'),
            'end': schedule['to_date'].strftime('"%Y-%m-%d"'),
            'color': get_user_color(schedule['user'])
        })
    return dumps(items)


@bp_schedule.route('')
def schedule():
    schedules = list(db.schedules.find())
    return render_template('schedules.html', schedules=schedules)


@bp_schedule.route('', methods=['POST'])
def add_schedule():
    if 'username' in session and session['is_admin']:
        if request.form.has_key('from_date') and request.form['from_date']\
            and request.form.has_key('to_date') and request.form['to_date']:
            schedule = {
                'memo': request.form['memo'],
                'user': session['username'],
                'from_date': datetime.strptime(request.form['from_date'], "%Y-%m-%d"),
                'to_date': datetime.strptime(request.form['to_date'], "%Y-%m-%d") + timedelta(days=1)
            }
            db.schedules.insert(schedule)
            return redirect('/schedule')
    return redirect('/schedule')


@bp_schedule.route('/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id=None):
    if 'username' in session and session['is_admin'] and schedule_id != None:
        schedule = db.schedules.find_one({"_id":ObjectId(schedule_id)})
        if schedule:
            db.schedules.delete_one(schedule)
    schedules = list(db.schedules.find())
    return render_template('schedules.html', schedules=schedules)


def get_user_color(username):
    user = db.users.find_one({'username': username})
    if user:
        return user['color']
    return 'gray'
