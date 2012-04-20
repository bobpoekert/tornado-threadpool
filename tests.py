import thread_pool
from tornado.testing import AsyncTestCase
from unittest import TestCase
import time, socket
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from functools import partial

class ThreadPoolTestCase(AsyncTestCase):

    def tearDown(self):
        thread_pool.thread_pool = thread_pool.ThreadPool()

    def test_run(self):

        def callback():
            self.stop()

        thread_pool.thread_pool.run(callback)
        self.wait(timeout=0.2)

    @thread_pool.in_thread_pool
    def sleep(self):
        time.sleep(0.1)
        self.stop()

    def test_in_thread_pool(self):
        start = time.time()
        self.sleep()
        self.assertLess(time.time(), start + 0.1)
        self.wait()
        self.assertGreater(time.time(), start + 0.1)

    def test_in_ioloop(self):
        self.done = False
        self._test_in_ioloop()
        IOLoop.instance().start()
        self.assertTrue(self.done)

    @thread_pool.in_thread_pool
    def _test_in_ioloop(self):
        time.sleep(0.1)
        self._test_in_ioloop_2()

    @thread_pool.in_ioloop
    def _test_in_ioloop_2(self):
        self.done = True
        IOLoop.instance().stop()

    def test_blocking_warn(self):
        self._fired_warning = False
        thread_pool.blocking_warning = self.warning_fired
        self.blocking_method()
        self.assertTrue(self._fired_warning)

    @thread_pool.blocking
    def blocking_method(self):
        time.sleep(0.1)

    def warning_fired(self, fn):
        self._fired_warning = True

class TheadPoolDoSTestCase(TestCase):

    def tearDown(self):
        thread_pool.thread_pool = thread_pool.ThreadPool()

    def setUp(self):
        self.entered = 0
        self.exited = 0

    def exit(self):
        time.sleep(0.01)
        self.exited += 1

    def test_DoS(self):

        for i in xrange(100):
            self.entered += 1
            thread_pool.thread_pool.run(self.exit)

        time.sleep(0.5)
        self.assertEqual(self.entered, self.exited)
        time.sleep(1)
        self.assertEqual(len(thread_pool.thread_pool.threads), 0)
