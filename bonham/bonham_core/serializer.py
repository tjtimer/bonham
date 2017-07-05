import datetime
import json
from collections import Iterator

import arrow
import curio

from .constants import Privacy
from .utils import camel_case

__all__ = ['serialize']


async def to_json(key: str, value):
    if key == 'privacy':
        value = Privacy(value).label
    if isinstance(value, (datetime.datetime, arrow.arrow.Arrow)):
        return arrow.get(value).for_json()
    if isinstance(value, (type,)):
        return value.__name__
    return value


async def serialize(name: str, obj: object) -> json:
    """
    Creates a json object from obj where keys are "camelCased" for ECMAScript conventions
    and all values are lists.
    Every serialized object contains a list of all keys in this json object.
    references to nested data objects are strings starting with an @-Symbol, followed by the key and the index.

    :return: json serializable dictionary
    """
    print("serializer")
    print(name, obj)
    new_obj = dict()
    keys = set()
    q = curio.Queue()
    await q.put((name, obj))
    while True:
        _name, item = await q.get()
        name = await camel_case(_name)
        keys.add(name)
        if name not in new_obj.keys():
            new_obj[name] = []
        if isinstance(item, (dict,)):
            obj = dict()
            for key, value in item.items():
                if key == 'password':
                    continue
                if isinstance(value, (dict, list, set)):
                    await q.put((key, value))
                    key = await camel_case(key)
                    if key in new_obj.keys():
                        obj[key] = f"@{key}--{len(new_obj[key])+1}"
                    else:
                        obj[key] = f"@{key}--0"
                else:
                    obj[await camel_case(key)] = await to_json(key, value)
            new_obj[name].append(obj)
        elif isinstance(item, (list, set, Iterator)):
            n_list = []
            for idx, obj in enumerate(item):
                if isinstance(obj, (dict, list, set)):
                    await q.put((_name, obj))
                    n_list.append(f"@{name}--{len(new_obj[name])+1}")
                else:
                    n_list.append(await to_json(str(idx), obj))
            new_obj[name].append(n_list)
        if q.empty():
            new_obj['keys'] = sorted(list(keys))
            return new_obj
