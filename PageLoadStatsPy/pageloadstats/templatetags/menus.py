from PageLoadStatsPy.pageloadstats.models import Target
from django import template

register = template.Library()

#@register.inclusion_tag('target_menu.html')
def target_menu():
    targets = Target.objects.filter(active=1).order_by('name')[:50]
    target_menu_dict = {}
    for target in targets:
        for tag in target.tags.split(","):
            if(target_menu_dict.has_key(tag)):
                #print type(target_menu_dict[tag])
                tempList = target_menu_dict[tag]
                tempList.append(target)
                target_menu_dict[tag]=tempList
                #target_menu_data[tag].append(target)
            else:
                target_menu_dict[tag] = [target]
    target_menu_text = "tag stuff"
    return target_menu_text
#register.inclusion_tag('link.html', takes_context=True)(jump_link)
register.inclusion_tag('target_menu.html')(target_menu)