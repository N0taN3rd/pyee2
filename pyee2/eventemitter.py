# -*- coding: utf-8 -
import asyncio
from asyncio import AbstractEventLoop
from collections import defaultdict, OrderedDict
from typing import Dict, Callable, DefaultDict, Any, Optional, List

__all__ = ["EventEmitter"]


class EventEmitter(object):
    """EventEmitter implementation like primus/eventemitter3 (Nodejs).

    We do not raise or emit an error event when your listener raises an error.
    Only supports regular or asyncio coroutine event listeners.
    """

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
        """Construct a new EventEmitter.

        :param loop: Optional loop argument. Defaults to asyncio.get_event_loop()
        :type loop: AbstractEventLoop
        """
        self._loop: AbstractEventLoop = loop if loop is not None else asyncio.get_event_loop()
        self._events: DefaultDict[
            str, Dict[Callable[..., Any], Callable[..., Any]]
        ] = defaultdict(OrderedDict)

    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Emit an event, passing any args and kwargs to the registered listeners.

        If the registered listener for an event is a coroutine, the coroutine is scheduled using asyncio.ensure_future

        :param event: The event to call listens for
        :param args: Arguments to pass to the listeners for the event
        :param kwargs: Keyword arguments to pass to the listeners for the event
        """
        for f in list(self._events[event].values()):
            try:
                result = f(*args, **kwargs)
            except Exception:
                continue

            if asyncio.iscoroutine(result):
                asyncio.ensure_future(result, loop=self._loop)

    def on(
        self, event: str, listener: Optional[Callable[..., Any]] = None
    ) -> Callable[..., Any]:
        """Register a listener for an event.

        Can be used as a decorator for pythonic EventEmitter usage.

        :param event: The event to register the listener for
        :param listener: The listener to be called when the event it is registered for is emitted
        :return: The listener or listener wrapper when used as a decorator
        """
        if listener is None:

            def _on(f: Callable[..., Any]) -> Callable[..., Any]:
                self._events[event][f] = f
                return f

            return _on
        self._events[event][listener] = listener
        return listener

    def once(
        self, event: str, listener: Optional[Callable[..., Any]] = None
    ) -> Callable[..., Any]:
        """Register a one time listener for an event.

        Can be used as a decorator for pythonic EventEmitter usage.

        :param event: The event to register the listener for
        :param listener: The listener to be called when the event it is registered for is emitted
        :return: The listener or listener wrapper when used as a decorator
        """

        def _wrapper(f: Callable[..., Any]) -> Callable[..., Any]:
            def g(*args: Any, **kwargs: Any) -> Any:
                self.remove_listener(event, f)
                return f(*args, **kwargs)

            self._events[event][f] = g
            return f

        if listener is None:
            return _wrapper
        else:
            return _wrapper(listener)

    def remove_listener(self, event: str, listener: Callable[..., Any]) -> None:
        """Remove a listener registered for a event

        :param event: The event that has the supplied `listener` register
        :param listener: The registered listener to be removed
        """
        self._events[event].pop(listener)

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        """Removes all listeners registered to an event.

        If event is none removes all registered listeners.

        :param event: Optional event to remove listeners for
        """
        if event is not None:
            self._events[event] = OrderedDict()
        else:
            self._events = defaultdict(OrderedDict)

    def listeners(self, event: str) -> List[Callable[..., Any]]:
        """Retrieve the list of listeners registered for a event

        :param event: The event to retrieve its listeners for
        :return: List of listeners registered for the event
        """
        return list(self._events[event].keys())

    def event_names(self) -> List[str]:
        """Retrieve a list of event names that are registered to this EventEmitter

        :return: The list of registered event names
        """
        return list(self._events.keys())
