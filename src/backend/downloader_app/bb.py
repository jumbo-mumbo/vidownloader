import time
import threading
import asyncio


async def slow_shit(arg, info):
    await asyncio.sleep(5)
    info['file_data'] = arg

async def seconds_passes(info):
    secs = 0
    while not info['file_data']:
        print(secs)
        await asyncio.sleep(1)
        secs += 1
    
  
async def monitor_downloading():
    info = {"file_data": None}

    task = asyncio.create_task(slow_shit("shit", info))
    cntr = asyncio.create_task(seconds_passes(info))

    await task
    await cntr
    
    return info
    
async def main():
    file = await monitor_downloading()
    print(file)


if __name__ == "__main__":
    asyncio.run(main())