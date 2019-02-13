pyee2
==========================================================
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

pyee2 is the [primus/eventemitter3](https://github.com/primus/eventemitter3) EventEmitter implementation ported to python based on [jfhbrook/pyee](https://github.com/jfhbrook/pyee).

pyee2:
 - Does not raise or emit an error event when your listener raises an error and no one is listening for the "error" event.
   That is to say pyee2 catches all errors raised by event listeners and only emits an error if there are listeners for the "error" event.
 - Does not not emit an event when a new listener is added or removed.
 - Only supports function or functions that return awaitables (coroutine, future, task) as event listeners.
   The test for awaitableness is done via "inspect.isawaitable"

```python3
from pyee2 import EventEmitter

ee = EventEmitter()

@ee.on("event")
def handler(arg, data=3):
    print(f"handler called arg={arg} data={data}")

ee.emit("event", 1, data=2)
```

    

