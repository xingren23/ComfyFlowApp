import asyncio
from contextlib import closing

import aiohttp
import tqdm

async def download(session, url, progress_queue):
    async with session.get(url) as response:
        target = url.rpartition('/')[-1]
        size = int(response.headers.get('content-length', 0)) or None
        position = await progress_queue.get()

        progressbar = tqdm.tqdm(
            desc=target, total=size, position=position, leave=False,
        )

        with open(target, mode='wb') as f, progressbar:
            async for chunk in response.content.iter_chunked(512):
                f.write(chunk)
                progressbar.update(len(chunk))

        await progress_queue.put(position)

        return target

async def main(loop):
    with open('urls.txt') as f:
        urls = [url.strip() for url in f]

    progress_queue = asyncio.Queue(loop=loop)
    for pos in range(5):
        progress_queue.put_nowait(pos)

    async with aiohttp.ClientSession(loop=loop) as session:

        tasks = [download(session, url, progress_queue) for url in urls]
        return await asyncio.gather(*tasks)

with closing(asyncio.get_event_loop()) as loop:
    for tgt in loop.run_until_complete(main(loop)):
        print(tgt)