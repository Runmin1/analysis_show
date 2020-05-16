import requests
import re
from urllib import parse
from lxml import etree
from config import *
import random
import csv
import time
from multiprocessing import Pool
from db import *

key = '软件测试'
client = MongodbClient(table=key)  # 初始化数据库类
client.change_table(key)
fp = open('51job.csv', 'wt', newline='', encoding='GBK', errors='ignore')
writer = csv.writer(fp)
'''link， title, time, place, salary, num, exp, edu, company, companyinfo, companyplace, info'''
writer.writerow(('链接', '职位', '时间', '地区', '薪资', '人数', '工作经验', '学历', '公司',
                 '公司信息', '公司地址', '岗位信息'))

# 获取页数
def get_webpages(key):
    url = get_url(key, 1)
    html = get_html(url, True)
    if html:
        selector = etree.HTML(html)
        items = selector.xpath(
            '//*[@id="pageContent"]/p[1]/span/text()')
        pages = int(items[0]) // 50 + 1
        return pages


# 获取关键字页面的url
def get_url(key, page):
    url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,' + \
          parse.quote(parse.quote(key)) + \
          ',2,{}.html'.format(page)
    return url


# 获取HTML
def get_html(url, need_header):
    # 下载页面
    if need_header:
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    while response.status_code != requests.codes.ok:
        print(response.status_code, ',', url)
        time.sleep(random.randrange(1, 3))
        get_html(url, False)
        continue
    else:
        return response.text

# 提取详情页的关键字段
def extract_detail_data(html):
    # 解析搜索页，获取职位链接
    selector = etree.HTML(html)
    jobInfo_urls = selector.xpath(
        '//*[@id = "resultList"]/div/p/span/a/@href')
    # 获取岗位信息
    for jobInfo_url in jobInfo_urls:
        jobInfo_html = get_html(jobInfo_url, True)
        # print(jobInfo_url)
        if jobInfo_html:
            selector = etree.HTML(jobInfo_html)
            data = {}  # 定义一个数据字典存储岗位信息
            data['link'] = jobInfo_url
            data['title'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[1]/p/text())')
            data['time'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[1]/span/text())')
            data['place'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[1]/em/text())')
            data['salary'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/p/text())')
            data['num'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[2]/span[1]/text())')
            data['exp'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[2]/span[@class="s_n"]/text())')
            data['edu'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[1]/div[2]/span[@class="s_x"]/text())')
            data['company'] = selector.xpath(
                'string(//*[@id = "pageContent"]/div[2]/a[1]/p/text())')
            data['companyinfo'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[2]/a[1]/div/text())')
            data['companyplace'] = selector.xpath(
                'string(//*[@id="pageContent"]/div[2]/a[2]/span/text())')
            info = selector.xpath(
                'string(//*[@id="pageContent"]/div[3]/div/article)')
            data['info'] = str(info).strip()

            # 空字符串用缺失值代替
            for key in data:
                if data[key] == '':
                    data[key] = None

            if data['title']:
                # 添加到数据库中
                client.put(data)
                # 写入文件
                writer.writerow((jobInfo_url, data['title'], data['time'], data['place'], data['salary'],
                                 data['num'], data['exp'], data['edu'], data['company'],
                                 data['companyinfo'], data['companyplace'], data['info']))
            else:
                print(data['title'], jobInfo_url)


# 数据爬取过程
def job_spider(page):
    url = get_url(key, page)
    print("url:", url)
    html = get_html(url, False)
    # time.sleep(random.randrange(1, 2))
    if html:
        extract_detail_data(html)
    else:
        print("html报错")


if __name__ == '__main__':
    start = time.time()
    # 判断关键字是否已存在数据表中
    if client.col_exist(key):
        print('该关键字已存在数据表')
        choose = input("是否继续爬虫（1：是，2：否）")
        if choose=="1":
            pages = get_webpages(key)
            print(pages, "页")
            # 利用进程池
            pool = Pool(processes=2)
            pages = ([p + 1 for p in range(pages)])
            # 往进程池添加任务
            pool.map(job_spider, pages)
            pool.close()
            pool.join()

            print(time.time() - start)
    else:
        pages = get_webpages(key)
        print(pages, "页")
        # 利用进程池
        pool = Pool(processes=2)
        pages = ([p + 1 for p in range(pages)])
        # 往进程池添加任务
        pool.map(job_spider, pages)
        pool.close()
        pool.join()

        print(time.time() - start)

