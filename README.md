# HaxBall League v0.1

**Description**

* HaxBall League is a community website, where you can create and manage your own league (add/edit teams, edit/set scores and replays, automatic generate the ranking table). 

**Screenshots**

<img src='https://raw.github.com/slunzok/haxball-league/master/screenshots/001_002.png'/>
<img src='https://raw.github.com/slunzok/haxball-league/master/screenshots/003_004.png'/>

* [HaxBall League - more screenshots](https://github.com/slunzok/haxball-league/tree/master/screenshots)

**Requirements**

* django 1.5.1 (python web framework)
* django-simple-captcha 0.3.6
* django-countries 1.5

**Example installation (on uberspace.de):**

    # install Django, see http://uberspace.de/dokuwiki/cool:django
    $ pip-2.7 install django-simple-captcha
    $ pip-2.7 install django-countries

    $ git clone git@github.com:slunzok/haxball-league.git
    $ cd haxball-league
    $ vim haxball/settings.py (#set correctly: GEOIP_PATH, DATABASES, TIME_ZONE, MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL, TEMPLATE_DIRS)
    
    $ mkdir /home/your_username/html/media
    $ mkdir /home/your_username/html/media/replays
    $ mkdir /home/your_username/html/static
    $ cp -a static/. /home/your_username/html/static/
    
    $ python2.7 manage.py syncdb
    
**License**

* HaxBall League is available under the BSD license
