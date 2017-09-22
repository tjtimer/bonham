# Bonham

Server/service framework part of a single page app i'm working on, based on python aiohttp.

Dedicated to the greatest drummer of all times MR. JOHN BONHAM.

**!!! This is pure work in progress. Some things seem to work others don't. !!!** 

Feel free to review, criticize or use it in any way you like.

***requires Python >=3.6***

---

##### table of content:
- [Desired Architecture](#architecture)
- [Usage](#usage)
---
#### Desired Architecture
<a name="architecture" />

Manger:
- one instance only
- spawns and monitors multiple processes (e.g. services and background tasks)
- handles communication between processes
    
Service:
- one instance per process
- can have multiple components ()
---
##### Usage
<a name="usage" />

```python
# <MyProject>/main.py

from bonham import Manager, Service

class MyService(Service):

    def __init__(self, *args, **kwargs):
        super().__init__()
    
    ...
    
    
# if you run it from commandline or monitoring apps like `supervisord` add:
if __name__ == '__main__':
    my_service = MyService()  # service setup
    my_service.run()  #  let the serice do its work.
 
# if you are running your service behind a gunicorn interface add:

my_service = MyService().run()
```
---

