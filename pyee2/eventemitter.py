import asyncio
from asyncio import AbstractEventLoop, Future, ensure_future as asyncio_ensure_future
from collections import OrderedDict
from inspect import isawaitable as inspect_isawaitable
from typing import Any, Dict, Callable, Optional, List

__all__ = ["EventEmitter"]


class EventEmitter(object):
    """EventEmitter implementation like primus/eventemitter3 (Nodejs).

    We do not raise or emit an error event when your listener raises an error
    and no one is listening for the "error" event; that is to say
    we swallow (catch) all errors raised.
    We also do not emit an event when a new listener is added.
    Only supports regular function or functions that return awaitables
    (coroutine, future, task) event listeners.
    The test for awaitableness is done via "inspect.isawaitable"
    """

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
        """Construct a new EventEmitter.

        :param loop: Optional loop argument. Defaults to asyncio.get_event_loop()
        :type loop: AbstractEventLoop
        """
        self._loop: AbstractEventLoop = loop if loop is not None else asyncio.get_event_loop()
        self._events: Dict[str, Dict[Callable[..., Any], Callable[..., Any]]] = dict()

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """Emit an event, passing any args and kwargs to the registered listeners.

        If the registered listener for an event returns an awaitable, the awaitable is scheduled
        using asyncio.ensure_future

        :param event: The event to call listens for
        :param args: Arguments to pass to the listeners for the event
        :param kwargs: Keyword arguments to pass to the listeners for the event
        """
        listeners = self._events.get(event)
        if listeners is None:
            return False
        listening_for_exceptions = "error" in self._events
        self_loop = self._loop
        self_maybe_emit_error = self._maybe_emit_error
        self_emit = self.emit
        for f in list(listeners.values()):
            try:
                result = f(*args, **kwargs)
                if inspect_isawaitable(result):
                    future = asyncio_ensure_future(result, loop=self_loop)
                    if listening_for_exceptions:
                        future.add_done_callback(self_maybe_emit_error)
            except Exception as e:
                if listening_for_exceptions:
                    self_emit("error", e)
        return True

    def _maybe_emit_error(self, the_future: Future) -> None:
        raised_exception = the_future.exception()
        if raised_exception:
            self.emit("error", raised_exception)

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
                self._add_listener(event, f, f)
                return f

            return _on
        self._add_listener(event, listener, listener)
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
            def wrapped_once_listener(*args: Any, **kwargs: Any) -> Any:
                self.remove_listener(event, f)
                return f(*args, **kwargs)

            self._add_listener(event, f, wrapped_once_listener)
            return f

        if listener is None:
            return _wrapper
        else:
            return _wrapper(listener)

    def _add_listener(
        self,
        event: str,
        original_listener: Callable[..., Any],
        maybe_wrapped_listener: Callable[..., Any],
    ) -> None:
        ldict = self._events.get(event, None)
        if ldict is None:
            self._events[event] = ldict = OrderedDict()
        ldict[original_listener] = maybe_wrapped_listener

    def remove_listener(self, event: str, listener: Callable[..., Any]) -> None:
        """Remove a listener registered for a event

        :param event: The event that has the supplied `listener` register
        :param listener: The registered listener to be removed
        """
        ldict = self._events.get(event, None)
        if ldict is not None:
            ldict.pop(listener, None)
            if len(ldict) == 0:
                del self._events[event]

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        """Removes all listeners registered to an event.

        If event is none removes all registered listeners.

        :param event: Optional event to remove listeners for
        """
        if event is not None:
            self._events.pop(event, None)
        else:
            self._events.clear()

    def listeners(self, event: str) -> List[Callable[..., Any]]:
        """Retrieve the list of listeners registered for a event

        :param event: The event to retrieve its listeners for
        :return: List of listeners registered for the event
        """
        ldict = self._events.get(event, None)
        if ldict is not None:
            return list(ldict.keys())
        return list()

    def event_names(self) -> List[str]:
        """Retrieve a list of event names that are registered to this EventEmitter

        :return: The list of registered event names
        """
        return list(self._events.keys())

    def listener_count(self, event: str) -> int:
        """Returns the number of listeners for an event.

        :param event: The event name
        :return: The number of listeners for the event
        """
        listeners = self._events.get(event, None)
        if listeners is None:
            return 0
        return len(listeners)
