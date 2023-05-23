import asyncio

async def long_running_task():
    progress = 0
    while progress < 100:
        # do some work
        await asyncio.sleep(1)
        progress += 10
        yield f"Task progress: {progress}%"
    yield "Task completed"

class Communication:
    async def execute_task(self):
        try:
            # execute long running task asynchronously with a timeout of 30 seconds
            result = ""
            async for progress_update in long_running_task():
                result += progress_update + "\n"
            # handle successful completion of the task
            return result
        except asyncio.TimeoutError:
            # handle timeout
            return "Task timed out"