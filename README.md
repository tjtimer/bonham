***Bonham***

A python aiohttp server.

Server part of a single page app i'm working on.

Dedicated to the greatest drummer of all times MR. JOHN BONHAM.

This is pure work in progress

!!! DO NOT USE ANY OF THIS CODE !!!

But feel free to review and criticize it.

requires Python 3.6

---
#### Coding Style
---
- max line length should be 100, 80 is better (pep8).
- functions:
   - keep the number of positional arguments as low as possible
   - use keyword arguments
    ```python
    def function(*, argument=None):
         if argument is None:
              argument = default_value
    ```
    or
    ```python
    def function(*, **kwargs):
         argument = kwargs.pop('argument_key', default_value)
         ...
    ```


