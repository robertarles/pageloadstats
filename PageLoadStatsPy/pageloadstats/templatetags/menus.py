from PageLoadStatsPy.pageloadstats.models import Target
from django import template

register = template.Library()

#@register.inclusion_tag('target_menu.html')
def target_menu():
    targets = Target.objects.filter(active=1).order_by('name')[:50]
    targets_by_tag = get_targets_by_tag()

    return {"targets_by_tag":targets_by_tag,}
#register.inclusion_tag('link.html', takes_context=True)(jump_link)
register.inclusion_tag('target_menu.html')(target_menu)


def get_targets_by_tag():
        
    targets = Target.objects.filter(active=1)
    
    tag_dict = {}
    
    # get a list of tags in use on the targets
    for target in targets:
        if(target.tags):
            tag_list= target.tags.replace(" ","")
            target_tags = tag_list.split(",")
            for tag in target_tags:
                if (not tag in tag_dict):
                    tag_dict[tag] = {}
                if (not target.name in tag_dict[tag]):
                    tag_dict[tag][target.name] = {}
                tag_dict[tag][target.name] = target.id
                #{"home":{"la":1,"phoenix",2}, "bpp":{"denver":21,"portland":24}}
    
    
    return tag_dict