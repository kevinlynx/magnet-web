# kevinlynx@gmail.com
import functools
import time

def create(**args):
    return MemKVCache(**args)

def with_cache(k):
    def deco(func):
        def wrapper(cls, *args, **kws):
            v = cls.cache.get(k)
            if v: return v
            v = func(cls, *args, **kws)
            if v: cls.cache.put(k, v)
            return v
        return wrapper
    return deco

def use_cache(func):
    def wrapper(cls, *args, **kws):
        k = cls.format_key(*args, **kws)
        v = cls.cache.get(k)
        if v: return v
        v = func(cls, *args, **kws)
        if v: cls.cache.put(k, v)
        return v
    return wrapper

class MemKVCache:
    def __init__(self, alive_time):
        self.alive_time = alive_time
        self.kvs = {}

    def put(self, k, v):
        print('put cache for ' + k)
        self.kvs[k] = dict(elapsed = self.alive_time + time.time(),
                value = v)

    def get(self, k):
        if not self.kvs.has_key(k): return None
        pack_v = self.kvs[k]
        if pack_v['elapsed'] < time.time(): 
            del self.kvs[k]
            return None
        print('get cache for ' + k)
        return pack_v['value']

