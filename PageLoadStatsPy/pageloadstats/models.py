# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Alert(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    limit_low = models.BigIntegerField()
    limit_high = models.BigIntegerField()
    elapsed_low = models.BigIntegerField()
    elapsed_high = models.BigIntegerField()
    active = models.IntegerField()
    class Meta:
        db_table = u'alert'

class AlertAlertRecipients(models.Model):
    alert_id = models.BigIntegerField()
    alert_recipient_id = models.BigIntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'alert_alert_recipients'

class AlertRecipients(models.Model):
    email_address = models.TextField()
    name = models.TextField()
    id = models.BigIntegerField(primary_key=True)
    active = models.IntegerField()
    class Meta:
        db_table = u'alert_recipients'

class Find(models.Model):
    id = models.IntegerField(primary_key=True)
    regex = models.TextField()
    present = models.IntegerField()
    name = models.TextField()
    target_id = models.IntegerField()
    active = models.IntegerField()
    count = models.IntegerField(null=True, blank=True)
    operator = models.CharField(max_length=135)
    class Meta:
        db_table = u'find'

class Settings(models.Model):
    sma_window_size = models.IntegerField()
    alert_solr_growth_limit = models.FloatField()
    alert_solr_shrink_limit = models.FloatField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'settings'

class Stat(models.Model):
    url = models.TextField()
    elapsed = models.TextField(blank=True)
    elapsed2 = models.TextField(blank=True)
    tag = models.TextField(blank=True)
    server = models.TextField(blank=True)
    request_id = models.TextField(blank=True)
    id = models.BigIntegerField(primary_key=True)
    timestamp = models.BigIntegerField()
    page_load_time = models.BigIntegerField()
    request_date = models.TextField(blank=True)
    target_id = models.BigIntegerField()
    http_status = models.BigIntegerField(null=True, blank=True)
    query_time = models.BigIntegerField(null=True, blank=True)
    result_count = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'stat'
    
class Stat_Rich(models.Model):
    url = models.TextField()
    elapsed = models.TextField(blank=True)
    elapsed2 = models.TextField(blank=True)
    tag = models.TextField(blank=True)
    server = models.TextField(blank=True)
    request_id = models.TextField(blank=True)
    id = models.BigIntegerField(primary_key=True)
    timestamp = models.BigIntegerField()
    page_load_time = models.BigIntegerField()
    request_date = models.TextField(blank=True)
    target_id = models.BigIntegerField()
    http_status = models.BigIntegerField(null=True, blank=True)
    query_time = models.BigIntegerField(null=True, blank=True)
    result_count = models.BigIntegerField(null=True, blank=True)
    class Meta:
        db_table = u'stat'
    def alert_level(self):
        # TODO: create a function that looks up the alert level
        target_alert = TargetAlert.objects.get(target_id=self.target_id)
        alert_info = Alert.objects.get(pk=target_alert.alert_id)
        return alert_info.limit_high

class Target(models.Model):
    url = models.TextField()
    active = models.IntegerField()
    id = models.BigIntegerField(primary_key=True)
    type = models.TextField(blank=True)
    name = models.TextField(blank=True)
    class Meta:
        db_table = u'target'

class TargetAlert(models.Model):
    target_id = models.BigIntegerField()
    alert_id = models.BigIntegerField()
    active = models.IntegerField()
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'target_alert'

class TargetCass(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.CharField(max_length=135)
    name = models.CharField(max_length=135)
    type = models.CharField(max_length=135)
    active = models.CharField(max_length=135)
    class Meta:
        db_table = u'target_cass'

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    password = models.TextField()
    email = models.TextField()
    class Meta:
        db_table = u'user'

