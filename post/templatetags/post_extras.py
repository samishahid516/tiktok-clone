import re
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(needs_autoescape=True)
def hashtag_links(value, autoescape=True):
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    escaped = esc(value)
    result = re.sub(
        r'#(\w+)',
        r'<a href="/hashtag/\1/" class="text-rose-500 hover:text-rose-600 font-medium">#\1</a>',
        escaped
    )
    return mark_safe(result)
