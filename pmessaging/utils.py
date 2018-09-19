from django.contrib.auth import get_user_model
from django.utils.text import wrap
from django.utils.translation import ugettext


def format_quote(sender, body):
    """
    Wraps text at 55 chars and prepends each
    line with `> `.
    Used for quoting messages in replies.
    """
    lines = wrap(body, 55).split('\n')
    for i, line in enumerate(lines):
        lines[i] = "> %s" % line
    quote = '\n'.join(lines)
    return ugettext(u"%(sender)s wrote:\n%(body)s") % {
        'sender': sender,
        'body': quote
    }

def get_username_field():
    return get_user_model().USERNAME_FIELD
