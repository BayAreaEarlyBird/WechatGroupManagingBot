#!/usr/bin/python
#-*- coding:cp936 -*-

import itchat, time
from itchat.content import *
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import urllib2
import re
import datetime
import os.path

def get_url_content(url):
    i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5",\
                 "Referer": 'http://www.baidu.com'}
    req = urllib2.Request(url, headers=i_headers)
    return urllib2.urlopen(req).read()

def get_submission(url):
    html_text = get_url_content(url)
    submission = re.findall(r'\d+ \/ \d+',html_text)
    return re.findall(r'\d+', submission[-1])[0]

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    msg.user.send('%s: %s' % (msg.type, msg.text))

@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    url = None
    submission = None
    last_submission = None
    if msg.isAt:
        fileName = msg.actualNickName.encode("utf-8")
        if os.path.isfile(fileName) :
            fin=open(fileName,'r')
            submission_list = fin.readlines()
            fin.close()
            if len(submission_list) > 0:
                last_submission = re.findall(r'\d*', submission_list[-1])[0]
                url = re.findall(r'https:\/\/leetcode.com\/.+\/', submission_list[-1])[0]
        if not url:
            url_list = re.findall(r'https:\/\/leetcode.com\/.+\/', msg.text)
            if len(url_list) == 0:
                msg.user.send("Can't fetch submission, please check url")
            url = url_list[0]
        submission = get_submission(url)
        if submission:
            fout=open(fileName,'a')
            now = datetime.datetime.now()
            fout.write(submission + ' ' + now.strftime("%Y-%m-%d %H:%M") + ' ' + url + '\n')
            fout.close()
            if last_submission:
                msg.user.send(msg.actualNickName + ', your today\'s Accepted Submission is:' + str(int(submission) - int(last_submission)))
            else:
                msg.user.send(msg.actualNickName + ', your total Accepted Submission is:' + submission)
        else:
            msg.user.send("Can't fetch submission, please check url")

itchat.auto_login(enableCmdQR=1, hotReload=True)

itchat.run(True)

