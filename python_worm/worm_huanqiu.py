import re
import json
import random
import re
import os
import socket
import string
import threading
import time
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import redis
from past.builtins import apply

DATA_DIR=os.path.pardir+os.sep+'Data'+os.sep
re_chinese_words = re.compile(u"[\u4e00-\u9fa5]+")
BASE_URL = 'http://weapon.huanqiu.com'
WEAPON_URL = BASE_URL + '/weaponmaps'
TIME_SLEEP = 5
M_Headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    , 'Referer': 'http://music.163.com/user/fans?id=97526496'

}
socket.setdefaulttimeout(10)
DB = redis.Redis(host='47.94.251.202', port=6379, db=8, password='wscjxky', decode_responses=True)

keys = DB.keys('huanqiu:sec_sort*')
print(keys)

def get_index_sort(data):
    soup = BeautifulSoup(data, 'html.parser')
    tags_div = soup.find('div', class_="listCon")
    tags_ul = tags_div.find_all('ul')

    for index_ul, tag_ul in enumerate(tags_ul):
        print(index_ul)
        first_sort = soup.find_all('h3')[index_ul + 1].text
        print(first_sort)
        tags_li = tag_ul.find_all('li')
        for tag_li in tags_li:
            tag_a = tag_li.find('a')
            link = tag_a.get('href')
            name = re.search(re_chinese_words, tag_a.text).group(0)
            DB.hset(first_sort, name, BASE_URL + link)
            print(link, name)


def get_sort_info(data):
    soup = BeautifulSoup(data, 'html.parser')
    second_sort = soup.find('span', class_="list").find('b').text
    print(second_sort)
    tags_div = soup.find('div', class_="picList")
    tags_li = tags_div.find_all('li')
    for index_ul, tag_li in enumerate(tags_li):
        tag_a = tag_li.find('span', class_='name').find('a')
        name = tag_a.text
        name = name.replace('”', '')
        name = name.strip()
        link = tag_a.get('href')
        DB.hset('huanqiu:sec_sort:'+second_sort, name, BASE_URL + link)
        print(link, name)
def get_sort_img(data):
    soup = BeautifulSoup(data, 'html.parser')
    img = soup.find('div', class_="maxPic").find('img').get('src')
    response = urllib.request.urlopen(img)
    data = response.read()
    try:
        os.mkdir(DATA_DIR+os.sep+'huanqiu')
    except :
        print('dir is already made')
    with open(DATA_DIR+"/1/1.%s" % (img[-3:]),"wb") as f:
        f.write(data)

def request_url(url, ):
    sort = url[-10:]
    key_cache = 'index'
    restart = True
    # proxy={'http': 'http://39.134.93.13:80'}
    # proxy_support = urllib2.ProxyHandler(proxy)
    # opener = urllib2.build_opener(proxy_support)
    # urllib2.install_opener(opener)
    filename = key_cache + ':' + sort
    try:
        if restart:
            if DB.get(filename):
                return DB.get(filename)
            else:
                print(url)
                time.sleep(TIME_SLEEP)
                req = urllib.request.Request(url, headers=M_Headers)
                data = urllib.request.urlopen(req).read()
                DB.set(filename, data)
                return data

    except urllib.error.URLError as e:
        print(e)
        print(e.reason)
        print(e.args)
        if (e.reason == 503):
            STOP_FLAG = True
class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.args = args
        self.func = func
    def run(self):
        apply(self.func, self.args)

if __name__ == '__main__':
    # base_url='https://www.researchgate.net/'
    # url_1=base_url+'publication/258821296_An_Iterative_Pilot-Data_Aided_Estimator_for_OFDM-Based_Relay-Assisted_Systems'
    # data = request_url(WEAPON_URL, BASE_URL[-10:], key_cache='index')
    # get_index_sort(data)
    Threadlist = []
    keys=DB.keys('huanqiu:sec_sort*')
    for first_sort in keys:
        dic=DB.hgetall(first_sort)
        for scond_sort, link in dic.items():
            # Threadlist.append(MyThread(request_url,link))
            data=request_url(link)
            get_sort_img(data)


    for t in Threadlist:
        t.setDaemon(True)  # 如果你在for循环里用，不行， 因为上一个多线程还没结束又开始下一个
        t.start()
    for j in Threadlist:
        j.join()
    # get_sort_info(data)
    # get_sort_img(data)
    # with open('detail','wb') as f:
    #     f.write(data)
    # with open('detail','rb') as f:
    #     data=f.read()
    # getPaperLinkdata(data)
    # getPaperAuthor(data)
