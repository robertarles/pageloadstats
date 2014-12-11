from django.template import Context, RequestContext, loader
from pageloadstats.models import Target, Alert, TargetAlert
from pageloadstats.models import AlertRecipients, AlertAlertRecipients
from pageloadstats.models import Stat, Stat_Rich
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse
import datetime
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.utils import simplejson
import urllib2
import time
import urlparse

cs_comment_tags = ["request id:", "tag:", "server:", "elapsed:", "elapsed2:"]

SCATTER_DAY_RANGE = 14


def target_list(request):
    latest_target_data = Target.objects.filter(active=1).order_by('name')[:50]
    t = loader.get_template('index.html')
    c = Context({
        'latest_target_data': latest_target_data,
    })
    return HttpResponse(t.render(c))


def manage_targets(request):
    latest_target_data = Target.objects.filter(active=1).order_by('name')
    latest_target_data_inactive = Target.objects.filter(active=0).order_by('name')
    t = loader.get_template('manage_targets.html')
    c = Context({
        'latest_target_data': latest_target_data,
        'latest_target_data_inactive': latest_target_data_inactive,
    })
    return HttpResponse(t.render(c))


def edit_target(request, target_id):
    target_data = Target.objects.get(pk=target_id)
    t = loader.get_template('edit_target.html')
    c = RequestContext(request, {
        'target_data': target_data,
        'available_alerts': get_available_alerts(),
        'current_alert_id': get_current_alert_id(target_id),
    })
    return HttpResponse(t.render(c))


def add_target(request):
    t = loader.get_template('add_target.html')
    c = RequestContext(request, {
        'target_data': None
    })
    return HttpResponse(t.render(c))


def get_available_alerts():
    ###
    # get a list of available active alerts
    ###
    try:
        available_alerts = Alert.objects.filter(active=1)
    except:
        available_alerts = None
    return available_alerts


def get_current_alert_id(target_id):
    ###
    # for target_id, return the alert that is associated, or an empty string if none
    ###
    current_alert_id = ''
    try:
        target_alerts = TargetAlert.objects.filter(target_id=target_id, active=1)
        for target_alert in target_alerts:
            current_alert_id = target_alert.alert_id
    except:
        current_alert_id = 'exception'
    return current_alert_id


def manage_alerts(request):
    alerts = Alert.objects.filter(active=1).order_by('name')
    alerts_inactive = Alert.objects.filter(active=0).order_by('name')
    t = loader.get_template('manage_alerts.html')
    c = Context({
        'alerts': alerts,
        'alerts_inactive': alerts_inactive,
    })
    return HttpResponse(t.render(c))


def manage_recipients(request):
    recipients = AlertRecipients.objects.filter(active=1).order_by('name')
    recipients_inactive = AlertRecipients.objects.filter(active=0).order_by('name')
    t = loader.get_template('manage_recipients.html')
    c = Context({
        'recipients': recipients,
        'recipients_inactive': recipients_inactive,
    })
    return HttpResponse(t.render(c))


def edit_recipient(request, recipient_id):
    recipient = AlertRecipients.objects.get(pk=recipient_id)
    t = loader.get_template('edit_recipient.html')
    c = RequestContext(request, {
        'recipient': recipient
    })
    return HttpResponse(t.render(c))


def edit_alert(request, alert_id):
    alert = Alert.objects.get(pk=alert_id)
    recipients_available = get_available_recipients()
    recipient_ids_associated = get_associated_recipient_ids(alert_id)
    t = loader.get_template('edit_alert.html')
    c = RequestContext(request, {
        'alert': alert,
        'recipients_available': recipients_available,
        'recipient_ids_associated': recipient_ids_associated
    })
    return HttpResponse(t.render(c))

def get_associated_recipient_ids(alertid):
    recipient_ids_associated = []
    alertRecipientsAssoc = AlertAlertRecipients.objects.filter(alert_id=alertid)
    for assoc in alertRecipientsAssoc:
        recipient_ids_associated.append(int(assoc.alert_recipient_id))
    return recipient_ids_associated

def get_available_recipients():
    ###
    # get a list of available active recipients
    ###
    try:
        recipients_available = AlertRecipients.objects.filter(active=1)
    except:
        recipients_available = None
    return recipients_available

def add_alert(request):
    t = loader.get_template('add_alert.html')
    c = RequestContext(request,{
                'alert': None
    })
    return HttpResponse(t.render(c))

def add_recipient(request):
    t = loader.get_template('add_recipient.html')
    c = RequestContext(request,{
                'recipient': None
    })
    return HttpResponse(t.render(c))

## target and alert api calls
###

def target_update(request, target_id):
    target = Target.objects.get(id=target_id)
    target.url = request.POST.get("target_url")
    target.name = request.POST.get("target_name")
    target.active = request.POST.get("target_active")
    target.tags = request.POST.get("target_tags")

    for alert in target.alerts.all():
        target_alert = TargetAlert.objects.get(alert = alert.id, target = target.id)
        target_alert.delete()
    if(request.POST.has_key("alert_id")):
        alert_id = request.POST.get("alert_id")
        if len(alert_id) > 0:
            alert = Alert.objects.get(id=alert_id)
            target_alert = TargetAlert(target=target,alert=alert,active=1)
            target_alert.save()

    target.save()
    response = HttpResponseRedirect("/pls/manage/targets")
    return response

def target_create(request):
    url = request.POST.get("target_url")
    name = request.POST.get("target_name")
    active = request.POST.get("target_active")
    tags = request.POST.get("target_tags")

    target = Target(url=url, name=name, active=active, tags=tags)
    target.save()

    response = HttpResponseRedirect("/pls/manage/targets")
    return response

def target_delete(request):
    pass

def alert_update(request, alert_id):
    alert = Alert.objects.get(id=alert_id)
    alert.active = request.POST.get("alert_active")
    alert.name = request.POST.get("alert_name")
    alert.limit_high = request.POST.get("alert_limit_high")

    for recipient in alert.alert_recipient_list.all():
        alertrecipientassoc = AlertAlertRecipients.objects.get(alert_recipient_id = recipient.id, alert_id=alert_id)
        alertrecipientassoc.delete()
    if(request.POST.has_key("recipient_ids")):
        for id in request.POST.getlist("recipient_ids"):
            alertrecipientassoc = AlertAlertRecipients(alert_recipient_id=id, alert_id=alert_id)
            alertrecipientassoc.save()
    alert.save()
    response = HttpResponseRedirect("/pls/manage/alerts")
    return response

def alert_create(request):
    limit_high = request.POST.get("alert_limit_high")
    active = request.POST.get("alert_active")
    name = request.POST.get("alert_name")

    alert = Alert(name=name, active=active, limit_high=limit_high, limit_low=0, elapsed_low=0, elapsed_high=0)
    alert.save()

    if(request.POST.has_key("recipient_ids")):
        for id in request.POST.getlist("recipient_ids"):
            alertrecipientassoc = AlertAlertRecipients(alert_recipient_id=id, alert_id=alert.id)
            alertrecipientassoc.save()

    response = HttpResponseRedirect("/pls/manage/alerts")
    return response

def alert_delete(request):
    pass

def recipient_update(request, recipient_id):
    recipient = AlertRecipients.objects.get(id=recipient_id)
    recipient.active = request.POST.get("recipient_active")
    recipient.name = request.POST.get("recipient_name")
    recipient.email_address = request.POST.get("recipient_email_address")
    recipient.save()
    response = HttpResponseRedirect("/pls/manage/recipients")
    return response

def recipient_create(request):
    name = request.POST.get("recipient_name")
    active = request.POST.get("recipient_active")
    email_address = request.POST.get("recipient_email_address")

    recipient = AlertRecipients(name=name, active=active, email_address=email_address)
    recipient.save()

    response = HttpResponseRedirect("/pls/manage/recipients")
    return response

def recipient_delete(request):
    pass
###
## END target recipients and alert api calls


def flot(request):
    """
    create a chart page
    """
    targetid = None
    if(request.GET.get("target_id")):
        targetid = request.GET.get("target_id")
    if(request.GET.get("target_tag")):
        targetid = get_ids_by_tag(request.GET.get("target_tag"))
    target = None
    if("," in targetid):
        targeturl = ""
        targetname = "Multiple Targets"
    else:
        target = Target.objects.get(pk=targetid)
        targeturl = target.url
        targetname = target.name
    chartTemplate = loader.get_template('flot.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    trim_above = request.GET.get("trim_above","")
    if(trim_above):
        trim_params = "&trim_above="+trim_above
    else:
        trim_params=""
    c = Context({
        'chart_data_url': "/pls/api/chartline/",
        'target_id': targetid,
        'target_name': targetname,
        'target_url': targeturl,
        'start_date': start_date,
        'trim_above': trim_above,
        'trim_params': trim_params,
        'start_end_params': "&start_date="+start_date+"&end_date="+end_date,
        'end_date': end_date,
    })
    return HttpResponse(chartTemplate.render(c))

def get_ids_by_tag(tag):
    targetidlist = []
    targetlist = Target.objects.filter(tags__contains=tag).filter(active=1)
    for target in targetlist:
        targetidlist.append(str(target.id))
    return ",".join(targetidlist)


def  http_errorchart(request):
    t = loader.get_template('httperrorchart.html')
    c = Context({
        'chart_data_url': "api/ofc2chart/httperrors/",
    })
    return HttpResponse(t.render(c))

def chart_httperrors(request):
    urlList = [] #store urls for mapping to y-axis
    today = datetime.datetime.now()
    daysAgo =today - datetime.timedelta(days=SCATTER_DAY_RANGE)
    stats = Stat_Rich.objects.filter(http_status__gt="200").filter(timestamp__gt=time.mktime(daysAgo.timetuple()) )
    jsonStats = {}
    jsonStats["elements"]=[]
    type={}
    type["type"]="scatter"
    type["colour"]="#FFD600"
    dotStyle = {}
    dotStyle["type"]="anchor"
    dotStyle["colour"]="#D600ff"
    dotStyle["dot-size"]="2"
    dotStyle["rotation"]="45"
    dotStyle["sides"]= "4"
    type["dot-style"]=dotStyle

    #jsonStats["elements"].append(type)
    values={}
    type["values"]=[]

    oldestDay = datetime.datetime.fromtimestamp(stats[0].timestamp).timetuple().tm_yday
    newestDay = datetime.datetime.fromtimestamp(stats[len(stats)-1].timestamp).timetuple().tm_yday
    tsList = [] #to hold a list of timestamps from the stats set
    for stat in stats:
        tsList.append(stat.timestamp)
        jsonStat = {}
       # jsonStat["url"] = stat.url
        if( stat.url not in urlList):
            urlList.append(stat.url)
        jsonStat["y"]=urlList.index(stat.url) + 1
        tenthOfDay=str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_hour / 2.4).replace(".","")
        jsonStat["x"]= str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_yday) +"." + tenthOfDay +str(datetime.datetime.fromtimestamp(stat.timestamp).timetuple().tm_min)
        parsedurl = urlparse.urlparse(stat.url)
        tippath = parsedurl.path
        if(parsedurl.query):
            tippath += "?" + parsedurl.query
        if(len(tippath)>100):
            tippath = tippath[:100]+"..."
        tiphost = parsedurl.hostname
        jsonStat["tip"] = "host: " + tiphost +"\ndate: "+stat.request_date +"\nstatus: "+str(stat.http_status)+  "\npath: "+tippath
        type["values"].append(jsonStat)
    jsonStats["elements"].append(type)
    title={}
    title["text"]="experimental display of http errors by page/day"
    jsonStats["title"]=title
    x_axis = {}
    #x_axis["min"]=oldestDay-1
    #x_axis["max"]=newestDay+1
    x_axis["labels"] = {}
   # x_axis["steps"] = "1"
    x_label_obj = {}
    x_labels = []
    for day in range(SCATTER_DAY_RANGE-1,-1,-1):
        date = datetime.datetime.now()
        labelDate = date-datetime.timedelta(days=day)
        dateString = labelDate.strftime('%m/%d/%Y')
        label = dateString
        if(label not in x_labels):
            x_labels.append(label)
    x_label_obj = {}
    x_label_obj["labels"] = x_labels
   # x_axis["labels"] = x_label_obj
    jsonStats["x_axis"]=x_axis
    y_axis = {}
    y_axis["min"]="0"
    y_axis["max"]=len(urlList)
    jsonStats["y_axis"]=y_axis


    return HttpResponse(simplejson.dumps(jsonStats), mimetype="application/json")


def http_errors(request):
    page=1
    if(request.GET.get('page')):
        page = request.GET.get('page')
    t = loader.get_template('httperrors.html')
    c = Context({
        'page': page,
    })
    return HttpResponse(t.render(c))

def get_http_errors(request):
    rpp = 50
    page=1
    if(request.GET.get('page')):
        page = request.GET.get('page')
    errorListAll = Stat.objects.filter(http_status__gt="200").order_by("-timestamp")
    # contact_list = Contacts.objects.all()
    paginator = Paginator(errorListAll, rpp)
    try:
        errorList = paginator.page(page)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    #return render_to_response('list.html', {"contacts": contacts})
    response_data = {}
    response_data['errors'] = []
    response_data['page'] = page
    response_data["num_pages"] = paginator.num_pages
    for error in errorList:
        error_dict  = {}
        error_dict["id"] = error.id
        error_dict["url"] = error.url
        error_dict["http_status"] = error.http_status
        error_dict["request_date"] =  error.request_date
        response_data["errors"].append(error_dict)
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def daily_avgs(request,tags=["home", "products", "magento", "search", "categories", "recipients"],days=4):
    t = loader.get_template('perfdaily.html')
    start_date = request.GET.get('start_date',"")
    end_date = request.GET.get("end_date","")
    start_date=""
    end_date=""
    days = range(1,int(days)+1)
    if(type(tags) != list):
        tags = tags.split(",")
    c = Context({
        'start_end_params': "%26start_date="+start_date+"%26end_date="+end_date,
        'days': days,
        'tags':tags,
    })
    return HttpResponse(t.render(c))

def get_daily_avg_by_id(request, target_id, days_ago):
    now = int(time.time())
    days_offset = int(days_ago) -1
    ending_midnight = now - (now % (24 * 60 * 60)) - ((24*60*60)*days_offset)
    starting_midnight = ending_midnight - (24 * 60 * 60)
    #print now
    #print ending_midnight
    #print starting_midnight
    stats = Stat_Rich.objects.filter(timestamp__gte=starting_midnight).filter(timestamp__lte=ending_midnight).filter(target_id=target_id)


    sumElapsed = 0
    avgElapsed = 0
    sumLoad = 0
    avgLoad = 0
    target_name = ""

    for stat in stats:
        sumLoad += int(stat.page_load_time) if stat.page_load_time else 0
        sumElapsed += int(stat.elapsed) if stat.elapsed else 0
        if(hasattr(stat,"query_time")): # solr queries dont have elapsed times, but do have an equivilent query_time
            sumElapsed += int(stat.query_time) if stat.query_time else 0
        if(hasattr(stat,"name")):
            target_name = stat.name()

    #if there is data, calculate the averages, else stick with defaults of ZERO
    if(len(stats)>0):
        avgLoad = sumLoad / len(stats)
        avgElapsed = sumElapsed / len(stats)


    response_data = {}
    response_data['data_type'] = "daily averages for id"
    response_data['id'] = target_id
    response_data['days_ago'] = days_ago
    response_data['load'] = avgLoad
    response_data['elapsed'] = avgElapsed
    response_data['target_name'] = target_name
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_daily_avg_by_tag(request, tag, days_ago):
    now = int(time.time())
    days_offset = int(days_ago) -1
    ending_midnight = now - (now % (24 * 60 * 60)) - ((24*60*60)*days_offset)
    starting_midnight = ending_midnight - (24 * 60 * 60)
    #print now
    #print ending_midnight
    #print starting_midnight
    stats = Stat_Rich.objects.filter(timestamp__gte=starting_midnight).filter(timestamp__lte=ending_midnight).filter(target__tags__icontains=tag)


    sumElapsed = 0
    avgElapsed = 0
    sumLoad = 0
    avgLoad = 0

    for stat in stats:
        sumLoad += int(stat.page_load_time) if stat.page_load_time else 0
        sumElapsed += int(stat.elapsed) if stat.elapsed else 0
        if(hasattr(stat,"query_time")): # solr queries dont have elapsed times, but do have an equivilent query_time
            sumElapsed += int(stat.query_time) if stat.query_time else 0

    #if there is data, calculate the averages, else stick with defaults of ZERO
    if(len(stats)>0):
        avgLoad = sumLoad / len(stats)
        avgElapsed = sumElapsed / len(stats)


    response_data = {}
    response_data['data_type'] = "daily average for tag"
    response_data['tag'] = tag
    response_data['days_ago'] = days_ago
    response_data['load'] = avgLoad
    response_data['elapsed'] = avgElapsed
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def flot_line(request):

    target_ids = request.GET.get("target_id")
    targetsdata = None
    if("," in target_ids):
        targetsdata = flot_line_multitarget(request)
    else:
        targetsdata = flot_line_singletarget(request)

    return HttpResponse(simplejson.dumps(targetsdata), mimetype="application/json")

def flot_line_multitarget(request):
    """
    Return the array required to generate a multi target flot chart
    """
    targetids = request.GET.get("target_id").split(",")
    startdate = request.GET.get('start_date')
    enddate = request.GET.get("end_date")
    trimabove = request.GET.get("trim_above")

    statsarray = []
    for targetid in targetids:
        targetstats = get_stats(targetid, startdate, enddate, trimabove)
        statsarray.append(targetstats)

    targetsdata = []
    for targetstats in statsarray:
        targetdata = get_target_load_line(targetstats)
        targetsdata.append(targetdata)

    return targetsdata

def get_target_load_line(targetstats):
    targetdata = {}
    targetdata["data"] = []
    targetdata["label"] = "label not set"
    targetelapsed = {}
    targetelapsed["label"] = "elapsed ms"
    targetelapsed["color"] = "#D35EC9"
    targetsma = {}
    targetsma["label"] = "Moving Avg"
    targetsma["color"] = "#5E9ED3"
    targetalert = {}
    targetalert["label"] = "Alert Level"
    targetalert["color"] = "red"
    loadsum = 0
    smasum = 0
    elapsedsum = 0
    ttfbsum = 0
    currentstat = 0
    for stat in targetstats:
        targetdata["label"] = stat.target.name
        timestamp = None
        page_load_time = None
        elapsed = 0
        server = "unknown"
        if(hasattr(stat, 'timestamp')):
#            timezoneoffset = 28800 # UTC -8 hours
#            timestamp = 1000 * (int(stat.timestamp) - timezoneoffset) # javascript timestamp(ms), adj to UTC
            timestamp = 1000 * int(stat.timestamp) # get the javascript timestamp (unix * 1000)
        if(hasattr(stat, 'page_load_time')):
            page_load_time = int(stat.page_load_time)
            loadsum += page_load_time
        if((hasattr(stat, 'elapsed'))):
            if((stat.elapsed is not None) or (stat.elapsed == 0)):
                try:
                    elapsed = int(stat.elapsed)
                    elapsedsum += int(elapsed)
                except:
                    pass
        if((hasattr(stat, 'server')) and (stat.server is not None)):
            server = stat.server
        if ("data" in targetdata.keys()):
            targetdata["data"].append([timestamp,page_load_time,
                                      "Load " +  str(stat.page_load_time) + " ms</br>" + server + "</br>" + stat.request_date ])
        else:
            targetdata["data"].append([timestamp,page_load_time])
        if ("data" in targetelapsed.keys()):
            elapsedlabel = "Elapsed " + str(elapsed)
            targetelapsed["data"].append([timestamp,elapsed,
                                "Elapsed " + str(elapsed) + " ms</br>" + server + "</br>" + stat.request_date])
        else:
            targetelapsed["data"] = [timestamp,elapsed]
        currentstat += 1

    return targetdata

def flot_line_singletarget(request):
    """
    Return the array required to generate a single target flot chart
    """
    target_id = request.GET.get("target_id")
    start_date = request.GET.get('start_date')
    end_date = request.GET.get("end_date")
    trim_above = request.GET.get("trim_above")

    statsarray = []
    targetstats = get_stats(target_id, start_date, end_date, trim_above)
    statsarray.append(targetstats)

    targetsdata = []
    for targetstats in statsarray:
        targetdata = {}
        targetdata["label"] = "load ms"
        targetdata["color"] = "#5ED379"
        targetelapsed = {}
        targetelapsed["label"] = "elapsed ms"
        targetelapsed["color"] = "#D35EC9"
        targetttfb = {}
        targetttfb['label'] = 'ttfb ms'
        targetttfb['color'] = '#e5e588'
        targetsma = {}
        targetsma["label"] = "Moving Avg"
        targetsma["color"] = "#5E9ED3"
        loadsum = 0
        smasum = 0
        elapsedsum = 0
        ttfbsum = 0

        smaarray = get_sma_new(targetstats, 100, "page_load_time")
        currentstat = 0
        for stat in targetstats:
            timestamp = None
            page_load_time = None
            elapsed = 0
            server = "unknown"
            if(hasattr(stat, 'timestamp')):
#                timezoneoffset = 28800 # UTC -8 hours
#                timestamp = 1000 * (int(stat.timestamp) - timezoneoffset) # javascript timestamp(ms), adj to UTC
                timestamp = 1000 * int(stat.timestamp) # get the javascript timestamp (unix * 1000)
            if(hasattr(stat, 'page_load_time')):
                page_load_time = int(stat.page_load_time)
                loadsum += page_load_time
            if(hasattr(stat, 'ttfb')):
                if stat.ttfb == None:
                    ttfb = 0
                else:
                    ttfb = int(stat.ttfb)
                ttfbsum += ttfb
            if((hasattr(stat, 'elapsed')) and (stat.elapsed is not 'None')):
                try:
                    elapsed = int(stat.elapsed)
                    elapsedsum += elapsed
                except:
                    pass
            if((hasattr(stat, 'server')) and (stat.server is not None)):
                server = stat.server
            if ("data" in targetdata.keys()):
                targetdata["data"].append([timestamp,page_load_time,
                                          "Load " +  str(stat.page_load_time) + " ms</br>" + server + "</br>" + stat.request_date ])
            else:
                targetdata["data"] = [timestamp,page_load_time]
            if ("data" in targetttfb.keys()):
                targetttfb["data"].append([timestamp,ttfb,
                                          "ttfb " +  str(stat.ttfb) + " ms</br>" + server + "</br>" + stat.request_date ])
            else:
                targetttfb["data"] = [timestamp, ttfb]
            if ("data" in targetelapsed.keys()):
                elapsedlabel = "Elapsed " + str(elapsed)
                targetelapsed["data"].append([timestamp,elapsed,
                                    "Elapsed " + str(elapsed) + " ms</br>" + server + "</br>" + stat.request_date])
            else:
                targetelapsed["data"] = [timestamp,elapsed]
            if ("data" in targetsma.keys()):
                targetsma["data"].append([timestamp,smaarray[currentstat],
                                          "SMA " + str(smaarray[currentstat]) + "ms</br>" + stat.request_date])
            else:
                targetsma["data"] = [timestamp,smaarray[currentstat]]
            currentstat += 1
        targetsdata.append(targetdata)
        targetsdata.append(targetelapsed)
        targetsdata.append(targetttfb)
        targetsdata.append(targetsma)

    return targetsdata

##
# This function calls getCheckOutput.  (TODO: Why is it merely a proxy for getCheckOutput()? and why did it need the request object?)
# @param request the http request
# @param target_id the target id to check stats on (an ID or 'all' to check them ALL!)
def check(request, target_id):
    check_output = get_check_output(target_id)
    return HttpResponse(check_output, mimetype="application/json")


##
# Get the stats for the requested target (or 'all' targets)
# @param target_id the ID of the target to check, or 'all' to check them all.
def get_check_output(target_id):
    retval = '{'
    targets = None

    if target_id == 'all':
        targets = Target.objects.filter(active=1)
    else:
        targets = Target.objects.filter(id=target_id).filter(active=1)
    for target in targets:
        status = 200
        try:
            requestdate = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            req = urllib2.Request(target.url)
            start = time.time()
            response = urllib2.urlopen(req)
            content = response.read(1)
            ttfbtime = time.time()
            content += response.read()
            ttlbtime = time.time()
            ttfb = int(round((ttfbtime-start)*1000))
            ttlb = int(round((ttlbtime-start)*1000))
            elapsed = ''
            if 'response-time' in response.headers.keys():
                elapsed = response.headers.get('response-time')
            s = Stat(url=target.url,
                     target_id=target.id,
                     elapsed=elapsed,
                     request_date=requestdate,
                     elapsed2=0,
                     result_count=0,
                     query_time=0,
                     timestamp=start,
                     page_load_time=ttlb,
                     ttfb=ttfb,
                     http_status=str(status))
            s.save()

            retval += "{'id':'" + str(target.id) + "', 'ttfb':'" + str(ttfb) + "', 'elapsed':'" + str(elapsed) + "', 'load_time':'" + str(ttlb) + "', 'http_status':'" + str(status)+ "'}, "

        except IOError, e:
            if hasattr(e, 'reason'):
                retval+= '{"We failed to reach target ' + str(target_id) + '. Reason":"' + str(e.reason) + '"}'
            elif hasattr(e, 'code'):
                retval+= '{The server couldn\'t fulfill the request. Error code":"'+ str(e.code) +'"}'
                status = e.code
            else:
                retval += ""
    retval = retval.strip(",")
    retval += "}"
    return retval

##
# grab a list of the citysearch comments from the current page.  These include server, release, elapsed...
# @parameter response the page's HTML source
# @return a dict of Citysearch comments
def get_comment_dict(response):
    in_comment = False
    comment_dict = {}
    comment_dict["tag"] = ""
    comment_dict["server"] = ""
    comment_dict["elapsed"] = ""
    comment_dict["request id"] = ""
    for line in response:
        line = line.strip()
        if("<!--" in line):
            in_comment = True
        if(in_comment == True):
            for tag in cs_comment_tags:
                if(tag in line.lower()):
                    value = line.split(":")[1].strip()
                    tagname = tag.replace(":", "")
                    comment_dict[tagname] = value
                    # TODO: check how this line is split and saved in the old pls
        if("-->" in line):
            in_comment = False

    return comment_dict

def get_sma_new(stats, sma_window_size, column):
    """
    Get a simple moving average for the current id
    return a list of sma values for the supplied stats list
    @param stats A result set of stats
    @param sma_window_size A number specifying how large of a historic data sample to be used to calculate each sma point.
    @param column the column from the db result set to create an SMA for
    """

    start_ts = stats[0].timestamp
    target_id = stats[0].target_id
    historic_stats = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__lt=start_ts).order_by("-timestamp")[:sma_window_size]

    # calculate an SMA for the first values
    sma_cavg = []
    sma_window = []
    # load up the sma window history
    for hstat in historic_stats:
        if(getattr(hstat,column) != None):
            sma_window.insert(0,int(getattr(hstat,column)))
        else:
            sma_window.insert(0,0)

    reversedStats = []
    reversedStats = stats
    #for stat in stats:
    #    reversedStats.insert(0,stat)
    # for each stat point, add it to the sma window and calculate the current average, insert into array of averages.  (also removing the oldest data point in the window queue)
    for stat in reversedStats:
        value = int(getattr(stat,column))
        #print column +" "+ str(value)
        if(value==None): value = 0
        while(len(sma_window)>=sma_window_size):
            sma_window.pop(0)
        sma_window.append(value)
        avgValue = sum(sma_window) / len(sma_window)
        sma_cavg.append(avgValue)
        #print "average " + str(avgValue)
    return sma_cavg
def get_tags(request):

    targets = Target.objects.filter(active=1)

    tag_dict = {}
    # get a list of tags in use on the targets
    for target in targets:
        target_tags = target.tags.split(",")
        for tag in target_tags:
            tag_dict[tag] = "placing the tag as a key ensures it will be unique, no dupe's"
    tag_list = tag_dict.keys()

    response_data = {}
    response_data['tags']=[]
    response_data['tags'].extend(tag_list)
    response_data['subject']="targets"

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_targets_all(request, return_type):
    targets = Target.objects.filter(active=1)

    response_data = {}
    response_data['targets'] = []
    response_data['subject'] = "all_targets"

    for target in targets:
        target_dict  = {}
        target_dict["id"] = target.id
        target_dict["name"] = target.name
        target_dict["target_url"] = target.url
        target_dict["tags"] = target.tags
        response_data["targets"].append(target_dict)

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def get_targets_by_tag(request, tag, return_type):
    targets = Target.objects.filter(active=1).filter(tags__contains=tag)

    response_data = {}
    response_data['targets'] = []
    response_data['with_tag'] = tag
    response_data['subject'] = "targets_with_tag"

    for target in targets:
        target_dict  = {}
        target_dict["id"] = target.id
        target_dict["name"] = target.name
        target_dict["target_url"] = target.url
        target_dict["tags"] = target.tags
        response_data["targets"].append(target_dict)

    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

def user_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/accounts/login/?next=/pls/')

def get_stats(target_id, start_date, end_date, trim_above):
    default_chart_range=100;
    if( start_date and end_date and trim_above):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).filter(page_load_time__lte=trim_above).exclude(page_load_time__isnull=True).order_by("-timestamp")
    elif (start_date and end_date):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(timestamp__gte=start_date).filter(timestamp__lte=end_date).exclude(page_load_time__isnull=True).order_by("-timestamp")
    elif (trim_above):
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).filter(page_load_time__lte=trim_above).exclude(page_load_time__isnull=True).order_by("-timestamp")[:default_chart_range]
    else:
        stats_rs = Stat_Rich.objects.filter(target_id=target_id).exclude(page_load_time__isnull=True).order_by("-timestamp")[:default_chart_range] # get the latest
    stats = []

    for stat in stats_rs:
        stats.insert(0,stat)

    return stats
