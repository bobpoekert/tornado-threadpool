import threading, Queue, traceback, warnings
from tornado.ioloop import IOLoop
from functools import wraps, partial

thread_locals = threading.local()

class ThreadPool(object):

    def __init__(self, max_qsize=10, timeout=1):
        self.threads = set([])
        self.lock = threading.RLock()
        self.queue = Queue.Queue()
        self.timeout = timeout
        self.max_qsize = max_qsize

    def run(self, fn):
        with self.lock:
            self.queue.put(fn)
            if len(self.threads) == 0 or self.queue.qsize() > self.max_qsize:
                self.spawn_thread()

    def spawn_thread(self):
        with self.lock:
            thread = None
            def get_thread():
                return thread
            thread = threading.Thread(target=self.work, args=(get_thread,))
            thread.setDaemon(True)
            self.threads.add(thread)
            thread.start()

    def on_error(self):
        traceback.print_exc()

    def work(self, get_thread):
        thread = get_thread()
        del get_thread
        thread_locals.thread_pool = True
        while 1:
            try:
                job = self.queue.get(True, self.timeout)
                try:
                    job()
                except:
                    self.on_error()
            except Queue.Empty:
                break

        self.threads.remove(thread)

thread_pool = ThreadPool()

def get_ioloop():
    "Monkeypatch me to use a custom ioloop for @in_ioloop"
    return IOLoop.instance()

def flag_ioloop():
    thread_locals.ioloop = True

get_ioloop().add_callback(flag_ioloop)

def in_ioloop(fn):

    @wraps(fn)
    def res(*args, **kwargs):
        try:
            if thread_locals.ioloop:
                fn(*args, **kwargs)
                return
        except AttributeError:
            pass

        get_ioloop().add_callback(partial(fn, *args, **kwargs))

    return res

def in_thread_pool(fn):

    @wraps(fn)
    def res(*args, **kwargs):
        try:
            if thread_locals.thread_pool:
                fn(*args, **kwargs)
                return
        except AttributeError:
            pass

        thread_pool.run(partial(fn, *args, **kwargs))

    return res

def blocking_warning(fn):
    warning_string = 'Blocking call to %s not in thread pool' % fn.__name__
    warnings.warn(warning_string, RuntimeWarning)
    traceback.print_last()

def blocking(fn):


    @wraps(fn)
    def res(*args, **kwargs):
        while 1:
            try:
                if thread_locals.thread_pool:
                    break
            except AttributeError:
                pass
            blocking_warning(fn)
            break
        return fn(*args, **kwargs)

    return res
