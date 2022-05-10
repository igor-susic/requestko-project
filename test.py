import asyncio
import time
import queue
import random
import logging

logging.basicConfig(level=logging.DEBUG)

#q = asyncio.Queue()


async def do_some_work():
    print("Make request")
    t = random.randint(1,20)
    print(f"Will wait {t} seconds")
    await asyncio.sleep(t)
    #q.put_nowait(t)
    print("Request done")
    return 5


async def main():
    print("Before")
    task1 = asyncio.create_task(do_some_work(), name="First")
    start = time.time()
    await asyncio.sleep(1)

    if task1.done():
        return task1.result()

    # try:
    #     if el := q.get_nowait():
    #         print(f"Element to return is {el}")
    #         return el
    # except asyncio.queues.QueueEmpty as e:
    #     print(f"before new tasks {time.time() - start}")
    # finally:
    task2 = asyncio.create_task(do_some_work(), name="Second")
    task3 = asyncio.create_task(do_some_work(), name="Third")

    done, pending = await asyncio.wait([task1, task2, task3], return_when=asyncio.FIRST_COMPLETED)

    finished: asyncio.Task = next(iter(done))

    import pdb; pdb.set_trace()

    print("little veofre loop")
    # while True:
    #     try:
    #         el = await q.get()
    #         print(f"Element to return is {el}")
    #         return el
    #     except queue.Empty as e:
    #         print("Pass")
    #         pass
    # fu = asyncio.Future()
    #
    # asyncio.create_task(do_some_work(fu), name="First task")
    # asyncio.create_task(some_stupid(), name="Second task")
    #
    # fu.done()
    #
    # #await task1
    # print("WHen will this run")
    # #await task2
    # print("Or this")
    #
    # start = time.time()
    # while not fu.done():
    #     #print(time.time() - start)
    #     if time.time() - start > 0.3:
    #         task = asyncio.create_task(do_some_work(fu), name="LOop task")
    #         await asyncio.gather(*[task, task])
    #         break



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.set_debug(enabled=True)
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())