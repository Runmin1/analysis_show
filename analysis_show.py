from pyecharts.charts import Pie, Geo, Funnel, Bar, Line  # 地图构造方法
from pyecharts import options as opts  # 配置入口模块
from pyecharts.components import Image
from pyecharts.globals import ChartType, ThemeType, RenderType
from data_clean import data_clean



'''工作分布图'''
class Job_show(object):

    def __init__(self, key):
        print(key)
        self.data_clean = data_clean(key)
        self.all_data = self.data_clean.get_all()
        self.place_data = self.data_clean.get_place()
        self.edu_data = self.data_clean.get_edu()
        self.low_salary_data = self.data_clean.get_low_salary()
        self.high_salary_data = self.data_clean.get_high_salary()
        self.avg_salary_data = self.data_clean.get_avg_salary()
        self.place_salary_data = self.data_clean.get_place_salary()
        self.exp = self.data_clean.get_exp()
        self.edu_salary = self.data_clean.get_edu_avgsalary()
        self.data_clean.word()


    #地理图
    def place_geo(self):
        city_list, num_list = self.place_data[0], self.place_data[1]

        # 绘制城市地理图
        place_geo = (
            Geo(init_opts=opts.InitOpts(width='550px', height='450px'),
                is_ignore_nonexistent_coord=True)
            .add_schema(maptype="china")
            .add("", list(zip(city_list, num_list)), type_=ChartType.EFFECT_SCATTER, )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=num_list[-1], pos_left='0%', pos_bottom='12%', is_piecewise=False),
                title_opts=opts.TitleOpts(subtitle='\n数据来源：前程无忧', pos_left='15%'),
                # toolbox_opts=opts.ToolboxOpts(),
            )
        )

        return place_geo

    # 地区分布
    def place_bar(self):
        city_list, num_list = self.place_data[0], self.place_data[1]
        city_list = city_list[-20:]
        num_list = num_list[-20:]
        job_bar = (
            Bar(init_opts=opts.InitOpts(width='350px', height='430px'))
            .add_xaxis(city_list)
            .add_yaxis("", num_list)
            .reversal_axis()
            .set_global_opts(datazoom_opts=opts.DataZoomOpts(is_show=False, type_="inside"),yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='#f0f06f')))
            .set_series_opts(label_opts=opts.LabelOpts(position="right"),
                             itemstyle_opts=opts.ItemStyleOpts(color='#f0f06f'),
                             )
        )
        return job_bar

    # 城市需求量Top20的对应薪资
    def place_salary_bar(self):
        place, avg_salary, median_salary, city_num = self.place_salary_data
        place_salary_bar = (
            Bar(init_opts=opts.InitOpts(width='400px', height='600px'))
                .add_xaxis(place)
                .add_yaxis("平均值", avg_salary,)
                .add_yaxis("中值", median_salary, is_selected=False,)
                .reversal_axis()
                .set_series_opts(label_opts=opts.LabelOpts(position="right"),
                                 )
        )
        return place_salary_bar


    # 各城市对应月薪
    def place_salary_show(self):
        place, avg_salary, median_salary, city_num = self.place_salary_data
        place_salary_bar = (
            Line(init_opts=opts.InitOpts(width='350px', height='310px'))
                .add_xaxis(place)
                .add_yaxis("平均值", avg_salary, color='yellow')
                .add_yaxis("中值", median_salary, color='#00cc00')

                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 markline_opts=opts.MarkLineOpts(
                                     data=[opts.MarkLineItem(type_="average", name="平均值"),
                                           ]), )
                .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="数量",
                    position="right",
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                )
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color='#f0f06f')),
                                 datazoom_opts=[
                                     opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                                 yaxis_opts=opts.AxisOpts(name="薪资（千/月）"),
                                 # toolbox_opts=opts.ToolboxOpts(),
                                 )
        )
        city_num = (
            Bar()
                .add_xaxis(place)
                .add_yaxis("职位数量", city_num, yaxis_index=1
                           )
                .set_series_opts(itemstyle_opts=opts.ItemStyleOpts(color='rgba(255,128,128,0.5)'))
        )
        return place_salary_bar.overlap(city_num)

    # 学历要求
    def edu_pie(self):
        edu_list, num_list = self.edu_data[0], self.edu_data[1]
        edu_pie = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='350px', height='280px'))
            .add(
                "学历要求",
                [list(z) for z in zip(edu_list, num_list)],
                radius=["40%", "55%"],
                # label_opts=opts.LabelOpts(
                #     formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                #     background_color="#eee",
                #     border_color="#aaa",
                #     border_width=1,
                #     border_radius=4,
                #     rich={
                #         "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                #         "abg": {
                #             "backgroundColor": "#e3e3e3",
                #             "width": "100%",
                #             "align": "right",
                #             "height": 22,
                #             "borderRadius": [4, 4, 0, 0],
                #         },
                #         "hr": {
                #             "borderColor": "#aaa",
                #             "width": "100%",
                #             "borderWidth": 0.5,
                #             "height": 0,
                #         },
                #         "b": {"fontSize": 16, "lineHeight": 33},
                #         "per": {
                #             "color": "#eee",
                #             "backgroundColor": "#334455",
                #             "padding": [2, 4],
                #             "borderRadius": 2,
                #         },
                #     },
                # ),
            )
            .set_global_opts(
        legend_opts=opts.LegendOpts(pos_left="left", pos_top='20%', orient="vertical"))
        )
        return edu_pie

    # 学历对薪资影响
    def edu_line(self):
        edu, low_salary, high_salary = self.data_clean.get_edu_salary()
        edu_line = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='350px', height='280px'))
                .add_xaxis(edu[:-1])
                .add_yaxis("低薪", low_salary[:-1])
                .add_yaxis("高新", high_salary[:-1])
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 markline_opts=opts.MarkLineOpts(
                                     data=[opts.MarkLineItem(type_="average", name="平均值"),
                                           ]), )
                .set_global_opts(
                                 xaxis_opts=opts.AxisOpts(name="学历",axislabel_opts=opts.LabelOpts(color='#f0f06f')),
                                 yaxis_opts=opts.AxisOpts(name="月薪"),
                                 )
        )
        return edu_line

    # 经验要求
    def exp_bar(self):
        exp_list, num_list = self.exp
        exp_bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='400px', height='250px'))
                .add_xaxis(exp_list[::-1])
                .add_yaxis("", num_list[::-1])

                .set_series_opts(label_opts=opts.LabelOpts(position="top"))
                .set_global_opts(
                datazoom_opts=opts.DataZoomOpts(is_show=False, type_="inside"),
                                 xaxis_opts=opts.AxisOpts(name="工作经验要求",
                                                          axislabel_opts=opts.LabelOpts(rotate=-40, color='#f0f06f')),
                                 yaxis_opts=opts.AxisOpts(name="职位数量"),

                                 )
        )
        return exp_bar

    # 工作经验对月薪的影响
    def exp_salary_show(self):
        exp, low_salary, high_salary = self.data_clean.get_exp_salary()
        exp_salary = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT, width='350px', height='230px'))
                .add_xaxis(exp)
                .add_yaxis("低薪", low_salary)
                .add_yaxis("高薪", high_salary)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 markline_opts=opts.MarkLineOpts(
                                     data=[opts.MarkLineItem(type_="average", name="平均值"),
                                           ]), )
                .set_global_opts(
                                datazoom_opts=opts.DataZoomOpts(is_show=False, type_="inside"),
                                 yaxis_opts=opts.AxisOpts(name="薪资（千/月）"),
                                 xaxis_opts=opts.AxisOpts(
                                     name="工作经验", axislabel_opts=opts.LabelOpts(rotate=-40, color='#fff')),
                                  )
        )
        return exp_salary

    # 薪资分布
    def salary_bar(self):
        val_salary = self.high_salary_data[0]
        num_low_salary = self.low_salary_data[1]
        num_high_salary = self.high_salary_data[1]
        salary_bar = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width='350px', height='200px'))
                .add_xaxis(val_salary)
                .add_yaxis("低薪", num_low_salary)
                .add_yaxis("高薪", num_high_salary)

                .set_series_opts(label_opts=opts.LabelOpts(position="top"),
                                 markpoint_opts=opts.MarkPointOpts(
                                     data=[opts.MarkPointItem(type_="max", name="最大值"),
                                           ]),
                                 )
                .set_global_opts(
                                 datazoom_opts=opts.DataZoomOpts(is_show=False, type_="inside"),
                                 yaxis_opts=opts.AxisOpts(name="数量"),
                                 xaxis_opts=opts.AxisOpts(name="千/月", axislabel_opts=opts.LabelOpts(color='rgb(13, 148, 235)')),
                        )
        )
        return salary_bar

    # 行业薪资
    def industry_salary_show(self):
        industry, salary, num = self.data_clean.get_industry_salary()
        industry_salary = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width='750px', height='270px'))
                .add_xaxis(industry)
                .add_yaxis("平均薪资", salary)

                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 markline_opts=opts.MarkLineOpts(
                                     data=[opts.MarkLineItem(type_="average", name="平均值"),
                                           ]), )
                .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="数量",
                    position="right",
                    splitline_opts=opts.SplitLineOpts(
                        is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=1)
                    ),
                )
            )
                .set_global_opts(
                                 datazoom_opts=[
                                     opts.DataZoomOpts(is_show=False), opts.DataZoomOpts(type_="inside")],
                                 yaxis_opts=opts.AxisOpts(name="薪资（千/月）"),
                                 xaxis_opts=opts.AxisOpts(
                                     name="行业", axislabel_opts=opts.LabelOpts(rotate=-10, color='#f0f06f')),
                                 toolbox_opts=opts.ToolboxOpts(),
                                 )
        )
        num = (
            Bar()
                .add_xaxis(industry)
                .add_yaxis("职位数量", num,
                           yaxis_index=1
                           )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                                 itemstyle_opts=opts.ItemStyleOpts(color='rgba(240, 240, 111,0.5)'))
        )
        return industry_salary.overlap(num)

    # 岗位职责
    def resp_word(self):
        # image = Image()
        # img_src = ("responsibility.png")
        # image.add(
        #     src=img_src,
        #     style_opts={"width": "200px", "height": "200px", "style": "margin-top: 20px"},
        # )
        resp = data_clean.word()[0]

        return resp

    # 岗位要求
    def req_word(self):
        # image = Image()
        # img_src = ("requirement.png")
        # image.add(
        #     src=img_src,
        #     style_opts={"width": "200px", "height": "200px", "style": "margin-top: 20px"},
        # )
        req = data_clean.word()[1]

        return image

