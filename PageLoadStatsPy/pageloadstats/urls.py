from django.conf.urls.defaults import patterns, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('PageLoadStatsPy.pageloadstats.views',
    url(r'^$', 'target_list'),                              # default view url
    url(r'^targets/$', 'target_list'),                      # a list of targets in the db
    
    url(r'^chart/(?P<target_id>\d+)/$', 'chart'),           # the chart for target # <target_id>
    url(r'^chart/(?P<tag>\w+)/$', 'chart_multi_by_tag'),      # the chart for multiple targets
    url(r'^chart/(?P<target_id_list>[0-9]+,[0-9,]+)/$', 'chart_multi_by_id'),      # the chart for multiple targets by id
    
    # TODO: change the chart.html calls to use the new api/ofc2chart/ urls (dep=views must pass the new data urls, too)
    #url(r'^chart_data/(?P<target_id>\d+)/$', 'chart_data'), # API this one returns the data for the chart view
    #url(r'^chart_multi_data/(?P<target_id_list>[0-9,]+)/$', 'chart_multi_data_by_ids'),        # API this one returns the data for the chart_multi view
    #url(r'^chart_multi_data/(?P<tag>\w+)/$', 'chart_multi_data_by_tag'),        # API this one returns the data for the chart_multi view
    
    # API for OFC2 charting
    url(r'^api/ofc2chart/(?P<target_id>\d+)/$', 'chart_data'), # API this one returns the data for the chart view
    url(r'^api/ofc2chart/(?P<target_id_list>[0-9,]+)/$', 'chart_multi_data_by_ids'),        # API this one returns the data for the chart_multi view
    url(r'^api/ofc2chart/(?P<tag>\w+)/$', 'chart_multi_data_by_tag'),        # API this one returns the data for the chart_multi view
    
    # API 
    url(r'^api/tags/$', 'get_tags'), # API get a list of tags in use
    
    url(r'^check/(?P<target_id>\d+)/$', 'check'),           # run a target stat check on tartet # <target_id>
    url(r'^check/(?P<target_id>all)/$', 'check'),           # run a target stat check on everything in the DB
    
    url(r'^dailyavgs/$', 'daily_avgs'),              # show the current daily overall performance stats
    url(r'^dailyavg/(?P<tag>.+)/(?P<days_ago>\d+)/$', 'get_daily_avg'),              # show the current daily overall performance stats
    
    url(r'^user_logout/$', 'user_logout'),           # log a user out
)
