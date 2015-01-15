from django.conf.urls import patterns, include, url
#from django.contrib import admin
#admin.autodiscover()

from django.views.generic import TemplateView

urlpatterns = patterns('PageLoadStatsPy.pageloadstats.views',
    #url(r'^/directory', TemplateView.as_view(template_name="directory.html")),
    url(r'^$', 'daily_avgs'),                              # default view url
    url(r'^targets/$', 'target_list'),                      # a list of targets in the db
    url(r'^dailyavgs/$', 'daily_avgs'),              # show the current daily overall performance stats
    url(r'^dailyavgs/(?P<tags>[\w,]+)/(?P<days>[0-9]+)/$', 'daily_avgs'),              # show the current daily overall performance stats
    url(r'^httperrors/$', 'http_errors'), # show stats of tests that did not return http 200
    url(r'^httperrorchart/$', 'http_errorchart'), # get a chart of  http errors

    url(r'^chart/$', 'flot'),
    url(r'^api/chartline/$', 'flot_line'),

    url(r'^manage/targets/$', 'manage_targets'),
    url(r'^target/edit/(?P<target_id>\d+)/$', 'edit_target'),
    url(r'^target/add/$', 'add_target'),

    url(r'^manage/alerts/$', 'manage_alerts'),
    url(r'^alert/edit/(?P<alert_id>\d+)/$','edit_alert'),
    url(r'^alert/add/$', 'add_alert'),

    url(r'^manage/recipients/$', 'manage_recipients'),
    url(r'^recipient/edit/(?P<recipient_id>\d+)/$','edit_recipient'),
    url(r'^recipient/add/$', 'add_recipient'),

    url(r'^api/tags/$', 'get_tags'), # API get a list of tags in use
    url(r'^api/targets/all/(?P<return_type>)\w+/$', 'get_targets_all'), # API get a lis of all active targets
    url(r'^api/targets/(?P<tag>\w+)/(?P<return_type>)\w+/$', 'get_targets_by_tag'), # API get a list of targets for the given tag


    url(r"^api/target/update/(?P<target_id>\d+)/$", "target_update"), # save changes to a target record
    url(r"^api/target/delete/(?P<target_id>\d+)/$", "target_delete"), # delete a target ACTUAL DELETION, you probably want to deactivate, not delete
    url(r"^api/target/create/", "target_create"), # add a new target
    url(r"^api/alert/update/(?P<alert_id>\d+)/$", "alert_update"), # save changes to a target record
    url(r"^api/alert/delete/(?P<alert_id>\d+)/$", "alert_delete"), # delete a target ACTUAL DELETION, you probably want to deactivate, not delete
    url(r"^api/alert/create/", "alert_create"), # add a new target
    url(r"^api/recipient/update/(?P<recipient_id>\d+)/$", "recipient_update"), # save changes to a target record
    url(r"^api/recipient/delete/(?P<recipient_id>\d+)/$", "recipient_delete"), # delete a target ACTUAL DELETION, you probably want to deactivate, not delete
    url(r"^api/recipient/create/", "recipient_create"), # add a new target


    url(r'^api/dailyavg/(?P<target_id>\d+)/(?P<days_ago>\d+)/$', 'get_daily_avg_by_id'),
    url(r'^api/dailyavg/(?P<tag>[\w,]+)/(?P<days_ago>\d+)/$', 'get_daily_avg_by_tag'),              # show the current daily overall performance stats

    url(r'^api/httperrors/$', 'get_http_errors'), # get a page of  http errors

    # request app to run checks against targets
    url(r'^check/(?P<target_id>\d+)/$', 'check'),           # run a target stat check on tartet # <target_id>
    url(r'^check/(?P<target_id>all)/$', 'check'),           # run a target stat check on everything in the DB

    url(r'^user_logout/$', 'user_logout'),           # log a user out



    #url(r'^pls/', include('PageLoadStatsPy.pageloadstats.urls')),
    #url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
)
