from django import template
import datetime
register = template.Library()


@register.filter('print_timestamp')
def print_timestamp():
    return "text1"
    #return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    #try:
        #assume, that timestamp is given in seconds with decimal point
        #ts = float(timestamp)
    #except ValueError:
        #return None
    #return datetime.datetime.fromtimestamp(ts)

#register.filter(print_timestamp)