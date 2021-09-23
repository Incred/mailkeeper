import re

from email import policy, message_from_string
from email.parser import Parser
from email.utils import getaddresses, unquote
import collections.abc
from math import ceil


"""
Parse headers of email message and return them as a dict.
Take into account multipart messages with text and html content types.

"""

VERP_ADDRESS_RE = re.compile(r'\+(.+)=(.+)@.*')
MIME_TYPES = {
    'text': 'text/plain',
    'html': 'text/html',
}


class EmailParser():
    def __init__(self, content=None, raw_content=None):
        self.data = {}
        self.raw_content = raw_content
        if content is not None:
            self.raw_content = message_from_string(content,
                                                   policy=policy.default)

    def get_data(self):
        return self.data

    def _parse_body(self):
        for part in self.raw_content.walk():
            if part.is_multipart():
                continue
            for mime_type in MIME_TYPES:
                if part.get_content_type() == MIME_TYPES[mime_type]:
                    self.data[mime_type] = MIME_TYPES[mime_type] + '\n'
                    self.data[mime_type] += part.get_payload().replace('\r',
                                                                       '')

    def _clean_varp(self, to):
        match = VERP_ADDRESS_RE.search(to)
        if match:
            local, domain = match.groups()
            assert all((local, domain))
            to = '{}@{}'.format(local, domain)
        return to

    def _get_to(self):
        tos = self.raw_content.get_all('to', [])
        tos = [self._clean_varp(to) for to in tos]
        ccs = self.raw_content.get_all('cc', [])
        all_recipients = getaddresses(tos + ccs)
        return list(map(lambda r: r[1], all_recipients))

    def parse(self):
        tos = self._get_to()
        self.data['email'] = self.raw_content.get('x-original-to') or tos[0]
        self.data['to'] = [tos]
        self.data['subject'] = self.raw_content.get('subject')
        self.data['from_email'] = self.raw_content.get('from')
        self.data['_id'] = unquote(self.raw_content.get('message-id').strip())
        self.data['raw_content'] = self.raw_content.as_string()
        self._parse_body()


class BouncedEmailParser(EmailParser):
    original_email = EmailParser('')
    delivery_status_dict = {}

    STATUS_FIELDS = ('Status', 'Action', 'Diagnostic-Code')
    ORIGINAL_MESSAGE_TYPES = ('text/rfc822-headers', 'message/rfc822',
                              'message/global', 'message/global-headers')
    DELIVERY_STATUS_TYPES = ('message/delivery-status',
                             'message/global-delivery-status')

    def _parse_body(self):
        """
        To get message-id of bounced email we need to parse original email,
        which is attached to bounce report with content in part with content
        type "text/rfc822-headers" or "message/rfc822".
        Then we parse also "message/delivery-status" part (which can be
        multipart) to obtain extended delivery status (code error and
        description)

        """
        super()._parse_body()
        delivery_status_parts = []
        for part in self.raw_content.walk():
            if part.get_content_type() in self.ORIGINAL_MESSAGE_TYPES:
                if part.is_multipart():
                    email = part.get_payload()[0]
                    self.original_email = EmailParser(raw_content=email)
                else:
                    self.original_email = EmailParser(part.get_payload())
                self.original_email.parse()
            if part.get_content_type() in self.DELIVERY_STATUS_TYPES:
                if part.is_multipart():
                    delivery_status_parts.extend(part.get_payload())
                else:
                    delivery_status_parts.extend([part.get_payload()])
        for status_part in delivery_status_parts:
            # In case global-delivery-status part contnains several header
            # blocks separated with a blank line email library parser thinks
            # its a nested message and puts second block of headers into body,
            # so we have to use get_payload() method and parse those headers
            # as a string
            payload = status_part.get_payload()
            if payload:
                delivery_status_parts.append(
                    Parser(policy=policy.default).parsestr(payload))
            self.delivery_status_dict.update({
                key: value for key, value in status_part.items() if key in
                self.STATUS_FIELDS
            })

    @property
    def delivery_status_as_str(self):
        return '\n'.join(('{}: {}'.format(k, v) for k, v
                          in self.delivery_status_dict.items()))
