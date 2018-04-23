# kevinlynx@gmail.com
from datetime import datetime
import utils, string
import time, json

class Article(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.hl_title = title
        self.content = ''
        self.link = []
        self.updated_at = 0
        self.created_at = 0
        self.keyword = []
        self.url = ''
        self.link_str = []

    def _fix_content(self):
        self.content = '\n'.join(self.link_str)[:200]

    def get_link_types(self):
        return list(set(reduce(lambda ret, l: ret + [self._link_type(l['text'], l['url'])], self.link_str, [])))

    def _link_type(self, text, url):
        for t in ['magnet', 'thunder', 'ftp', 'ed2k']:
            if url.startswith(t): return t
        if text.endswith('.torrent') or url.endswith('.torrent'): return 'torrent'
        return 'other'

    @staticmethod
    def create(rec):
        id = rec['id']
        title = rec['title']
        a = Article(id, title)
        a.content = rec.get('content', '')
        a.url = rec.get('url', '')
        a.link = json.loads(rec.get('link')) if rec.has_key('link') else []
        a.updated_at = utils.as_datetime(rec.get('updated_at', 0))
        a.created_at = utils.as_datetime(rec.get('created_at', 0))
        a.is_updated = a.updated_at != a.created_at and datetime.today().date() == a.updated_at.date()
        a.keyword = rec.get('keyword', '').split(',')
        def parse_link(s):
            secs = s.split('\t')
            return {'text': secs[0], 'url': secs[1]}
        if not a.content: a._fix_content()
        a.link_str = map(parse_link, filter(lambda n: n, rec.get('linkStr', '').split('\n')))
        return a

