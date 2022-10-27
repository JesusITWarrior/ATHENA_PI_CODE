import asyncio

async def mainProcess():
    print("Starting logging loop...")
    doorTask = asyncio.create_task(doorProcess())
    tempTask = asyncio.create_task(tempProcess())
    await doorTask
    
async def doorProcess():
    while True:
        print("Checking door status")
        await asyncio.sleep(1)
    
    
async def tempProcess():
    while True:
        print("Starting temperature log")
        await asyncio.sleep(5)
    
asyncio.run(mainProcess())