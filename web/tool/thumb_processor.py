# kevinlynx@gmail.com
import os, sys, time

HOME_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(HOME_PATH, ".."))
sys.path.append(os.path.join(HOME_PATH, "../lib"))

try:
    from BeautifulSoup import BeautifulSoup
except:
    from bs4 import BeautifulSoup
from db import DBConn
from img_thumb import Thumber
from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog [options]")
parser.add_option("-b", "--db", dest="db_host", default='127.0.0.1')
parser.add_option("-u", "--user", dest="db_user", default="kevin")
parser.add_option("-d", "--pwd", dest="db_pwd", default="111111")
parser.add_option("-c", "--count", dest="count", help ='worker count', default = 10)
(options, args) = parser.parse_args()

class ImgLoader:
    def __init__(self, db_conf):
        self.db = DBConn(db_conf['host'], db_conf['user'], db_conf['pwd'], db_conf['db'])

    def load_tasks(self, count):
        # slow
        #sql = 'select id, content from documents where id not in (select id from thumb) order by updated_at desc limit %d' % count
        sql = 'select id, content from documents where thumb_status = 1 order by updated_at desc limit %d' % count
        rets = self.db.execute_short(sql)
        if not rets: return None
        tasks = []
        for rec in rets:
            url = self._get_image_url(rec['content'])
            if not url: 
                self.on_done({'id': rec['id']}, None, 2)
                continue
            tasks.append({'id': rec['id'], 'url': url})
        return tasks

    def on_done(self, task, data, status = 3):
        sql = 'insert into thumb(id, data) values (%s, %s)'
        if not self._thumb_exist(task['id']):
            self.db.update(sql, (task['id'], data if data else None))
        self._update_doc_status(task['id'], 0 if data else status)

    def _update_doc_status(self, id, status):
        sql = 'update documents set thumb_status = %s where id = %s'
        print('update doc set status: %d: %s' % (id, status))
        self.db.update(sql, (status, id))

    def _thumb_exist(self, id):
        sql = 'select id from thumb where id=%d' % int(id)
        return self.db.execute_short(sql)

    def _get_image_url(self, content):
        if not content: return ''
        soup = BeautifulSoup(content)
        imgs = soup.find('img')
        return imgs.get('src') if imgs else ''

def main():
    loader = ImgLoader({'host': options.db_host, 'user': options.db_user, 'pwd': options.db_pwd, 'db': 'magnet'})
    th = Thumber(loader, int(options.count))
    th.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('exiting...')
        th.stop()

if __name__ == '__main__':
    main()

