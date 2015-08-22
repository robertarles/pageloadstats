from PageLoadStatsPy.pageloadstats.models import Alert, Target, Stat, AlertAlertRecipients, AlertRecipients, TargetAlert
from django.contrib import admin

class TargetAlertInline(admin.StackedInline):
    model = TargetAlert
    fk_name = "target"

class TargetAdmin(admin.ModelAdmin):
    list_display = ('id','name','url')
    inlines = [TargetAlertInline]


class AlertAdmin(admin.ModelAdmin):    
    list_display = ("id", "name", "limit_high")


class TargetAlertAdmin(admin.ModelAdmin):
    def target_name(self, target_alert):
        return Target.objects.get(id=target_alert.target_id).name
    def alert_name(self, target_alert):
        return Alert.objects.get(id=target_alert.alert_id).name
    
    list_display = ("id","target_name", "alert_name")
    
    
admin.site.register(Target, TargetAdmin)
admin.site.register(Stat)
admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertAlertRecipients)
admin.site.register(AlertRecipients)
admin.site.register(TargetAlert, TargetAlertAdmin)
