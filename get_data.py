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

key = 'java'  # 全局变量key
edu = ['博士', '硕士', '本科', '大专', '中专', '高中', '']
client = MongodbClient()  # 初始化数据库类
client.change_table(key)
client.clear()


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
        response = requests.get(url)
    response.encoding = 'utf-8'
    while response.status_code != requests.codes.ok:
        print(response.status_code)
        time.sleep(random.randrange(1, 3))
        get_html(url)
        continue
    else:
        return response.text


fp = open('51job.csv', 'wt', newline='', encoding='GBK', errors='ignore')
writer = csv.writer(fp)
'''title, time, place, salary, num, exp, edu, company, companyinfo, companyplace, info'''
writer.writerow(('职位', '时间', '地区', '薪资', '人数', '工作经验', '学历', '公司',
                 '公司信息', '公司地址', '岗位信息'))


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
                'string(//*[@id="pageContent"]/div[3]/div[2]/article)')
            data['info'] = str(info).strip()

            if (str(data['edu']) not in edu):
                print("edu有错", jobInfo_url)
                print(data['edu'])
            if (data['title'] != ''):
                # 添加到数据库中
                client.put(data)
                # 写入文件
                writer.writerow((data['title'], data['time'], data['place'], data['salary'],
                                 data['num'], data['exp'], data['edu'], data['company'],
                                 data['companyinfo'], data['companyplace'], data['info']))


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
    pages = get_webpages(key)
    print(pages, "页")
    # for page in range(1,pages+1):
    #     job_spider(page)
    # 利用进程池
    pool = Pool(processes=1)
    pages = ([p + 1 for p in range(pages)])
    # 往进程池添加任务
    pool.map(job_spider, pages)
    pool.close()
    pool.join()

    print(time.time() - start)
