# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import logging
import threading

from pmessaging.models import Message
from pmessaging.settings import MESSAGE_REMOVAL_FREQUENCY
from pmessaging.settings import OLD_MESSAGES_DELETED_IN

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


def delete_old_messages():
    """ This function deletes all messages which are older than the OLD_MESSAGES_DELETED_IN constant."""
    logging.info('Old message cleanup started...')

    now = datetime.datetime.now()
    delete_before = now + datetime.timedelta(days=OLD_MESSAGES_DELETED_IN)

    messages = Message.objects.filter(sent_at__date__lte=delete_before)

    for message in messages:
        # lets delete the image file, thumbnail and instance
        message.delete()
        logging.info('deleted an old message')
    logging.info('Old message cleanup finished...')


def launch_old_message_remover():
    """ This function runs the old message delete function every hour (freq can be changed in settings)."""
    threads = threading.Timer(MESSAGE_REMOVAL_FREQUENCY, launch_old_message_remover)
    threads.start()
    delete_old_messages()


launch_old_message_remover()