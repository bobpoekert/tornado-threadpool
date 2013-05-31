Tornado Thread-Pool
===================

Tornado Thread-Pool is a library for [Tornado](http://www.tornadoweb.org/) that lets you make sure that your blocking code and your non-blocking code don't interfere with each other.

You don't have to remember to call `IOLoop.add_callback` at the appropriate time, or worry about whether that database query will block other web requests.

Just decorate your methods with `@in_thread_pool` (for blocking methods) or `@in_ioloop` (for non-blocking methods) and let the library worry about running the method in the right place.

Usage
-----

```python
    from thread_pool import in_thread_pool, in_ioloop, blocking
    
    @blocking
    def get_thing_from_database():
        # If this method is not called from the thread pool,
        # it will result in a warning.
        return db.get('thing')

    @in_thread_pool
    def blocking_method(callback):
        # Call some blocking api, like a database driver.
        # When called, it will always return immediately,
        # and do its work at some future time in a thread pool.
        callback(get_thing_from_database())

    @in_ioloop
    def non_blocking_method(callback, data):
        # Call some non-blocking api, like AsyncHTTPClient.
        # Guarunteed to run in a tornado IOLoop.

```

Dependencies
------------

* Python (in theory any version >= 2.3, but I only tested it on 2.7)
* Tornado (only tested on version 2.2, but should work on earlier versions)

Running Tests
-------------

python -m tornado.testing tests
