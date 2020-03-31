from pyecharts.charts import Pie, Geo, Funnel, Bar  # 地图构造方法
from pyecharts import options as opts  # 配置入口模块
from pyecharts.globals import ChartType, ThemeType
from pyecharts.faker import Faker
from data_clean import data_clean
from config import key


'''工作分布图'''
class Job_show(object):

    def __init__(self):
        self.data_clean = data_clean()
        self.place_data = self.data_clean.get_place()
        self.edu_data = self.data_clean.get_edu()

    #地理图
    def place_geo(self):
        city_list, num_list = self.place_data[0], self.place_data[1]
        title = key + "工作分布图"

        # 绘制城市地理图
        place_geo = (
            Geo(init_opts=opts.InitOpts(width='600px', height='500px'))
            .add_schema(maptype="china")
            .add("", list(zip(city_list, num_list)), type_=ChartType.EFFECT_SCATTER, )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=num_list[-1], pos_left='8%', is_piecewise=True),
                title_opts=opts.TitleOpts(title=title, subtitle='\n数据来源：前程无忧', pos_left='15%'),
            )
        )
        return place_geo

    def place_proportion(self):
        city_list, num_list = self.place_data[0], self.place_data[1]
        title = key + "&城市-漏斗图"
        #绘制工作地点数量漏斗图
        place_proportion=(
            Funnel(init_opts=opts.InitOpts(width='400px', height='400px'))
            .add("", list(zip(city_list, num_list)), label_opts=opts.LabelOpts(position="inside", )) # 加上数值 formatter= '{b}: {@city_list}'),
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title, pos_left='center'),
                legend_opts=opts.LegendOpts(orient='vertical', pos_left='left'),
            )
        )
        # place_proportion.render(r'C:\Users\润敏\Desktop\工作地点漏斗图.html')
        return place_proportion

    #柱状图
    def place_bar(self):
        city_list, num_list = self.place_data[0], self.place_data[1]
        title = key + "职位前20名城市"
        city_list = city_list[-20:]
        num_list = num_list[-20:]
        job_bar = (
            Bar(init_opts=opts.InitOpts(width='550px', height='500px'))
            .add_xaxis(city_list)
            .add_yaxis("", num_list)
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(title_opts=opts.TitleOpts(title=title),)
        )
        return job_bar

    #学历要求
    def edu_pie(self):
        edu_list, num_list = self.edu_data[0], self.edu_data[1]
        edu_pie = (
            Pie()
            .add(
                "学历要求",
                [list(z) for z in zip(edu_list, num_list)],
                radius=["40%", "55%"],
                label_opts=opts.LabelOpts(
                    formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                    background_color="#eee",
                    border_color="#aaa",
                    border_width=1,
                    border_radius=4,
                    rich={
                        "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                        "abg": {
                            "backgroundColor": "#e3e3e3",
                            "width": "100%",
                            "align": "right",
                            "height": 22,
                            "borderRadius": [4, 4, 0, 0],
                        },
                        "hr": {
                            "borderColor": "#aaa",
                            "width": "100%",
                            "borderWidth": 0.5,
                            "height": 0,
                        },
                        "b": {"fontSize": 16, "lineHeight": 33},
                        "per": {
                            "color": "#eee",
                            "backgroundColor": "#334455",
                            "padding": [2, 4],
                            "borderRadius": 2,
                        },
                    },
                ),
            )
            .set_global_opts(title_opts=opts.TitleOpts(title=key+"职位的学历要求"),
                             legend_opts=opts.LegendOpts(pos_left="left", pos_top='20%', orient="vertical"))
        )
        return edu_pie
