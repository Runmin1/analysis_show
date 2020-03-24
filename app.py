from flask import Flask,redirect,url_for,render_template
import analysis_show
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
# from flask_mongoengine import MongoEngine
# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))


app = Flask(__name__)


# @app.route('/<key>')
# def job_analysis(key):
#     return 'Hellow %s!' % key

#localhost:5000/user/admin  显示Hello admin
@app.route('/user')
def hello(name):
    if name =='admin':
        return redirect(url_for('job_analysis'))

@app.route('/')
def index():
    # job_geo_show = analysis_show.Job_Geo_show('web_developer','前端开发')
    # job_geo = job_geo_show.Job_Geo()
    # job_funnel = job_geo_show.place_proportion()
    # return render_template('index.html', Job_Geo=job_geo.render_embed(), place_proportion=job_funnel.dump_options())
    return render_template('index.html')

@app.route('/Job_Geo')
def Job_Geo():
    job_geo_show = analysis_show.Job_Geo_show('web_developer','前端开发')
    job_geo = job_geo_show.Job_Geo()
    return Markup(job_geo.render_embed())

@app.route('/Job_Funnel')
def Job_Funnel():
    job_funnel_show = analysis_show.Job_Geo_show('web_developer', '前端开发')
    job_funnel = job_funnel_show.place_proportion()

    return Markup(job_funnel.render_embed())

@app.route('/Job_Bar')
def Job_Bar():
    job_bar_show = analysis_show.Job_Geo_show('web_developer', '前端开发')
    job_bar = job_bar_show.job_bar()

    return Markup(job_bar.render_embed())

if __name__ == '__main__':
    app.run(debug=True)
