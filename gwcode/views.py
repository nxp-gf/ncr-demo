#!/usr/bin/env python
#coding=utf-8
from __future__ import unicode_literals
from pyecharts import Bar, Line
from flask import Flask, render_template, request
from random import randint
from flask_bootstrap import Bootstrap
import time, datetime
import db_test

app = Flask(__name__, static_folder='static')
bootstrap = Bootstrap(app)

shelves_num = 2
business_hours_start = '08:00:00'
business_hours_end = '23:00:00'

start_hour = time.strptime(business_hours_start, "%H:%M:%S").tm_hour
end_hour = time.strptime(business_hours_end, "%H:%M:%S").tm_hour

@app.route("/")
def hello():
    return render_template('base.html',
                           title='Home page')

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/store_bar', methods=['GET','POST'])
def store_bar():
    cur_dt = datetime.datetime.now()
    dt_fmt = cur_dt.strftime('%Y-%m-%d') + ' ' + business_hours_start
    #dt_fmt = cur_dt.strftime('%Y-%m') + '-19 08:00:00'

    v1 = db_test.query_overall_history_hour_person_count(dt_fmt, end_hour - start_hour)

    bar = draw_store_bar(cur_dt, v1)
    return render_template('base.html',
                           title='Store Bar Chart',
                           myechart=bar.render_embed(),
                           script_list=bar.get_js_dependencies())

@app.route('/store_line', methods=['GET','POST'])
def store_line():
    cur_dt = datetime.datetime.now()
    dt_fmt = cur_dt.strftime('%Y-%m-%d %H:%M:%S')
    #dt_fmt = cur_dt.strftime('%Y-%m') + '-19 10:00:00'

    v1 = db_test.query_overall_person_multicount(dt_fmt)

    line = draw_store_line(cur_dt, v1)
    return render_template('base.html',
                           title='Store Line Chart',
                           myechart=line.render_embed(),
                           script_list=line.get_js_dependencies())

				   
@app.route('/shelves_bar', methods=['GET','POST'])
def shelves_bar():
    cur_dt = datetime.datetime.now()
    dt_fmt = cur_dt.strftime('%Y-%m-%d') + ' ' + business_hours_start
    #dt_fmt = cur_dt.strftime('%Y-%m') + '-19 08:00:00'

    values = []
    for i in range(1, shelves_num + 1):
        v = db_test.query_shelf_history_hour_person_count(i, dt_fmt, end_hour - start_hour)
        values.append(v)

    bar = draw_shelves_bar(cur_dt, values)
    return render_template('base.html',
                           title='Shelves Bar Chart',
                           myechart=bar.render_embed(),
                           script_list=bar.get_js_dependencies())

@app.route('/shelves_line', methods=['GET','POST'])
def shelves_line():
    cur_dt = datetime.datetime.now()
    dt_fmt = cur_dt.strftime('%Y-%m-%d %H:%M:%S')
    #dt_fmt = cur_dt.strftime('%Y-%m') + '-19 10:00:00'

    values = []
    for i in range(1, shelves_num + 1):
        v = db_test.query_shelf_person_multicount(i, dt_fmt)
        values.append(v)

    line = draw_shelves_line(cur_dt, values)
    return render_template('base.html',
                           title='Shelves Line Chart',
                           myechart=line.render_embed(),
                           script_list=line.get_js_dependencies())

def draw_store_line(dt, v):
    attr = []
    for i in range(-4, 1):
        offset = datetime.timedelta(minutes=i)
        dtf = (dt + offset).strftime("%H:%M")
        attr.append(dtf)

    line = Line(dt.date())
    line.add("Store-1", attr, v, is_smooth=True, mark_point=["max", "min"])
    return line

def draw_store_bar(dt, v):
    attr = []
    for i in range(start_hour, end_hour):
        t = str(i) + ':00'
        attr.append(t)

    bar = Bar(dt.date())
    bar.add("Store-1", attr, v, mark_line=["average"], mark_point=["max", "min"])
    return bar


def draw_shelves_line(dt, array):
    attr = []
    for i in range(-4, 1):
        offset = datetime.timedelta(minutes=i)
        dtf = (dt + offset).strftime("%H:%M")
        attr.append(dtf)

    j = 1
    line = Line(dt.date())
    for i in array:
        name = "Shelf-" + str(j)
        j = j + 1
        line.add(name, attr, i, is_smooth=True, mark_point=["max", "min"])

    return line

def draw_shelves_bar(dt, array):
    attr = []
    for i in range(start_hour, end_hour):
        t = str(i) + ':00'
        attr.append(t)

    j = 1
    bar = Bar(dt.date())
    for i in array:
        name = "Shelf-" + str(j)
        j = j + 1
        bar.add(name, attr, i, mark_line=["average"], mark_point=["max", "min"])

    return bar

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
