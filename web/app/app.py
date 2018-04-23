#!/bin/env python
# -*- coding: utf-8 -*-  
# kevinlynx@gmail.com
import os, sys, json, datetime, random, time, io

HOME_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(HOME_PATH, ".."))
sys.path.append(os.path.join(HOME_PATH, "../lib"))

import flask
from flask import Flask, request, Response, make_response, send_from_directory, send_file
from flask import render_template, redirect, url_for, jsonify
from agg import Agg
from douban import DoubanMovie
import utils
import jieba

def app_startup(file, local = False, black_file = 'black_list.txt'):
    jieba.initialize()
    conf = json.loads(utils.read_file_string(file))
    app.agg = Agg(conf['solr'], conf['db'])
    app.is_local = local
    app.black_ids = filter(lambda s: s, map(lambda s: s.strip(), utils.read_file_string(black_file).split('\n')))

index_cnt_in_page = 50
search_cnt_in_page = 20
i_list_cnt_in_page = 30
page_display = 5
max_page = 10

app = Flask(__name__, static_url_path = '/static')
app.debug = True
app.startup = app_startup

def is_debug(): return request.args.get('t', '')

def split_list(list_, cnt):
    rets = []
    tmp_l = []
    for i in range(1, 1 + len(list_)):
        tmp_l.append(list_[i - 1])
        if i % cnt == 0:
            rets.append(tmp_l)
            tmp_l = []
    return rets

@app.context_processor
def reg_processor():
    def nav_css(t):
        return 'current-menu-item' if request.path == t else ''
    def is_today(t):
        return datetime.datetime.today().date() == t.date()
    def is_index():
        return request.path == '/'
    return dict(is_local = lambda: app.is_local,
            is_debug = is_debug, nav_css = nav_css, is_today = is_today,
            is_i_list = lambda: request.path.startswith('/ilist'),
            split_list = split_list,
            is_index = is_index)

@app.template_filter('date_brief')
def format_timestamp(t):
    if type(t) == long or type(t) == int:
        t = datetime.datetime.fromtimestamp(t / 1000)
    if not t: return 'invalid date'
    return t.strftime('%Y/%m/%d %H:%M')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/favicon.ico')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/')
def index():
    newest_kws = app.agg.load_newest_kw(10)
    recent_count = app.agg.storage.recent_count(24)
    newest = load_newest(18)
    return render_template('index.html', newest_kws = newest_kws, recent_count = recent_count, 
            results = newest)

@app.route('/list')
def list():
    p = int(request.args.get('p', 0))
    if p > max_page: p = max_page
    def url_fn(p):
        return url_for('list', p = p)
    total_cnt = limit_total_cnt(app.agg.storage.doc_count())
    page_nav = get_page_nav(total_cnt, p, url_fn, index_cnt_in_page)
    start = p * index_cnt_in_page
    articles = app.agg.load_list(start, index_cnt_in_page)
    newest = load_newest()
    return render_template('list.html', articles = articles, newest = newest, page_nav = page_nav)

@app.route('/ilist')
def i_list():
    p = int(request.args.get('p', 0))
    if p > max_page: p = max_page
    def url_fn(p):
        return url_for('i_list', p = p)
    start = p * i_list_cnt_in_page
    articles = app.agg.storage.load_i_newest(start, i_list_cnt_in_page)
    if not articles:
        return redirect(url_for('i_list', p = p - 1)) if p > 0 else \
                redirect(url_for('index'))
    total_cnt = limit_total_cnt(app.agg.storage.doc_count())
    page_nav = get_page_nav(total_cnt, p, url_fn, i_list_cnt_in_page)
    newest = load_newest()
    return render_template('i_list.html', articles = articles, newest = newest, page_nav = page_nav)

@app.route('/view/<id>.html')
def view(id):
    article = app.agg.load(int(id))
    if not article: return redirect(url_for('index'))
    if str(id) in app.black_ids:
        return render_template('redirect.html', article = article)
    app.agg.insert_inner_anchor(article, lambda k: url_for('search', q = k))
    # cheat search engine this article context is the original 
    if article.id > 0:
        ext_article = app.agg.load(article.id - 1)
        article.ext_content = ext_article.text_content[0:200]
    newest = load_newest()
    related, kw = app.agg.load_related(article, 10)
    return render_template('view.html', article = article, newest = newest, related = related, related_kw = kw)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    if not q: return redirect(url_for('index'))
    page = int(request.args.get('p', '0'))
    offset = page * search_cnt_in_page
    articles, hits, qtime = app.agg.search.search(q, offset, search_cnt_in_page)
    def url_fn(p):
        return url_for('search', p = p, q = q)
    page_nav = get_page_nav(hits, page, url_fn, search_cnt_in_page)
    newest = load_newest()
    return render_template('search.html', articles = articles, page_nav = page_nav, hits = hits, qtime = qtime, q = q,
            newest = newest)

@app.route('/e/<type>/<tag>')
def expl(type, tag):
    # encode to `str' type
    type = type.encode('utf-8')
    tag = tag.encode('utf-8')
    douban = DoubanMovie(app.agg.get_cache())
    results = douban.query(type, tag)
    newest = load_newest()
    return render_template('expl_movie.html', results = results or [], newest = newest)

@app.route('/img/<id>')
def get_img(id):
    data = app.agg.storage.load_img(id)
    if not data:
        return send_from_directory(app.static_folder, 'images/404.JPG'), 404
    return send_file(io.BytesIO(data), mimetype = 'image/jpg')

# partial html displayed on search page
@app.route('/img/search/<id>')
def get_img_search(id):
    title = request.args.get('title', '')
    if not id: return 'invalid id', 404
    exist = app.agg.storage.image_exist(id)
    if not exist: return 'not found', 404
    return render_template('search_thumb.html', id = id, title = title)

@app.route('/recommend/slide')
def get_recommend_slide():
    douban = DoubanMovie(app.agg.get_cache())
    recs = douban.query('movie', '热门', 20, 0) or []
    results = []
    one_list = []
    icnt = 4
    for i in range(1, 1 + len(recs)):
        one_list.append(recs[i - 1])
        if i % 4 == 0:
           results.append(one_list)
           one_list = []
    return render_template('slide.html', results = results)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', code = 404)

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', code = 500)

# NOTE: only load docs with images now
def load_newest(count = 10):
    return app.agg.storage.load_i_newest(0, count)

def get_page_nav(total_cnt, page, url_fn, cnt_in_page):
    total_page = total_cnt / cnt_in_page + 1
    page = page if page <= total_page else total_page
    start = page - page_display / 2
    start = start if start >= 0 else 0
    end = start + page_display if start + page_display <= total_page else total_page
    page_nav = {
        'cur': page,
        'total': total_page,
        'start': start,
        'end': end,
        'format_url': url_fn
    }
    return page_nav

def limit_total_cnt(total):
    limit_total = index_cnt_in_page * max_page
    return total if total < limit_total else limit_total

if __name__ == '__main__':
    app.startup('app.cfg', False)
    app.run(host = '0.0.0.0', port = 7000)

