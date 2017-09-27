import datetime
import json

import arrow
from curio import run

from bonham import Serializer


def test_dict_plain():
    print("\n\nTest dict-plain\n\n")

    async def _test_plain_dict():
        obj = {
            'email':        'tjtimer@gmail.com',
            'password':     'adsoamsd',
            'created':      arrow.get(datetime.datetime.now()).replace(hours=-10),
            'last_updated': datetime.datetime.now()
            }
        new = await Serializer.serialize('Account', obj)
        print(new)
        plain = new['account'][0]
        assert len(new['keys']) is 1
        assert isinstance(new['account'], (list,))
        assert 'password' not in plain.keys()
        assert 'lastUpdated' in plain.keys()
        assert all([isinstance(plain[key], (str, int, float, bool)) for key in plain.keys()])

    run(_test_plain_dict)


def test_list_plain():
    print("\n\nTest list-plain\n\n")

    async def _test_list_plain():
        obj = ['test', 'string',
               int, type, 12 * 5, datetime.datetime.now(), ]
        new = await Serializer.serialize('list-plain', obj)
        print(f"\n\nlist-plain: {new}\n\n")
        assert isinstance(new, (dict,))
        assert isinstance(new['listPlain'], (list,))
        assert new['listPlain'][0][0] == 'test'
        assert isinstance(new['listPlain'][0][3], (str,))
        x = json.dumps(new)
        y = json.loads(x)
        assert y == new

    run(_test_list_plain)


def test_dict_nested():
    print("\n\nTest dict-nested\n\n")

    async def _test_dict_nested():
        obj = {
            'test':       'string',
            'password':   'adsoamsd',
            'date':       datetime.datetime.now(),
            'camel_case': 'something',
            'nested_1':   {
                'test':       'nested_str',
                'password':   'nested_pw',
                'date': arrow.now(),
                'camel_case': 'nested_cc',
                },

            'nested_2':   {
                'test':           'nested2_str',
                'password':       'nested2_pw',
                'date': arrow.utcnow(),
                'camel_case':     'nested2_cc',
                'list':           [1, 2, 3, 'one', 'two', {
                    'key':        3,
                    'password':   'ladidadida',
                    'camel_list': 'dumdidum'
                    }],
                'nested2_nested': {
                    'password': 'blah b',
                    'integer':  1024,
                    'level_3':  {
                        'list':     [1, 2, 3, {
                            'password':      'asdj',
                            'nd_camel_case': 983475
                            }],
                        'password': 'asdihoa!',
                        'monty':    'python'
                        }
                    }
                }
            }
        new = await Serializer.serialize('dict-nested', obj)
        print()
        print('dict-nested', new['keys'])
        print()
        assert all([key in new['keys'] for key in ['dictNested', 'nested1', 'nested2', 'nested2Nested']])
        x = json.dumps(new)
        y = json.loads(x)
        assert y == new
        for key in new['keys']:
            print()
            print(key, new[key])
            print()
            assert isinstance(new[key], (list,))
            for item in new[key]:
                if isinstance(item, (dict,)):
                    assert 'password' not in item.keys()
                    assert all([isinstance(value, (str, int, float, bool)) for value in item.values()])

    run(_test_dict_nested)


def test_list_nested():
    print("\n\nTest list-nested\n\n")

    async def _test_list_nested():
        obj = (item for item in [1, 2, 3, {
            'password':      'asdj',
            'nd_camel_case': 983475,
            'nested_1':      {
                'password':  'asdlha',
                'something': 1234534
                }
            }])
        #  keys: 3, nested1, testList
        new = await Serializer.serialize('list-nested', obj)
        print()
        print('list-nested', new)
        print()
        assert all([key in new['keys'] for key in ['listNested', 'nested1']])
        x = json.dumps(new)
        y = json.loads(x)
        assert y == new

    run(_test_list_nested)
