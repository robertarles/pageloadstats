from PageLoadStatsPy.pageloadstats.models import Alert, Target, Stat
from django.contrib import admin

admin.site.register(Target)
admin.site.register(Stat)
admin.site.register(Alert)