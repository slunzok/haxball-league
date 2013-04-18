from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^leagues/', include('leagues.urls', namespace='leagues')),
    url(r'^captcha/', include('captcha.urls')),
)
