import re
from email import policy, message_from_string
from email.utils import getaddresses
import collections.abc
from math import ceil


"""
Parse headers of email message and return them as a dict.
Take into account multipart messages with text and html content types.

"""

VERP_ADDRESS_RE = re.compile(r'\+(.+)=(.+)@.*')


class EmailParser():
    def __init__(self, content=None):
        self.data = {}
        self.raw_content = message_from_string(content, policy=policy.default)

    def get_data(self):
        return self.data

    def _parse_body(self):
        for part in self.raw_content.walk():
            if part.is_multipart():
                continue
            if part.get_content_type() == 'text/plain':
                self.data['text'] = part.get_payload().replace('\r', '')
            if part.get_content_type() == 'text/html':
                self.data['html'] = part.get_payload()

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
        self.data['email'] = tos[0]
        self.data['to'] = [tos]
        self.data['subject'] = self.raw_content.get('subject')
        self.data['from_email'] = self.raw_content.get('from')
        self.data['_id'] = self.raw_content.get('message-id')
        self.data['raw_content'] = self.raw_content.as_string()
        self._parse_body()
