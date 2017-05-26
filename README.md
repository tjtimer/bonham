Bonham
---
---
Server part of a single page app i'm working on, based on python aiohttp.

Dedicated to the greatest drummer of all times MR. JOHN BONHAM.

**!!! This is pure work in progress. Some things seem to work others don't. !!!** 

Feel free to review, criticize or use it in any way you like.

***requires Python 3.6***

---
#####table of content:  
- [Coding Style](#coding-style)
---

#### <a name="coding-style" />Coding Style
- max line length should be 100, 80 is better (pep8).
- functions:
   - keep the number of positional arguments as low as possible
   - use keyword arguments
    ```python
    def function(*, argument=None):
         if argument is None:
              argument = default_value
         ...
    ```
    or
    ```python
    def function(*, **kwargs):
         argument = kwargs.pop('argument_key', default_value)
         ...
    ```


