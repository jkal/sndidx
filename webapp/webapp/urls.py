from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from webapp.views import *

urlpatterns = patterns('',
    url(r'^browserid/', include('django_browserid.urls')),

    url(r'^$', 'webapp.views.home', name='home'),
    url(r'^signin/$', 'webapp.views.signin', name='signin'),
    url(r'^upload/$', 'webapp.views.upload', name='upload'),
    url(r'^search/$', 'webapp.views.search', name='search'),
    url(r'^results/(\w+)/$', 'webapp.views.results', name='results'),
    url(r'^graph/(\w+)/$', 'webapp.views.graph', name='graph'),
)

urlpatterns += staticfiles_urlpatterns()
