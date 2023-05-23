import asyncio

class Communication:
    async def execute_task(self):
        try:
            # execute long running task asynchronously with a timeout of 30 seconds
            result = await asyncio.wait_for(long_running_task(), timeout=30)
            # handle successful completion of the task
            return result
        except asyncio.TimeoutError:
            # handle timeout
            return "Task timed out"