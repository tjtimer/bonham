from collections import Iterator
import datetime
import json

import arrow
import curio

from bonham.constants import PrivacyStatus


async def camel_case(value):
    v_list = value.replace('-', '_').split('_')
    if len(v_list) == 1:
        return value.lower()
    cc_value = v_list[0].lower()
    cc_value += ''.join(part.capitalize() for part in v_list[1:])
    return cc_value


async def to_json(key: str, value):
    """
    transform a plain dict (no nested objects) to a json serializable dict
    """
    if key == 'privacy':
        value = PrivacyStatus(value).label
    if isinstance(value, (datetime.datetime, arrow.arrow.Arrow)):
        return arrow.get(value).for_json()
    if isinstance(value, (type,)):
        return value.__name__
    return value


async def serialize(name: str, obj: object) -> json:
    """
    creates a new json serializable dict object from data object
    where keys are "camelCase" for ECMAScript conventions
    
    
    
    :return: json serializable dictionary
    """
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
