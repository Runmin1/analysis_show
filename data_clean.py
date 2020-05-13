from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import jieba
import matplotlib.pyplot as plt
from db import *
import pandas as pd
import numpy as np
import re
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS

class data_clean(object):

    def __init__(self, key):
        self.key = key
        table = key
        print("data_clean", key, table)
        self.client = MongodbClient()  # 初始化数据库类
        self.client.change_table(table)
        self.datas = pd.DataFrame(self.client.get_all())  # 读取db所有数据并转换为DataFrame类型
        # print(self.datas.shape)
        # 只保留职位名有数据或分析的职位
        if key=="数据分析":
            self.datas = self.datas[self.datas.title.str.contains(r'.*?数据.*?')]

        print(self.datas.shape)
        # 重复数据处理（2种情况：内容重复、链接重复）
        job = ['title', 'place', 'salary', 'exp', 'edu', 'company', 'companyinfo', 'companyplace', 'info']
        # print('内容重复：', self.datas.duplicated(job).sum())
        # print('链接重复：', self.datas.duplicated('link').sum())
        self.datas.drop_duplicates('link')

        # 去除空数据(薪资)
        # print((self.datas.isnull()).sum())
        df_nan_salary = self.datas.loc[self.datas['salary'].isnull()]
        df_nan_info = self.datas.loc[self.datas['info'].isnull()]
        self.datas = self.datas.drop(df_nan_salary.index)
        self.datas = self.datas.drop(df_nan_info.index)

        # 清理脏数据（去除兼职、实习、广告等信息）
        df_dirty_salary = self.datas[self.datas['salary'].str.contains(
            r'(小时|天)+')]
        df_dirty_job_name = self.datas[self.datas['title'].str.contains(
            r'(\*|在家|试用|体验|无需|无须|试玩|红包|实习)+')]
        df_dirty = pd.concat([df_dirty_salary, df_dirty_job_name])
        # print('清理的脏数据', df_dirty.shape)
        self.datas = self.datas.drop(df_dirty.index)

        # 地区清洗-将地区规整为城市
        self.datas['citys'] = self.datas.loc[:, 'place'].str.split("-").str[0]

        # 薪资清洗-统一薪资单位
        self.datas['low_salary'] = self.datas['salary'].apply(
            self.salary_unify).str[0]
        self.datas['high_salary'] = self.datas['salary'].apply(
            self.salary_unify).str[1]
        self.datas['avg_salary'] = self.datas['salary'].apply(
            self.salary_unify).str[2]

        # 行业清洗
        '''提取第一个行业'''
        self.datas['industry'] = self.datas['companyinfo'].apply(
            lambda x: x.split("|")[-1].split()[0])

        print(self.datas.shape)

    def salary_unify(self, salary):
        '''统一薪资单位'''
        # 网站中的单位有：万/年、千/月、万/月、元/天、元/小时，统一为千/月
        if '-' in salary:  # 针对1-2万/月或者10-20万/年的情况，包含-
            low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
            high_salary = re.findall(re.compile('(\d?\.?\d+)'), salary)[1]
            low_salary = float(low_salary)
            high_salary = float(high_salary)
            if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
                low_salary = low_salary / 12 * 10
                high_salary = high_salary / 12 * 10
            elif u'万' in salary and u'月' in salary:
                low_salary = low_salary * 10
                high_salary = high_salary * 10
        else:
            # 针对20万以上/年和100元/天这种情况，不包含-，取最低工资，没有最高工资
            low_salary = re.findall(re.compile('(\d*\.?\d+)'), salary)[0]
            high_salary = 0
            low_salary = float(low_salary)
            if u'万' in salary and u'年' in salary:  # 单位统一成千/月的形式
                low_salary = low_salary / 12 * 10
            elif u'万' in salary and u'月' in salary:
                low_salary = low_salary * 10
            elif u'元' in salary and u'天' in salary:
                low_salary = low_salary / 1000 * 21  # 每月工作日21天
        low_salary = round(low_salary, 1)
        high_salary = round(high_salary, 1)
        if high_salary == 0:
            avg_salary = low_salary
        else:
            avg_salary = (low_salary + high_salary) / 2

        return low_salary, high_salary, avg_salary

    # 将df 数据转为 列表
    def to_list(self, datas, sort=None):
        datas = datas.value_counts()
        if sort == 'i':
            datas = datas.sort_index()
        elif sort == 'v' or sort == 'vf':
            datas = datas.sort_values()
        elif sort == 'vt':
            datas = datas.sort_values(ascending=True)

        datas_num = datas.values.tolist()
        datas = datas.reset_index()
        datas_val = datas.loc[:, 'index'].tolist()
        return datas_val, datas_num

    def get_all(self):
        datas = self.datas
        return datas

    def get_counts(self):
        counts = self.datas.shape[0]
        return counts

    def place_avg_median(self):
        counts = self.datas.shape[0]   #招聘信息总数
        num = self.datas['citys'].nunique()  # 城市数
        avg = round(counts / num,0)
        city_list = self.datas['citys'].value_counts(
        ).sort_values(ascending=True).values.tolist()  #城市需求排序列表
        half = len(city_list) // 2
        median = round((city_list[half] + city_list[~half]) / 2,0)

        return avg, median


    def get_place(self):
        '''地区'''
        # 获取每个城市发布的招聘数量
        city = self.datas['citys'].value_counts(
        ).sort_values(ascending=True)  # 每个城市数量
        # 地区数据格式为dataframe格式，转换为列表
        num_list = city.values.tolist()
        city = city.reset_index()
        city_list = city.loc[:, 'index'].tolist()
        return city_list, num_list

    def get_edu(self):
        edu = self.datas['edu']
        # 数据格式由dataframe转换为列表
        edu_list, num_list = self.to_list(edu)
        return edu_list, num_list

    def get_exp(self):
        exp = self.datas['exp']
        exp_list, num_list = self.to_list(exp)
        return exp_list, num_list

    def salary_category(self, datas):
        # 薪资分组
        salary_max = datas.max()
        bin = [0, 4, 5, 6, 8, 10, 12, 15, 20,
               25, 30, 40, 100]
        salary = pd.cut(datas.values, bin, labels=[
            str(bin[i]) + '-' + str(bin[i + 1]) for i in range(len(bin) - 1)])
        return salary

    def get_low_salary(self):
        '''低薪数据'''
        # 分组依据
        low_salary = self.salary_category(self.datas['low_salary'])
        # 低薪列表
        low_salary_val, low_salary_num = self.to_list(low_salary)
        return low_salary_val, low_salary_num

    def get_high_salary(self):
        '''高薪数据'''
        # 分组依据
        high_salary = self.salary_category(self.datas['high_salary'])
        # 高薪列表
        high_salary_val, high_salary_num = self.to_list(high_salary)

        return high_salary_val, high_salary_num

    def get_avg_salary(self):
        '''平均薪资数据'''
        # 分组依据
        avg_salary = self.salary_category(self.datas['avg_salary'])
        # 平均薪资列表
        avg_salary_val, avg_salary_num = self.to_list(avg_salary)

        return avg_salary_val, avg_salary_num

    def get_industry_salary(self):
        salary_industry = self.datas.groupby(
            by='industry')['avg_salary'].mean().round(1)  # 平均值
        num = self.datas['industry'].value_counts()
        salary_industry = pd.concat(
            [salary_industry, num], axis=1)
        salary_industry = salary_industry.sort_values(by='industry')
        avg_salary = salary_industry.avg_salary.tolist()
        num = salary_industry.industry.tolist()
        industry = salary_industry.index.tolist()

        return industry, avg_salary, num

    def get_place_salary(self):
        avg_salary_place = pd.DataFrame({"mean": np.round((self.datas.groupby(
            by='citys')['avg_salary'].mean()), 1)})  # 平均值
        median_salary_place = pd.DataFrame({"median": np.round((self.datas.groupby(
            by='citys')['avg_salary'].median()), 1)})  # 中位数
        city_num = self.datas['citys'].value_counts()
        salary_place = pd.concat(
            [avg_salary_place, median_salary_place, city_num], axis=1)
        salary_place = salary_place.sort_values(by='citys',
                                                ascending=False)[:20]
        avg_salary = salary_place['mean'].values.tolist()
        median_salary = salary_place['median'].values.tolist()
        city_num = salary_place['citys'].values.tolist()
        place = salary_place.index.tolist()
        return place, avg_salary, median_salary, city_num

    def get_edu_avgsalary(self):
        salary_edu = self.datas.groupby(
            by='edu')['avg_salary'].mean().round(1)  # 平均值
        salary_edu = salary_edu.sort_values()
        avg_salary = salary_edu.values.tolist()
        edu = salary_edu.index.tolist()
        return edu, avg_salary

    def get_edu_salary(self):
        salary_edu = self.datas[['edu', 'low_salary', 'high_salary']].groupby(
            by='edu').mean()  # 平均值
        list_custom = ['中技', '中专', '高中', '大专', '本科', '硕士', '博士']
        salary_edu['index'] = salary_edu.index
        salary_edu['index'] = salary_edu['index'].astype('category')
        # inplace = True，使 recorder_categories生效
        salary_edu['index'].cat.set_categories(list_custom, inplace=True)
        # inplace = True，使 df生效
        salary_edu.sort_values('index', inplace=True)

        low_salary = salary_edu.low_salary.tolist()
        high_salary = salary_edu.high_salary.tolist()
        edu = salary_edu.index.tolist()
        return edu, low_salary, high_salary

    def get_exp_salary(self):
        salary_exp = self.datas[['exp', 'low_salary', 'high_salary']].groupby(
            by='exp').mean()  # 平均值
        salary_exp = salary_exp.sort_values(by='low_salary')
        print(salary_exp)
        low_salary = salary_exp.low_salary.tolist()
        high_salary = salary_exp.high_salary.tolist()
        exp = salary_exp.index.tolist()
        return exp, low_salary, high_salary

    def word(self):
        r = r"任职要求|任职资格|岗位要求|任职条件|任职职格|职位需求|职位要求|工作经验及所需技能"
        # 提取岗位职责
        responbility = self.datas['info'].apply(lambda x: re.split(
            r, x)[0] if re.search(r, x) else x)
        # 提取岗位要求
        requirement = self.datas['info'].apply(lambda x: re.split(
            r, x)[1] if re.search(r, x) else "")

        # 把所有字符串连接成一个长文本
        responbility = ''.join(i for i in responbility)
        requirement = ''.join(i for i in requirement)
        # 去掉逗号等符号
        responsibility = re.sub(re.compile('，|；|\.|、|。'), '', responbility)
        requirement = re.sub(re.compile('，|；|\.|、|。'), '', requirement)
        # 分析岗位职责
        wordlist1 = " ".join(jieba.cut(responsibility, cut_all=True))
        stopwords1 = list(STOPWORDS) + ['岗位', '职责', '数据', '分析', '负责',
                                        '相关', '公司', '进行', '工作']  # 分析岗位职责
        wc1 = WordCloud(font_path=r'C:\Users\润敏\PycharmProjects\analysis_show\static\fonts\FZY3JW.TTF',
                        background_color="white",  # 背景颜色
                        max_words=2000,  # 词云显示的最大词数
                        stopwords=stopwords1,  # 设置停用词
                        max_font_size=100,  # 字体最大值
                        random_state=42,  # 设置有多少种随机生成状态，即有多少种配色
                        width=1000, height=860, margin=2,  # 设置图片默认的大小,margin为词语边缘距离
                        ).generate(wordlist1)
        wc1.to_file("responsibility.png")
        # 分析岗位要求
        wordlist2 = " ".join(jieba.cut(requirement, cut_all=False))
        stopwords2 = list(
            STOPWORDS) + ['岗位', '职责', '相关专业', '以上学历', '优先', '计算', '经验', '学历', '上学', '熟练', '使用', '以上']  # 分析岗位要求
        wc2 = WordCloud(font_path=r'C:\Users\润敏\PycharmProjects\analysis_show\static\fonts\FZY3JW.TTF',
                        background_color="white",  # 背景颜色
                        max_words=2000,  # 词云显示的最大词数
                        stopwords=stopwords2,  # 设置停用词
                        max_font_size=100,  # 字体最大值
                        random_state=42,  # 设置有多少种随机生成状态，即有多少种配色
                        width=1000, height=860, margin=2,  # 设置图片默认的大小,margin为词语边缘距离
                        ).generate(wordlist2)
        wc2.to_file("requirement.png")
        return wc1, wc2

if __name__ == '__main__':
    data_clean = data_clean()
    data_clean.word()