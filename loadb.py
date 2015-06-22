import aiohttp
from aiohttp import web
import asyncio
import time
from operator import itemgetter
from functools import wraps

seconds = 0
connections = [
    ('http://localhost:8000', 0),
    ('http://localhost:8001', 0),
    ('http://localhost:8002', 0)
]


class BalanceApplication(web.Application):

    def make_handler(self, **kwargs):
        self._request_factory = super().make_handler(**kwargs)
        return self._request_factory

    def wrap_handler_lb(self, f):

        @wraps(f)
        def wrapper(request):
            content = yield from request.text()
            if 'loadbalancer' == content:
                conns = str(len(self._request_factory.connections))
                return web.Response(body=bytes(conns, encoding='ascii'))
            else:
                return (yield from f(request))
        return wrapper

    def add_route(self, method, path, handler,
                  *, name=None, expect_handler=None):
        real_handler = self.wrap_handler_lb(handler)
        self.router.add_route(method, path, real_handler)


@asyncio.coroutine
def balance(request):
    global seconds
    global connections
    start = time.time()
    if True:
        seconds = 0
        conns = []
        for conn in connections:
            resp = yield from aiohttp.request('POST', conn[0],
                                              data='loadbalancer')
            content = yield from resp.content.read()
            conns.append((conn[0], int(content)))
            resp.close()
        connections = conns
        print(connections)
    connection = sorted(connections, key=itemgetter(1))[0]
    print(connection)
    resp = yield from aiohttp.request(request.method,
                                      connection[0] + request.path,
                                      data=(yield from request.content.read()))
    seconds += time.time() - start
    resp_data = yield from resp.read()
    return web.Response(body=bytes(resp_data))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', r'/{name:[^{}/]*}', balance)
    server = yield from loop.create_server(app.make_handler(),
                                           '127.0.0.1', 9000)
    print('startato!')
    return server

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
