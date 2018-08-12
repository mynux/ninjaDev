#!/bin/python
# -*- coding: utf-8 -*-
#
# This script is retrieve qq zone moments(说说) full content json formated data:
# from https://qzone.qq.com via selenium simulation session login. And then translate
# them into markdown formated Jekyll website.
# 
# TAG: Migration-Tool; QQZone-Moments; Markdown
# 

import requests
import re
import datetime
from selenium import webdriver
from time import sleep
from PIL import Image

def QR_login(): 
    def getGTK(cookie):
        hashes = 5381
        for letter in cookie['p_skey']:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff
    browser=webdriver.PhantomJS(executable_path="/Users/weheng/life/qqzone/phantomjs")
    url="https://qzone.qq.com/"
    browser.get(url)
    browser.maximize_window()
    sleep(3)
    browser.get_screenshot_as_file('QR.png')
    im = Image.open('QR.png')
    im.show()
    sleep(20)
    print(browser.title)
    cookie = {}
    for elem in browser.get_cookies():
        cookie[elem['name']] = elem['value']
    print('Get the cookie of QQlogin successfully!(total %d keyvalue pair)' % (len(cookie)))
    html = browser.page_source
    g_qzonetoken=re.search(r'window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',html)
    gtk=getGTK(cookie)
    browser.quit()
    return (cookie,gtk,g_qzonetoken.group(1))
 
# Entrance point.

headers={
    'Host': 'h5.qzone.qq.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': '*/*',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://user.qzone.qq.com/790178228?_t_=0.22746974226377736',
    'Connection':'keep-alive'
}
 
cookie,gtk,qzonetoken=QR_login() 

s=requests.session()

qq="807704416"

total_shuoshuo = 271
page_size = 20
divisor = total_shuoshuo / page_size
remain = total_shuoshuo - page_size * divisor
total_pages = divisor + remain % 1
print("total shuoshuo: %d, page_size: %d, total_pages: %d" % (total_shuoshuo, page_size, total_pages))

for p in range(0,total_pages):
    pos=p*20
    params={
        'uin':qq,
        'ftype':'0',
        'sort':'0',
        'pos':pos,
        'num':'20',
        'replynum':'100',
        'g_tk':gtk,
        'callback':'_preloadCallback',
        'code_version':'1',
        'format':'jsonp',
        'need_private_comment':'1',
        'qzonetoken':qzonetoken
    }
    
    response=s.request('GET','https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',params=params,headers=headers,cookies=cookie)
    print(response.status_code)
    text=response.text
    if not re.search('lbs', text):
        print('%sdownload completed with success'% qq)
        break
    
    # split msglist per cursor 
    newline_splited_content = re.sub('_preloadCallback', "\n_preloadCallback", text)
    pattern = r'_preloadCallback(.*)$'
    msglist_regex = re.compile(pattern)
    f = open("shuoshuo.txt", 'a')
    for line in newline_splited_content.splitlines():
        msglist_json = msglist_regex.match(line)
        if msglist_json:
            msgcontent = msglist_json.group()
            msg = re.sub(r'_preloadCallback\((.*)\);$', '\\1', msgcontent)
            f.write(msg.encode("utf-8") + "\n")
 
    f.close()
print('download completed with success!')
