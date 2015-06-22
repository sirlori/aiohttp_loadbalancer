from loadb import BalanceApplication
import asyncio
from aiohttp import web
import sys
import time

done_requests = 0
request_seconds = 0
seconds = 0


@asyncio.coroutine
def stupid_handler(request):
    global request_seconds
    global seconds
    global done_requests
    start = time.time()
    done_requests += 1
    if seconds >= 1 / 10000:
        print(request_seconds)
        request_seconds = 0
        seconds = 0
    request_seconds += 1
    seconds += time.time() - start
    return web.Response(body=b'CIAO')


@asyncio.coroutine
def init(loop, argv):
    port = int(argv[1])
    app = BalanceApplication(loop=loop)
    app.add_route('*', r'/{name:[^{}/]*}', stupid_handler)
    server = yield from loop.create_server(app.make_handler(),
                                           '127.0.0.1', port)
    print('partito su porta ' + argv[1])
    return server

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, sys.argv))
    try:
        loop.run_forever()
    except:
        total = float(sys.argv[2])
        print('\nRichieste Effettuate: {requests}, {percentage}'.
              format(requests=done_requests,
                     percentage=(done_requests / total)))
