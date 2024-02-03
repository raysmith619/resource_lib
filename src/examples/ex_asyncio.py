#ex_asyncio.py 31Jan2024  crs, From python.org/e/library
import asyncio

async def main():
    print('Hello ...')
    await asyncio.sleep(1)
    print('... World!')

asyncio.run(main())