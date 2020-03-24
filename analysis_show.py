from db import *
import pandas as pd
from pyecharts.charts import Map, Geo, Funnel, Bar  # 地图构造方法
from pyecharts import options as opts  # 配置入口模块
from pyecharts.globals import ChartType, SymbolType


'''工作分布图'''
class Job_Geo_show(object):

    def __init__(self,table,key):
        self.key = key
        self.client = MongodbClient()  # 初始化数据库类
        self.client.change_table(table)
        self.datas = pd.DataFrame(list(self.client.get_all()))  # 读取db所有数据并转换为DataFrame类型
        print(self.datas.shape)

    #数据处理
    def place_list(self, datas):
        #将地区规整为城市
        citys = datas.loc[:, 'place'].str.split("-").str[0]

        # 获取每个城市发布的招聘数量
        print(citys.nunique())  # 城市数
        city = citys.value_counts()  # 每个城市数量
        print(city)

        #地区数据格式为dataframe格式，转换为列表
        num_list = city.values.tolist()
        city = city.reset_index()
        city_list = city.loc[:, 'index'].tolist()
        return city_list, num_list

    #地理图
    def Job_Geo(self):
        city_list, num_list = self.place_list()
        title = self.key + "工作分布图"
        #绘制城市地理图
        Job_Geo=(
            Geo(init_opts=opts.InitOpts(width='600px', height='500px'))
            .add_schema(maptype="china")
            .add("", list(zip(city_list, num_list)), type_=ChartType.EFFECT_SCATTER,)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=num_list[0], pos_left='8%', is_piecewise=True),
                title_opts=opts.TitleOpts(title=title, subtitle='\n数据来源：前程无忧', pos_left='15%'),
            )
        )
        return Job_Geo
        # Job_Geo.render(r'C:\Users\润敏\Desktop\大数据工作城市分布图.html')

    def place_proportion(self):
        city_list, num_list= self.place_list()
        title = self.key + "&城市-漏斗图"
        #绘制工作地点数量漏斗图
        place_proportion=(
            Funnel(init_opts=opts.InitOpts(width='400px', height='400px'))
            .add("", list(zip(city_list, num_list)), label_opts=opts.LabelOpts(position="inside", )) # 加上数值 formatter= '{b}: {@city_list}'),
            .set_global_opts(
                title_opts=opts.TitleOpts(title="工作地点数量漏斗图", pos_left='center'),
                legend_opts=opts.LegendOpts(orient='vertical', pos_left='left'),
            )
        )
        # place_proportion.render(r'C:\Users\润敏\Desktop\工作地点漏斗图.html')
        return place_proportion

    #柱状图
    def job_bar(self):
        city_list, num_list = self.place_list()
        title = self.key + "&城市-柱状图"
        city_list = city_list[::-1]
        num_list = num_list[::-1]
        job_bar = (
            Bar()
            .add_xaxis(city_list)
            .add_yaxis("", num_list)
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )
        return job_bar

class Job_edu_show(object):

    def __init__(self,table,key):
        self.key = key
        self.client = MongodbClient()  # 初始化数据库类
        self.client.change_table(table)
        self.datas = pd.DataFrame(list(self.client.get_all()))  # 读取db所有数据并转换为DataFrame类型
        print(self.datas.shape)

    def edu_analy(self):
        edu = self.datas['edu']
        num = edu.value_counts()
        print(num)