# -*- coding: utf-8 -*-  
# latest movies from douban.com
import json
import utils
from kv_cache import with_cache, use_cache

class DoubanMovie:
    API = 'https://movie.douban.com/j/search_subjects'

    def __init__(self, cache):
        self.cache = cache

    @use_cache
    def query(self, type, tag, page_limit = 40, page_start = 0):
        resp = utils.http_get(self.API, 
                {'type': type, 'tag': tag, 'sort': 'recommend', 'page_limit': page_limit, 'page_start': page_start})
        return json.loads(resp)['subjects'] if resp else None

    def format_key(self, type, tag, page_limit = 40, page_start = 0):
        return 'douban/%s/%s/%d/%d' % (type, tag, page_limit, page_start)

