# -*- coding: utf-8 -*-  
# kevinlynx@gmail.com
# 07.30.2016
# search from solr
import random
from article import Article
import pysolr
from log import logger

class Search(object):
    TIMEOUT = 10
    QF = 'title^8 linkStr^4 content^2'

    def __init__(self, url):
        self.solr = pysolr.Solr(url, timeout = self.TIMEOUT)

    def simple_search(self, q, **kwarg):
        results = self.solr.search(q, defType = 'dismax', fl = 'title,id', qf = self.QF, **kwarg)
        return map(lambda r: Article.create(r), results), results.hits, results.qtime

    def search(self, q, start, count, **kwarg):
        kwarg.update({ 'hl': 'true', 'hl.fl': 'title content linkStr', 'hl.fragsize': 100,
                'hl.simple.pre': '<span class="hl">', 'hl.simple.post': '</span>'})
        results = self.solr.search(q, defType = 'dismax', qf = self.QF, 
            start = start, rows = count, fl = 'title,linkStr,id,updated_at', **kwarg)
        def hl_field(d, f):
            return d.get(f, [''])[0]
        def with_highlighting(id):
            d = results.highlighting[str(id)]
            title = hl_field(d, 'title')
            content = hl_field(d, 'content') or hl_field(d, 'linkStr')
            return title, content 
        def to_article(r):
            a = Article.create(r)
            ht, hc = with_highlighting(a.id) 
            if ht: a.hl_title = ht
            if hc: a.content = hc
            return a
        return map(to_article, results), results.hits, results.qtime

if __name__ == '__main__':
    pass

