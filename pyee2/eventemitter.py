# -*- coding: utf-8 -
import asyncio
from asyncio import AbstractEventLoop
from collections import defaultdict, OrderedDict
from typing import Dict, Callable, DefaultDict, Any, Optional, List

import attr

__all__ = ["EventEmitter"]


@attr.dataclass
class EventEmitter(object):
    _events: DefaultDict[str, Dict[Callable[..., Any], Callable[..., Any]]] = attr.ib(
        factory=lambda: defaultdict(OrderedDict), init=False
    )
    _loop: AbstractEventLoop = attr.ib(factory=asyncio.get_event_loop, repr=False)

    def on(self, event: str, f: Callable[..., Any]) -> None:
        self._events[event][f] = f

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        for f in list(self._events[event].values()):
            try:
                result = f(*args, **kwargs)
            except Exception:
                continue

            if asyncio.iscoroutine(result):
                if self._loop:
                    asyncio.ensure_future(result, loop=self._loop)
                else:
                    asyncio.ensure_future(result)

    def once(self, event: str, f: Callable[..., Any]) -> None:
        def g(*args, **kwargs):
            self.remove_listener(event, f)
            return f(*args, **kwargs)

        self._events[event][f] = g

    def remove_listener(self, event: str, f: Callable[..., Any]) -> None:
        self._events[event].pop(f)

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        if event is not None:
            self._events[event] = OrderedDict()
        else:
            self._events = defaultdict(OrderedDict)

    def listeners(self, event: str) -> List[Callable[..., Any]]:
        return list(self._events[event].keys())
