pyee2: A port of node.js's primus/eventemitter3 to python.
==========================================================

pyee2 is based on jfhbrook/pyee but modified to provide primus/eventemitter3 EventEmitter.

.. code-block:: python

    from pyee2 import EventEmitter

    ee = EventEmitter()

    @ee.on("event")
    def handler(arg, data=3):
        print(f"handler called arg={arg} data={data}")

    ee.emit("event", 1, data=2)

