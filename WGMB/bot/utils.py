import urllib3
from bs4 import BeautifulSoup
import re

from datetime import date, timedelta

from .models import User, History


def parse_solved_problems(url):
    """
        Parse solved problems from the target URL

        Args:
            url: target URL, str

        Return:
            solved problems, str
    """
    urllib3.disable_warnings()
    response = urllib3.PoolManager().request(method='GET', url=url)
    if response.status == 200:
        soup = BeautifulSoup(response.data, "lxml")
        solved = soup.find_all(class_='badge progress-bar-success')[-5]
        return re.compile(r'\d+').findall(solved.string)[0]


def get_last_history(username):
    """
        Get the last history in the database

        Args:
            username: the target user, str

        Return:
            the last history, History
    """
    users = User.objects.filter(username=username)
    if users:
        return users[0].history_set.last()


def update_history(username):
    """
        Update the history database if necessary. Please carefully read the following docs.

        If the database have today's history, then the database only will be updated
    when new problems solved, and difference between the today's history and at least one day 
    before history will be returned, which means comparison will also process when yesterday's
    history don't exists and the comparision will process between today and the day before 
    yesterday or other day, when the history is available.
        
        If the database don't have today's history, then new history of today will be inserted
    into the database, and difference between the today's history and at least one day before
    history will be returned.

        If the username don't exists in the database, return -1.

        If the user just registered today, return -2;

        Args:
            username, the target user, str

        Return:
            difference explained as above, int
    """
    diff = -1
    users = User.objects.filter(username=username)
    if users:
        user = users[0]
        history_set = user.history_set
        # get the last history
        last_history = history_set.last()
        # update if solved new problems, otherwise no operation
        if last_history.date == date.today():
            if history_set.count() != 1:
                pre_history = history_set.exclude(date=date.today()).last()
                solved_problems = int(parse_solved_problems(user.url))
                diff = solved_problems - pre_history.solved_problems
                if solved_problems != last_history.solved_problems:
                    History.objects.filter(id=last_history.id).update(solved_problems=solved_problems)
            else:
                solved_problems = int(parse_solved_problems(user.url))
                diff = -2
                if solved_problems != last_history.solved_problems:
                    History.objects.filter(id=last_history.id).update(solved_problems=solved_problems)
        # insert new history
        else:
            new_history = History()
            new_history.solved_problems = parse_solved_problems(user.url)
            new_history.date = date.today()
            new_history.user = user
            new_history.save()
            diff = new_history.solved_problems - last_history.solved_problems
    return diff
