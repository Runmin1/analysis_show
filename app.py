from flask import Flask,redirect,url_for,render_template
import analysis_show
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
# from flask_mongoengine import MongoEngine
# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))


app = Flask(__name__)
job_show = analysis_show.Job_show()

@app.route('/')
@app.route('/<name>')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/place_Geo')
def place_geo():
    place_show = job_show.place_geo()
    return Markup(place_show.render_embed())

@app.route('/place_Funnel')
def place_funnel():
    place_show = job_show.place_proportion()
    return Markup(place_show.render_embed())

@app.route('/place_Bar')
def place_bar():
    place_show = job_show.place_bar()
    return Markup(place_show.render_embed())

@app.route('/edu_pie')
def edu_pie():
    edu_show = job_show.edu_pie()
    return Markup(edu_show.render_embed())

if __name__ == '__main__':
    app.run(debug=True)
