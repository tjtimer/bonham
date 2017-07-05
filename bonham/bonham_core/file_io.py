import aiofiles


async def read_file(file_path):
    print('read file called')
    async with aiofiles.open(file_path, 'rb') as in_file:
        return await in_file.read()

async def write_file(file_path, write_mode, data):
    async with aiofiles.open(file_path, write_mode) as out_file:
        async for line in data:
            yield out_file.write(line)
