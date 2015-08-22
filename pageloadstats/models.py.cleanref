from django.db import models

class Target(models.Model):
    url = models.CharField(max_length=750)
    name = models.CharField(max_length=100)
    url_type = models.CharField(max_length=100)
    active = models.IntegerField()
    def __unicode__(self):
        return self.name
    
class Alert(models.Model):
    name = models.CharField(max_length=100)
    limit_high = models.IntegerField()
    active = models.IntegerField()
    def __unicode__(self):
        return self.name
    
class Stat(models.Model):
    url = models.CharField(max_length=750)
    elapsed = models.IntegerField()
    elapsed2 = models.IntegerField()
    tag = models.CharField(max_length=100)
    server = models.CharField(max_length=100)
    request_id = models.CharField(max_length=100)
    request_date = models.CharField(max_length=100)
    timestamp = models.IntegerField()
    target_id = models.IntegerField()
    load_time = models.IntegerField()
    http_status = models.IntegerField()
    result_count = models.IntegerField()
    query_time = models.IntegerField()
    def __unicode__(self):
        return self.url
