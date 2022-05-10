import aiohttp
import asyncio
import logging

from asyncio.tasks import Task
from asyncio.queues import Queue, QueueEmpty
from typing import List

from starlette.status import HTTP_200_OK

from requestko.utils import is_content_type_application_json

logger = logging.getLogger("requestko.requestor")


class Requestor:

    def __init__(self):
        self._session = aiohttp.ClientSession(base_url="https://exponea-engineering-assignment.appspot.com")
        self._path = "/api/work"

    async def request_work(self) -> dict:
        tasks: List[Task] = []
        working_queue = Queue()

        tasks.append(asyncio.create_task(self._request_endpoint(working_queue), name="Initial request"))

        await asyncio.sleep(0.3)  # Per specification wait 300ms

        try:
            return working_queue.get_nowait()
        except QueueEmpty as e:
            logger.debug("Initial request not fast enough, spawning two other tasks")
        finally:
            tasks.append(asyncio.create_task(self._request_endpoint(working_queue), name="Second request"))
            tasks.append(asyncio.create_task(self._request_endpoint(working_queue), name="Third request"))

        response = None
        while True:
            try:
                if response := working_queue.get_nowait():
                    logger.debug(f"Found successful response: {response}")
                    break
            except QueueEmpty as e:
                continue

        task_to_cancel: Task
        for task_to_cancel in tasks:
            if not task_to_cancel.done():
                task_to_cancel.cancel(msg=f"Already have a response. Canceling task: {task_to_cancel.get_name()}")

        return response

    async def _request_endpoint(self, queue: Queue) -> None:
        timeout = aiohttp.ClientTimeout(total=0.6)  # Assume something wrong as we have response times

        try:
            async with self._session.get(self._path, allow_redirects=False, timeout=timeout) as response:
                if response.status != HTTP_200_OK:
                    logger.debug(f"Request failed, status code: {response.status}")
                    return

                if not is_content_type_application_json(response=response):
                    logger.debug(f"Request failed, status code: {response.status}")
                    return

                queue.put_nowait(await response.json())
        except asyncio.TimeoutError as e:
            logger.debug("The request reached timeout ...")
        finally:
            #await self._session.close()
            logger.debug("Closed the session")
