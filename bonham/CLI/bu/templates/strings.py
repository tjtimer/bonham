"""
    Author: Tim "tjtimer "Jedro
"""

async def init_string(config):
    yield f"# {config['app_dir']} / {config['app_name']}"
    yield ""
    yield "__all__ = []"

