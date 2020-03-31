from db import *
import pandas as pd
from pyecharts.charts import Geo
import re
from config import key, TABLE

'''数据清洗'''
class data_clean(object):

    def __init__(self, table=TABLE, key=key):
        self.key = key
        self.client = MongodbClient()  # 初始化数据库类
        self.client.change_table(table)
        self.datas = pd.DataFrame(self.client.get_all())  # 读取db所有数据并转换为DataFrame类型
        print(self.datas.shape)

        # 重复数据处理（2种情况：内容重复、链接重复）
        job = ['title', 'place', 'salary', 'exp', 'edu', 'company', 'companyinfo', 'companyplace', 'info']
        print('内容重复：', self.datas.duplicated(job).sum())
        print('链接重复：', self.datas.duplicated('link').sum())
        self.datas.drop_duplicates('link')

        # 去除空数据
        print((self.datas.isnull()).sum())
        df_nan = self.datas.loc[self.datas['salary'].isnull()]
        self.datas = self.datas.drop(df_nan.index)

        # 清理脏数据（去除兼职、实习、广告等信息）
        df_dirty_salary = self.datas[self.datas['salary'].str.contains(
            r'(小时|天)+')]
        df_dirty_job_name = self.datas[self.datas['title'].str.contains(
            r'(\*|在家|试用|体验|无需|无须|试玩|红包|实习)+')]
        df_dirty = pd.concat([df_dirty_salary, df_dirty_job_name])
        print('清理的脏数据', df_dirty.shape)
        self.datas = self.datas.drop(df_dirty.index)

        print(self.datas.shape)

    def get_place(self):
        '''地区清洗'''
        # 将地区规整为城市
        citys = self.datas.loc[:, 'place'].str.split("-").str[0]

        # 偏僻城市处理
        geo = Geo()
        for index, city in citys.items():
            if geo.get_coordinate(name=city) == None:
                citys = citys.drop(index)
                print(index, city)
        print(len(citys))

        # 获取每个城市发布的招聘数量
        city = citys.value_counts().sort_values(ascending=True)  # 每个城市数量
        # print(citys.nunique())  # 城市数

        # 地区数据格式为dataframe格式，转换为列表
        num_list = city.values.tolist()
        city = city.reset_index()
        city_list = city.loc[:, 'index'].tolist()
        return city_list, num_list

    def get_edu(self):
        edu = self.datas['edu']
        edu_counts = edu.value_counts()
        print(edu_counts)
        # 数据格式由dataframe转换为列表
        num_list = edu_counts.values.tolist()
        edu_counts = edu_counts.reset_index()
        edu_list = edu_counts.loc[:, 'index'].tolist()
        return edu_list, num_list

    def salary_unify(self, salary):
        '''统一薪资单位'''
        # 网站中的单位有：万/年、千/月、万/月、元/天、元/小时，统一为千/月
        if '-' in salary:  # 针对1-2万/月或者10-20万/年的情况，包含-
            low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
            high_salary = re.findall(re.compile('(\d?\.?\d+)'), salary)[1]
            if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
                low_salary = float(low_salary) / 12 * 10
                high_salary = float(high_salary) / 12 * 10
            elif u'万' in salary and u'月' in salary:
                low_salary = float(low_salary) * 10
                high_salary = float(high_salary) * 10
        else:
            # 针对20万以上/年和100元/天这种情况，不包含-，取最低工资，没有最高工资
            low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
            high_salary = ""
            if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
                low_salary = float(low_salary) / 12 * 10
            elif u'万' in salary and u'月' in salary:
                low_salary = float(low_salary) * 10
            elif u'元' in salary and u'天' in salary:
                low_salary = float(low_salary) / 1000 * 21  # 每月工作日21天
        return low_salary, high_salary

    def get_low_salary(self):
        '''低薪数据'''
        # print((self.datas.salary.str[-3:]).value_counts())

        # 统一数据单位，获取最低薪资
        low_salary = self.datas['salary'].apply(
            self.salary_unify).str[0]

        # 低薪列表
        low_salary = low_salary.value_counts().sort_index()
        low_salary_num = low_salary.values.tolist()
        low_salary_val = low_salary.index.tolist()

        return low_salary_val, low_salary_num

    def get_high_salary(self):
        '''高薪数据'''
        high_salary = self.datas['salary'].apply(
            self.salary_unify).str[1]

        # 高薪列表
        high_salary = high_salary.value_counts().sort_index()
        high_salary_num = high_salary.values.tolist()
        high_salary_val = high_salary.index.tolist()

        return high_salary_val, high_salary_num

    def get_industry(self):
        '''提取第一个行业'''
        self.datas['industry'] = self.datas['companyinfo'].apply(lambda x: x.split("|")[-1].split()[0])
        return self.datas


