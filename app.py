from flask import Flask,redirect,url_for,render_template,Response,request
import analysis_show
import salary_pred
from data_clean import data_clean
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

# select = "数据分析"
app = Flask(__name__)


@app.route('/choose', methods=['GET', 'POST'])
def choose():
    global select
    global job_show
    global datas
    global pred
    select = request.form.get('job_select')
    job_show = analysis_show.Job_show(select)
    pred = salary_pred(select)
    datas = data_clean(select)
    return redirect(url_for("nav"))

@app.route('/')
def index():
    return render_template('choose.html')

@app.route('/nav')
@app.route('/<name>')
def nav(name=None):
    counts = datas.get_counts()   # 获取招聘信息总数
    avg, median = datas.place_avg_median()  # 获取招聘信息平均数及中位数
    return render_template('index.html', name=name, counts=counts,avg=avg,median=median)

@app.route('/test')
def test():
    return render_template('test.html')

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

@app.route('/place_salary')
def place_salary():
    place_salary = job_show.place_salary_show()
    return Markup(place_salary.render_embed())

@app.route('/salary_low_high')
def salary_low_high():
    salary_low_high = job_show.salary_bar()
    return Markup(salary_low_high.render_embed())

@app.route('/edu_pie')
def edu_pie():
    edu_show = job_show.edu_pie()
    return Markup(edu_show.render_embed())

@app.route('/edu_salary')
def edu_salary():
    edu_salary = job_show.edu_line()
    return Markup(edu_salary.render_embed())

@app.route('/exp_bar')
def exp_bar():
    edu_show = job_show.exp_bar()
    return Markup(edu_show.render_embed())

@app.route('/exp_salary')
def exp_salary():
    exp_salary = job_show.exp_salary_show()
    return Markup(exp_salary.render_embed())

@app.route('/industry')
def industry():
    industry = job_show.industry_salary_show()
    return Markup(industry.render_embed())

@app.route('/resp_word')
def resp_word():

    with open("responsibility.png", 'rb') as f:
        image = f.read()
    req = Response(image, mimetype="image/jpeg")
    return req

@app.route('/req_word')
def req_word():

    with open("requirement.png", 'rb') as f:
        image = f.read()
    resp = Response(image, mimetype="image/png")
    return resp

@app.route('/pred')
def salary_pred():
    city = request.form.get('city')
    exp = request.form.get('exp')
    edu = request.form.get('edu')
    pred_low, pred_avg = pred.pred(city, exp, edu)

    return render_template('index.html', pred_low=pred_low, pred_avg=pred_avg)


if __name__ == '__main__':
    app.run(debug=True)
