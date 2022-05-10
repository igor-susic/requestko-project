import aiohttp
import asyncio
import logging

from asyncio.tasks import Task
from typing import List, Optional

from starlette.status import HTTP_200_OK

from requestko.utils import is_content_type_application_json

logger = logging.getLogger("requestko.requestor")


class Requestor:

    def __init__(self):
        self._session = aiohttp.ClientSession(base_url="https://exponea-engineering-assignment.appspot.com")
        self._path = "/api/work"

    async def close(self) -> None:
        await self._session.close()

    async def request_work(self, timeout: float) -> dict:
        tasks: List[Task] = [asyncio.create_task(self._request_endpoint(timeout), name="Initial request")]

        await asyncio.sleep(0.3)  # Per specification wait 300ms

        if tasks[0].done():
            if result := tasks[0].result() is not None:
                logger.debug("Early success!")
                return result

        logger.debug("Initial request not fast enough, spawning two other tasks")
        tasks.append(asyncio.create_task(self._request_endpoint(timeout), name="Second request"))
        tasks.append(asyncio.create_task(self._request_endpoint(timeout), name="Third request"))

        for f in asyncio.as_completed(tasks):
            logger.debug("Going through tasks")
            result: dict = await f
            logger.debug("One task is here")
            if result is not None:
                task_to_cancel: Task
                for task_to_cancel in tasks:
                    if not task_to_cancel.done():
                        logger.debug(f"Will try to cancel task: {task_to_cancel}")
                        task_to_cancel.cancel(msg=f"Already got response. Canceling task: {task_to_cancel.get_name()}")
                    else:
                        logger.debug(f"Seems task: {task_to_cancel.get_name()} is also done, but it doesn't matter")

                logger.debug(f"This is result {result}")
                return result

        raise Exception

    async def _request_endpoint(self, timeout: float) -> Optional[dict]:
        timeout = aiohttp.ClientTimeout(total=timeout)

        try:
            logger.debug(f"Starting one request")
            async with self._session.get(self._path, allow_redirects=False, timeout=timeout) as response:
                if response.status != HTTP_200_OK:
                    logger.debug(f"Request failed, status code: {response.status}")
                    return None

                if not is_content_type_application_json(response=response):
                    logger.debug(f"Request failed, did not receive right content type")
                    return None

                return await response.json()
        except asyncio.TimeoutError as e:
            logger.debug("The request reached timeout ...")
            return None
