# Bonham

Server part of a single page app i'm working on, based on python aiohttp.

Dedicated to the greatest drummer of all times MR. JOHN BONHAM.

**!!! This is pure work in progress. Some things seem to work others don't. !!!** 

Feel free to review, criticize or use it in any way you like.

***requires Python 3.6***

---

##### table of content:
- [Usage](#usage)
- [Coding Style](#coding-style)
---
#### <a name="usage" />Usage
```python
# <MyProject>/main.py

from bonham import *


def run():
    config = load_yaml_conf('/path/to/my/conf.yaml')




```
#### <a name="coding-style" />Coding Style
- max line length should be 100, better 80 (pep8).
- functions:
   - keep the number of positional arguments as low as possible
   - use keyword arguments
   - use type annotation
   - use docstrings
 ```python
def my_function(*, argument: type=None) -> type:
     if argument is None:
          argument = 'default_value'
          ...
 ```
or
```python
def my_function(**kwargs)-> type:
     argument = kwargs.pop('argument_key', 'default_value')
     ...
```


