# kevinlynx@gmail.com
# 2016.08.10
# to download images and make thumbnail
import utils
from PIL import Image
import threading, os, time
import random
from Queue import Queue, Empty, Full
from threading import Lock
from cStringIO import StringIO
from log import logger, make_file_log

make_file_log()

class ImgThumb:
    TIMEOUT = 60 
    SIZE = (140, 205)

    def __init__(self):
        pass

    def thumb(self, url):
        content = utils.http_get(url, timeout = self.TIMEOUT)
        if not content: return None
        try:
            img = Image.open(StringIO(content))
            img.thumbnail(self.SIZE)
            thumb_data = StringIO()
            img.save(thumb_data, 'JPEG')
            thumb_data.seek(0)
            return thumb_data.getvalue()
        except IOError, e:
            print('PIL error: ' + str(e))  	
            return None
        return None

class ThumbWorker(threading.Thread):
    def __init__(self, owner):
        threading.Thread.__init__(self)
        self.daemon = True
        self.thumber = ImgThumb()
        self.owner = owner
        self.is_stop = False
        self.succ = 0
        self.fail = 0

    def run(self):
        print('worker %s starts' % self.name)
        while not self.is_stop:
            self._process()
            self._print_stats()
        logger.info('worker %s exit', self.name)

    def stop(self):
        self.is_stop = True

    def _process(self):
        try:
            self._do_process()
        except Exception, e:
            logger.error('fatal worker error: %s', e)
            raise e

    def _do_process(self):
        task = self.owner._get_task()
        if not task: 
            time.sleep(1)
            return False
        try:
            self._process_one(task)
            logger.debug('process done %s', task['url'])
        except Exception, e:
            logger.warn('process error: %d:%s' % (task['id'], task['url'].encode('utf-8')))
            logger.warn('exception: %s', e)
            self.fail +=1
            self.owner.loader.on_done(task, None)
        return True

    def _process_one(self, task):
        logger.debug('to thumb %s', task['url'])
        data = self.thumber.thumb(task['url'])
        self.owner.loader.on_done(task, data)
        if data:
            self.succ += 1 
        else:
            self.fail += 1

    def _print_stats(self):
        if (self.succ + self.fail) % 500 == 0:
            logger.info('worker: %s (succ/fail) (%d/%d)' % (self.name, self.succ, self.fail))

class Thumber(threading.Thread):
    def __init__(self, loader, worker_cnt = 2):
        threading.Thread.__init__(self)
        self.daemon = True
        self.loader = loader
        self.workers = [ThumbWorker(self) for x in xrange(0, worker_cnt)]
        self.queue = Queue(worker_cnt * 2)
        self.is_stop = False

    def start(self):
        self._load()
        [w.start() for w in self.workers]
        threading.Thread.start(self)

    def run(self):
        print('thumber starts')
        def get_alive():
            return reduce(lambda c, w: c + (1 if w.is_alive() else 0), self.workers, 0)
        while not self.is_stop:
            print('%d alive workers' % get_alive())
            if not self._load():
                time.sleep(5)
            else:
                time.sleep(1)
        print('thumber exit')

    def _load(self):
        tasks = self.loader.load_tasks(len(self.workers))
        if not tasks: 
            print('load empty task from db')
            return False
        print('load %d task from db' % len(tasks))
        try:
            for task in tasks: self.queue.put(task, True, 1)
            return True
        except Full, e:
            print('got full exception')
        return False
        
    def stop(self):
        self.is_stop = True
        [w.stop() for w in self.workers]
        [w.join(5) for w in self.workers]

    def _get_task(self):
        if self.is_stop: return None
        try:
            return self.queue.get(True, 1)
        except Empty:
            print('got empty task')
        return None

if __name__ == '__main__':
    pass
