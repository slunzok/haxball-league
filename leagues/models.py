from django.db import models
from django_countries import CountryField

ROUNDS_TYPE = (
    (1, 'Round Robin'),
    (2, 'Double Round Robin'),
)

class Description(models.Model):
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    teams = models.IntegerField()
    rounds = models.IntegerField(default=2, choices=ROUNDS_TYPE)
    country = CountryField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return u'%s' % self.name
    
class Contestants(models.Model):
    league = models.ForeignKey(Description)
    name = models.CharField(max_length=20)
    match = models.IntegerField(default=0)
    win = models.IntegerField(default=0)
    draw = models.IntegerField(default=0)
    loss = models.IntegerField(default=0)
    goal_for = models.IntegerField(default=0)
    goal_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'%s' % self.name
    
class Results(models.Model):
    league = models.ForeignKey(Description)
    contestant1 = models.ForeignKey(Contestants, related_name="contestant1")
    contestant2 = models.ForeignKey(Contestants, related_name="contestant2")
    result1 = models.IntegerField(default=-1)
    result2 = models.IntegerField(default=-1)
    replay = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.contestant1, self.contestant2)
    
