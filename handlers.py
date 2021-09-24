import asyncio
import json
import logging
import base64
import hmac
import hashlib
from aiohttp_requests import requests
from sqlalchemy import update, and_

from db import DB, Email
from utils import EmailParser, BouncedEmailParser
import config


logger = logging.getLogger(__name__)


class MainHandler:

    processed = None

    def __init__(self, sender, recipient, msg):
        self.msg = msg
        self.sender = sender
        self.recipient = recipient
        self.data = {}
        self.db = DB(config.A_DB_URL)
        self.db.connect()

    async def process(self):
        self.data = message = self._parse_email(self.msg)
        event = None
        _, recipient_domain = self.recipient.split('@')
        if self.recipient in config.IGNORE_EMAIL_LIST:
            self.data = None
            return
        if recipient_domain == config.BOUNCED_EMAIL_DOMAIN:
            await self._process_bounced()
            event = 'bounced'
        elif recipient_domain == config.INBOUND_EMAIL_DOMAIN:
            event = 'inbound'
        self.data['event'] = event
        if event is None:
            return

        content_json = self._make_json(event, message)
        data = {
            'mandrill_events': content_json
        }
        try:
            if config.EVENTS_URLS:
                response = await requests.post(
                    config.EVENTS_URLS[event],
                    data=data,
                    headers={
                        config.X_MAILKEEPER_HEADER: self.get_signature(data,
                                                                       event)
                    }
                )
                response_msg = '{} {}'.format(response.status, response.reason)
                logger.info('%s event handled (Message-ID: %s, Recipient:'
                            ' %s): %s', event, message['_id'],
                            message['email'], response_msg)
        except Exception as e:
            logger.error(e)
            raise
        else:
            self.processed = True

    async def _process_bounced(self):
        """
        In case of bounced response we need to update status of original
        email which is bounced and put the error to extended_delivery_status
        to display it on the admin page
        """
        try:
            bounced_email_parser = BouncedEmailParser(self.data['raw_content'])
            bounced_email_parser.parse()
            data = bounced_email_parser.original_email.data
            msg_id = data.get('_id') if data else None
            delivery_status = bounced_email_parser.delivery_status_as_str
            recipient = data.get('email')
        except Exception as exc:
            logger.error('Error during processing bounced: %s', exc)
            raise
        else:
            if not all((msg_id, delivery_status)):
                logger.error(
                    'Both msg_id and delivery_status must not be empty:\n'
                    'bounced message-id: %s\n'
                    'delivery_status: %s\n'
                    'recipient: %s\n', msg_id, delivery_status, recipient)
            async with self.db.session() as session:
                await session.execute(update(Email).where(and_(
                    Email.message_id == msg_id,
                    Email.recipient == recipient)).values(
                        status='bounced',
                        extended_delivery_status=delivery_status[:255],
                    )
                )

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
