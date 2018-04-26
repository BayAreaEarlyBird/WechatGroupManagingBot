#!/usr/bin/env python3

import itchat
import re
import urllib3

basic_url = '127.0.0.1:8000/bot/'


def parse_url(text):
    """
        Parse URL from message using BeautifulSoup 4.

        Args:
            text: message, str

        Return:
            parsed URL, str
    """
    url = re.compile(r'https://leetcode\.com/\w+').findall(text)
    if url:
        return url[0]


def get_nickname(username):
    """
        Get nickname for corresponding username

        Args:
            username: username in message, str
        Return:
            nickname, str
    """
    return itchat.search_friends(userName=username)['NickName']


def is_register(text):
    """
        Whether the command is registering command.

        Args:
            text: message text received, str
        
        Return:
            the command is registering command or not, bool
    """
    return len(re.compile(r'register').findall(text)) > 0


def is_update_url(text):
    """
        Whether the command is updating url command.

        Args:
            text: message text received, str
        
        Return:
            the command is updating command or not, bool
    """

    return len(re.compile(r'update url').findall(text)) > 0


def is_day_report(text):
    """
        Whether the command is daliy report command.

        Args:
            text: message text received, str
        
        Return:
            the command is daliy report command or not, bool
    """
    
    return len(re.compile(r'day').findall(text)) > 0


@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def reply(message):
    """
        Command parser as a proxy server and replying.

        Now support:
            register      : @xxxxx register https://leetcode.com/xxxxxx
            update url    : @xxxxx update url https://leetcode.com/xxxxxx
            daliy report  : @xxxxx day
        
        TODO:
            weekly report : @xxxxx week (this may be manually done)
    """
    if message.isAt:
        # get nickname
        nickname = get_nickname(message['FromUserName'])
        # register
        if is_register(message.text):
            # parse URL from message
            url = parse_url(message.text)
            if url:
                # request registering to server
                # server run on the same computer in default 
                response = urllib3.PoolManager().request(
                    method='POST', url=basic_url + 'register', fields={'username': nickname, 'url': url})
                # register success
                if response.status == 200:
                    message.user.send(nickname + ', you totally solved ' + response.data.decode() + ' problems')
                # url error
                elif response.status == 404:
                    message.user.send(nickname + ', please check the url')
                # registerd already
                else:
                    message.user.send(nickname + ', you have registered already, if need, please update your url with the update command')
            # url error
            else:
                message.user.send(nickname + ', please check the url')
        # update url
        elif is_update_url(message.text):
            # parse URL from message
            url = parse_url(message.text)
            if url:
                # request updating user to server
                # server run on the same computer in default 
                response = urllib3.PoolManager().request(
                    method='POST', url=basic_url + 'user', fields={'username': nickname, 'url': url})
                # update success
                if response.status == 200:
                    message.user.send(nickname + ', update done')
                # url error
                elif response.status == 404:
                    message.user.send(nickname + ', please check the url')
            # url error
            else:
                message.user.send(nickname + ', please check the url')
        # daliy report
        elif is_day_report(message.txt):
            # request daliy report to server
            # server run on the same computer in default 
            response = urllib3.PoolManager().request(
                    method='GET', url=basic_url + 'day', fields={'username': nickname})
            # request success
            if response.status == 200:
                diff = int(response.data.decode())
                # only one history, no comparision
                if diff < 0:
                    message.user.send(nickname + ', you totally solved ' + -diff + ' problems')
                # comparision
                else:
                    message.user.send(nickname + ', you solved ' + diff + ' problems today')
        # else:
            # message.user.send(nickname + ', ')


def send_one_group(message, group_name):
    """
        Send message to one group. (for future consideration)

        Args:
            message:    message text to send, str
            group_name: the name of the group to be sent, str
    """
    # search the room with the specified group name
    rooms = itchat.search_chatrooms(group_name)
    if rooms is None:
        print('no such group:', group_name)
    else:
        username = rooms[0]['UserName']
        itchat.send(msg=message, toUserName=username)


def test():
    """
        Just for tesing
    """
    response = urllib3.PoolManager().request(
                    method='GET', url=basic_url + 'day', fields={'username': 'neilfvhv'})
    print(response.data)


if __name__ == '__main__':
    # disable warnings for SSH
    urllib3.disable_warnings()
    # login
    itchat.auto_login(hotReload=True)
    # block main thread
    itchat.run()
