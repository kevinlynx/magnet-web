# kevinlynx@gmail.com
import os, sys, codecs, random
from urlparse import urlparse

HOME_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(HOME_PATH, "../lib"))

from storage import Storage
from search import Search
import utils
import jieba
import kv_cache

MEIDA_FILE = 'mp4,mkv,rmvb'.split(',')
PROTOCOL = 'http,ftp'.split(',')

class Agg(object):
    def __init__(self, solr_url, db_conf):
        self.search = Search(solr_url)
        self.storage = Storage(db_conf['host'], db_conf['user'], db_conf['pwd'], db_conf['db'])
        self.kvs = kv_cache.create(alive_time = 300)

    def get_cache(self):
        return self.kvs

    def load(self, id, ext_kw = True):
        article = self.storage.load(id)
        if not article: return None
        if ext_kw: self._extend_keywords(article)
        article.text_content = utils.strip_html(article.content) if article.content else ''
        return article

    def load_list(self, offset, cnt):
        articles = self.storage.load_newest(offset, cnt)
        return articles

    def load_related(self, article, count):
        if len(article.ext_keyword) == 0: return []
        kw = article.ext_keyword[0]
        articles, hits, qtime = self.search.simple_search(kw, start = 0, rows = count or 10)
        return articles, kw

    def load_newest_kw(self, count):
        articles = self.storage.load_newest(0, count)
        kws = []
        for a in articles:
            kws.extend(self._extend_keywords(a))
        return list(set(kws))[:count]

    def _extend_keywords(self, article):
        def valid(t): return len(t) > 1
        words = filter(valid, jieba.lcut(article.title, cut_all = False))
        article.ext_keyword = list(set(words))
        article.keyword.extend(article.ext_keyword)
        return article.ext_keyword

    # SEO stuff
    def insert_inner_anchor(self, article, search_fn):
        content = article.content
        for k in article.ext_keyword[:4]:
            url = search_fn(k)
            content = content.replace(k, '<a href="%s" target="_blank">%s</a>' % (url, k), 1)
        article.content = content     
        
