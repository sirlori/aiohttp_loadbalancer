import aiohttp
import sys
import asyncio


@asyncio.coroutine
def main():
    # sending some empty requests to lb
    resp = yield from aiohttp.request('GET', 'http://localhost:9000/')
    print((yield from resp.text()))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # create a future that waits asynchroniously for
    # all other futures
    f = asyncio.wait([main() for i in range(int(sys.argv[1]))])
    loop.run_until_complete(f)
