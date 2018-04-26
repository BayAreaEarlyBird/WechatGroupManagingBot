from django.db import models


class User(models.Model):

    username = models.CharField(max_length=200, unique=True)
    url = models.CharField(max_length=200)

    def __str__(self):
        return self.username + ' ' + self.url


class History(models.Model):

    solved_problems = models.IntegerField()
    date = models.DateField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username) + ' ' + str(self.solved_problems) + ' ' + str(self.date.year) + ' ' + str(self.date.month) + ' ' + str(self.date.day)
