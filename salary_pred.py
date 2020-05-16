from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder as LE
from sklearn.linear_model import LinearRegression as LR
from data_clean import *
import numpy as np


class salary_pred(object):

    def __init__(self, key):
        self.data_clean = data_clean(key)
        jobs = self.data_clean.get_all()
        # 数据处理
        jobs = jobs.drop(jobs.loc[jobs['exp'].isnull()].index)
        jobs = jobs.drop(jobs.loc[jobs['edu'].isnull()].index)
        jobs = jobs.drop(jobs.loc[jobs['place'].isnull()].index)
        jobs['exp'] = jobs['exp'].apply(self.get_exp)
        jobs['low_salary'] = jobs['low_salary'].round(0)
        jobs['avg_salary'] = jobs['avg_salary'].round(0)
        # 将各字符分类变量重编码为数值分类变量
        self.le = LE()
        citys_list = jobs['citys'].tolist()
        jobs['citys'] = self.le.fit_transform(jobs['citys'].astype(str))  # 城市重编码
        jobs['edu'] = jobs['edu'].replace('中专', 0)  # 学历重编码
        jobs['edu'] = jobs['edu'].replace('初中及以下', 0)
        jobs['edu'] = jobs['edu'].replace('中技', 0)
        jobs['edu'] = jobs['edu'].replace('高中', 1)
        jobs['edu'] = jobs['edu'].replace('大专', 2)
        jobs['edu'] = jobs['edu'].replace('本科', 3)
        jobs['edu'] = jobs['edu'].replace('硕士', 4)
        jobs['edu'] = jobs['edu'].replace('博士', 5)

        # 特征选择
        X = jobs[['citys', 'exp', 'edu']]
        # 结果集
        y_low = jobs['low_salary']
        y_avg = jobs['avg_salary']
        # 模型训练
        self.model_low, self.info_low = self.fit(X, y_low)
        self.model_avg, self.info_avg = self.fit(X, y_avg)

    # 薪资处理
    def get_exp(self, exp):
        ## 1年经验，2年经验，3-9年经验，无工作经验
        if '-' in exp:
            exp = exp.split('-')
            return int(exp[0])
        elif exp == '无工作经验' or '在校生/应届生':
            return 0
        else:
            return int(exp[0])

    def fit(self, X, y):
        # 30%的测试数据
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        print('X_train:', X_train.shape)
        print('X_test:', X_test.shape)
        print('y_train:', y_train.shape)
        print('y_test:', y_test.shape)
        ## 模型学习
        model = LR()
        model.fit(X_train, y_train)

        # 预测薪资
        y_pred = model.predict(X_test)

        # 打印模型信息
        print('系数:', model.coef_)
        print('截距:', model.intercept_)
        print(
            '模型: Salary = {} + {} * 城市 + {} * 经验+ {} * 学历'.format(model.intercept_, model.coef_[0], model.coef_[1],
                                                                     model.coef_[2]))
        print('均方根误差: {}'.format(np.sqrt(mean_squared_error(y_test, y_pred))))
        info = {'模型': 'Salary = {} + {} * 城市 + {} * 经验+ {} * 学历'.format(
            model.intercept_, model.coef_[0], model.coef_[1], model.coef_[2]), '均方根误差': np.sqrt(
            mean_squared_error(y_test, y_pred))}
        return model, info

    def get_info_low(self):
        return self.info_low['模型'], self.info_low['均方根误差']

    def get_info_avg(self):
        return self.info_avg['模型'], self.info_avg['均方根误差']

    # 预测
    def pred(self, area, exp, xueli):
        area_index = list(self.le.classes_).index(area)
        xueli_index = list(('中专/中技', '高中', '大专', '本科', '硕士', '博士')).index(xueli)
        exp = int(exp)
        pred_low = self.model_low.predict([[area_index, exp, xueli_index]])
        print("测试2")
        pred_avg = self.model_avg.predict([[area_index, exp, xueli_index]])
        print("测试3")
        print(area + "区域、工作经验为", exp, "、学历为" + xueli)
        print("预测低薪资为：" + '%.2f' % pred_low)
        print("预测平均薪资为：" + '%.2f' % pred_avg)
        return pred_low, pred_avg


# 测试代码
# if __name__ == '__main__':
#     salary_pred = salary_pred()
#     salary_pred.pred('深圳', 0, '本科')
