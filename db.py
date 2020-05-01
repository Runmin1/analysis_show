from config import TABLE, HOST, PORT
from pymongo import MongoClient, ASCENDING
import datetime

# 我们把配置文件放入 config.py 文件内
class MongodbClient(object):

    def __init__(self, table=TABLE, host=HOST, port=PORT):
        self.table = table
        self.client = MongoClient(host, port)
        self.db = self.client.Job

    @property
    def get_counts(self):
        """获取表里的数据总数"""
        return self.db[self.table].count()

    def change_table(self, table):
        """切换数据库表"""
        self.table = table

    def get_new(self):
        """获取最新一条数据"""
        data = self.get_all()[-1] if self.get_all() else None
        return data

    def get_data(self, num):
        """获取指定num的数据"""
        datas = self.get_all()
        if datas:
            data = [i for i in datas if i['num'] == num][0]
            return data
        return None

    def get_all(self):
        """获取全部数据"""
        # 判断表里是否有数据
        if self.get_counts != 0:
            datas = [i for i in self.db[self.table].find()]
            return datas
        return None

    def put(self, data):
        slice_job = {k: data[k] for k in list(data.keys())[1:]}
        data_if_exist = dict(slice_job)
        data_time = data_if_exist.pop('time')
        data_if_exist.pop('num')
        """添加数据"""
        # 判断是否重复
        if self.db[self.table].find_one("link", data['link']):
            # 重复则不添加
            print("链接重复,不添加")
        elif self.db[self.table].find_one(data_if_exist):
            # 数据重复，保留最新发布的一条招聘信息
            db_time = self.db[self.table].find_one(data_if_exist)['time']
            # 将日期字符串转为时间再比较
            datetime.datetime.strptime(db_time, "%Y-%m-%d")
            datetime.datetime.strptime(data_time, "%Y-%m-%d")
            if db_time < data_time:
                self.delete(data_if_exist)
                self.db[self.table].insert_one(data)
                print("已替换为新的招聘信息")
            print("数据重复,保留最新发布的一条招聘信息")
        else:
            self.db[self.table].insert_one(data)

    def delete(self, data):
        """删除数据"""
        self.db[self.table].remove(data)

    def col_exist(self, key):
        result = key in self.db.collection_names()
        return result

    def clear(self):
        """清空表"""
        self.db[self.table].remove({})
