from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'leagues.views.index', name='index'),
    url(r'^(?P<league_id>\d+)/$', 'leagues.views.detail', name='detail'),
    url(r'^(?P<league_id>\d+)/pass/$', 'leagues.views.admin_pass', name='pass'),
    url(r'^(?P<result_id>\d+)/set_score/$', 'leagues.views.set_score', name='set_score'),
    url(r'^(?P<result_id>\d+)/clear_score/$', 'leagues.views.clear_score', name='clear_score'),
    url(r'^(?P<result_id>\d+)/set_replay/$', 'leagues.views.set_replay', name='set_replay'),
    url(r'^(?P<league_id>\d+)/edit_names/$', 'leagues.views.edit_names', name='edit_names'),
    url(r'^(?P<league_id>\d+)/delete/$', 'leagues.views.delete', name='delete'),
    url(r'^latest/$', 'leagues.views.latest', name='latest'),
)
