import asyncio
import threading
from asyncio import CancelledError
from typing import Coroutine, Any, Callable


class AsyncThread(threading.Thread):
    def __init__(self, target: Callable[[], Coroutine[Any, Any, Any]]):
        super().__init__()
        self.target = target
        self.loop = None

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        self.loop = asyncio.get_running_loop()
        try:
            await self.target()
        except CancelledError:
            print("Exited async thread")

    def close(self):
        if self.loop:
            for task in asyncio.all_tasks(self.loop):
                task.cancel()