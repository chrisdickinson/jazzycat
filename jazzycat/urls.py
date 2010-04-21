from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    'jazzycat.views',
    url(r'^register/$', 'register'),
)
