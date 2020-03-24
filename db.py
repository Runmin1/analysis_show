from config import TABLE, HOST, PORT
from pymongo import MongoClient, ASCENDING

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

    def set_num(self):
        """给每条数据设置唯一自增num"""
        nums = []
        datas = self.get_all()
        if datas:
            for data in datas:
                nums.append(data['num'])
            return max(nums)
        return 0

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
            # 先排序
            self.sort()
            datas = [i for i in self.db[self.table].find()]
            return datas
        return None

    def put(self, data):
        """添加数据"""
        # num = self.set_num() + 1
        # 判断是否重复
        if self.db[self.table].find_one(data):
            # 重复则删除，重新插入
            self.delete(data)
            print("重复删除")
            # data['num'] = num
            self.db[self.table].insert_one(data)
        else:
            # data['num'] = num
            print("无重复")
            self.db[self.table].insert_one(data)

    def delete(self, data):
        """删除数据"""
        self.db[self.table].remove(data)

    def clear(self):
        """清空表"""
        self.client.drop_database(self.table)

    def sort(self):
        """按num键排序"""
        self.db[self.table].find().sort('num', ASCENDING)

    def get_page(self, page, count):
        """
        分页数据
        :param page: 页数
        :param count: 每页条数
        :return: 每页数据
        """
        # 判断是否有数据
        if self.get_nums != 0:
            # 排序
            self.sort()
            # 如果整除count为0，就直接返回为第一页
            pages = self.get_nums // count + 1 if self.get_nums >= 10 else 1

            paginate = []
            for p in range(1, pages+1):
                if p > 1:
                    datas = [i for i in self.db[self.table].find().limit(
                        count).skip((p-1)*count)]
                else:
                    datas = [i for i in self.db[self.table].find().limit(count)]
                paginate.append({'page': p, 'data': datas})
            return [j['data'] for j in paginate if j['page'] == page]
        return None
