import asyncio
import json
import logging
import base64
import hmac
import hashlib
from aiohttp_requests import requests

from utils import EmailParser
import config


log = logging.getLogger('mail.debug')


class MainHandler:

    processed = None

    def __init__(self, sender, recipient, msg):
        self.msg = msg
        self.sender = sender
        self.recipient = recipient
        self.data = {}

    async def process(self):
        self.data = message = self._parse_email(self.msg)
        event = None
        _, recipient_domain = self.recipient.split('@')
        if self.recipient in config.IGNORE_EMAIL_LIST:
            log.info('Ignore recipient: {}'.format(self.recipient))
            self.data = None
            return
        if recipient_domain == config.BOUNCED_EMAIL_DOMAIN:
            event = 'bounced'
        elif recipient_domain == config.INBOUND_EMAIL_DOMAIN:
            event = 'inbound'
        self.data['event'] = event
        if event is None:
            log.error('No event selected')
            return

        content_json = self._make_json(event, message)
        data = {
            'mandrill_events': content_json
        }
        try:
            response = await requests.post(
                config.EVENTS_URLS[event],
                data=data,
                headers={
                    config.X_MAILKEEPER_HEADER: self.get_signature(data, event)
                }
            )
        except Exception as e:
            log.error(e)
            raise
        else:
            self.processed = True

    def _parse_email(self, content):
        email_parser = EmailParser(content=content)
        email_parser.parse()
        return email_parser.get_data()

    def _make_json(self, event, message):
        data = {}
        data['event'] = event
        data['msg'] = message
        return json.dumps([data])

    def get_signature(self, data, event):
        signed_data = config.EVENTS_URLS[event]
        for key, value in sorted(data.items()):
            signed_data += key
            signed_data += value
        return base64.b64encode(
            hmac.new(
                config.WEBHOOK_KEYS[event],
                msg=signed_data.encode("utf-8"),
                digestmod=hashlib.sha1
            ).digest()
        ).decode()