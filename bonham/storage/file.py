"""
file.py
Tim "tjtimer" Jedro
01.10.2018
"""
from pathlib import Path
from typing import AsyncGenerator
import aiofiles as af


async def write(path: [str, Path], mode: str=None, content: [str, bytes, AsyncGenerator]=None):
    async with af.open(path, f"w{mode or ''}") as f:
        if isinstance(content, AsyncGenerator):
            async for chunk in content:
                await f.write(chunk)
        else:
            await f.write(content)