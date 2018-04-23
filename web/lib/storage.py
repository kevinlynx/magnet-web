# kevinlynx@gmail.com
from db import DBConn
from article import Article
import random, time, datetime

class Storage(DBConn):
    def __init__(self, host, user, pwd, db):
        DBConn.__init__(self, host, user, pwd, db)
   
    def load_newest(self, offset = 0, page_cnt = 40):
        rows = self.execute_short('select id, title, created_at, updated_at from documents order by updated_at desc limit %s,%s;' \
            % (offset, page_cnt))
        return map(lambda row: Article.create(row), rows)

    # with Image
    def load_i_newest(self, offset = 0, page_cnt = 40):
        # not fast
        #sql = 'select id, title, created_at, updated_at from documents \
        #        where id in (select id from thumb where status = 0) order by updated_at desc limit %s,%s'
        # faster
        sql = 'select id, title, created_at, updated_at from documents where thumb_status = 0 order by updated_at desc limit %s,%s'
        rows = self.execute_short(sql % (offset, page_cnt))
        return map(lambda row: Article.create(row), rows)

    def doc_count(self):
        # see http://www.imysql.cn/2008_06_24_speedup_innodb_count
        # very slow
        # row = self.execute_short('select count(id) as count from documents')[0]
        # faster
        row = self.execute_short('select count(id) as count from documents where updated_at > 0')[0]
        return int(row['count'])

    def load(self, id):
        rows = self.execute_short('select id, title, content, url, keyword, updated_at, created_at, link from documents where id=%d' % int(id)) 
        return Article.create(rows[0]) if len(rows) > 0 else None

    def recent_count(self, hours):
        start_tm = int(time.time() * 1000) - hours * 3600 * 1000
        dt = datetime.datetime.fromtimestamp(start_tm / 1000)
        row = self.execute_short('select count(id) as count from documents where updated_at >=%s', [dt])[0]
        return int(row['count'])

    def load_img(self, id):
        rows = self.execute_short('select data from thumb where id = %d' % int(id))
        data = rows[0]['data'] if rows else None
        return data

    def image_exist(self, id):
        rows = self.execute_short('select status from thumb where id = %d' % int(id))
        return rows[0]['status'] == 0 if rows else False

if __name__ == '__main__':
    s = Storage('127.0.0.1', 'kevin', '111111', 'magnet')
    print(s.recent_count(2))

