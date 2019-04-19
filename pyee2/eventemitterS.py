from asyncio import AbstractEventLoop, Future, ensure_future, get_event_loop
from collections import OrderedDict
from functools import partial
from inspect import isawaitable
from typing import Any, Awaitable, Callable, Dict, List, Optional

__all__ = ["EventEmitterS"]


class EventEmitterS:
    """Exactly the same class as EventEmitter except it is slotted"""

    __slots__ = ["_loop", "__events"]

    def __init__(self, loop: Optional[AbstractEventLoop] = None) -> None:
        """Initialize a new EventEmitterS.

        :param loop: Optional loop argument. Defaults to asyncio.get_event_loop()
        :type loop: AbstractEventLoop
        """
        self._loop: AbstractEventLoop = loop if loop is not None else get_event_loop()
        self.__events: Dict[str, Dict[Callable[..., Any], Callable[..., Any]]] = {}

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """Emit an event, passing any args and kwargs to the registered listeners.

        If the registered listener for an event returns an awaitable, the awaitable is scheduled
        using asyncio.ensure_future

        :param event: The event to call listens for
        :param args: Arguments to pass to the listeners for the event
        :param kwargs: Keyword arguments to pass to the listeners for the event
        """
        listeners = self.__events.get(event)
        if listeners is None:
            return False
        listening_for_exceptions = "error" in self.__events
        handle_awaitable = self.__handle_awaitable if listening_for_exceptions else self.__ne_handle_awaitable
        emit_error = self.emit
        for listener in list(listeners.values()):
            try:
                result = listener(*args, **kwargs)
                if isawaitable(result):
                    handle_awaitable(result)
            except Exception as e:
                if listening_for_exceptions:
                    emit_error("error", e)
        return True

    def raising_emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        """Emit an event, passing any args and kwargs to the registered listeners.

        If the registered listener for an event returns an awaitable, the awaitable is scheduled
        using asyncio.ensure_future

        Unlike emit, this method makes no attempt to catch exceptions raised by a listener and always
        adds done callback to the future returned by ensure_future, if the result was awaitable, that will
        emit the error event if the future raised an exception.

        :param event: The event to call listens for
        :param args: Arguments to pass to the listeners for the event
        :param kwargs: Keyword arguments to pass to the listeners for the event
        """
        listeners = self.__events.get(event)
        if listeners is None:
            return False
        handle_awaitable = self.__handle_awaitable
        for listener in list(listeners.values()):
            result = listener(*args, **kwargs)
            if isawaitable(result):
                handle_awaitable(result)
        return True

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
            return partial(self.on, event)
        self.__add_listener(event, listener, listener)
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

        if listener is None:
            return partial(self.once, event)

        def once_wrapper(*args: Any, **kwargs: Any) -> Any:
            self.remove_listener(event, listener)
            return listener(*args, **kwargs)

        self.__add_listener(event, listener, once_wrapper)
        return listener

    def remove_listener(self, event: str, listener: Callable[..., Any]) -> None:
        """Remove a listener registered for a event

        :param event: The event that has the supplied `listener` register
        :param listener: The registered listener to be removed
        """
        ldict = self.__events.get(event, None)
        if ldict is not None:
            ldict.pop(listener, None)
            if len(ldict) == 0:
                del self.__events[event]

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        """Removes all listeners registered to an event.

        If event is none removes all registered listeners.

        :param event: Optional event to remove listeners for
        """
        if event is not None:
            self.__events.pop(event, None)
            return
        self.__events.clear()

    def listeners(self, event: str) -> List[Callable[..., Any]]:
        """Retrieve the list of listeners registered for a event

        :param event: The event to retrieve its listeners for
        :return: List of listeners registered for the event
        """
        ldict = self.__events.get(event, None)
        if ldict is not None:
            return [listener for listener in ldict.keys()]
        return []

    def event_names(self) -> List[str]:
        """Retrieve a list of event names that are registered to this EventEmitter

        :return: The list of registered event names
        """
        return [ename for ename in self.__events.keys()]

    def listener_count(self, event: str) -> int:
        """Returns the number of listeners for an event.

        :param event: The event name
        :return: The number of listeners for the event
        """
        listeners = self.__events.get(event, None)
        if listeners is None:
            return 0
        return len(listeners)

    def has_listeners(self, event_name: str) -> bool:
        """Returns T/F indicating if the supplied event has listeners registered

        :param event_name: The event to check if it has registered listeners
        :return: T/F indicating if the event has listeners registered
        """
        return event_name in self.__events

    def __add_listener(
        self,
        event: str,
        original_listener: Callable[..., Any],
        maybe_wrapped_listener: Callable[..., Any],
    ) -> None:
        """Utility method for registering an listener for an event

        :param event: The event the listener will be registered for
        :param original_listener: The listener to be registered
        :param maybe_wrapped_listener: The original or wrapped listener
        """
        ldict = self.__events.get(event, None)
        if ldict is None:
            ldict = OrderedDict()
            self.__events[event] = ldict
        ldict[original_listener] = maybe_wrapped_listener

    def __handle_awaitable(self, awaitable: Awaitable[Any]) -> None:
        """Utility method for handling an awaitable return value of an
        listener when there are error listeners

        :param awaitable: An awaitable returned by a listener
        """
        future = ensure_future(awaitable, loop=self._loop)
        future.add_done_callback(self.__maybe_emit_error)

    def __ne_handle_awaitable(self, awaitable: Awaitable[Any]) -> None:
        """Utility method for handling an awaitable return value of an
        listener when there are no error listeners

        :param awaitable: An awaitable returned by a listener
        """
        ensure_future(awaitable, loop=self._loop)

    def __maybe_emit_error(self, the_future: Future) -> None:
        """Utility method for emitting the exception, if one was raised,
        in the future created from the awaitable returned by an event listener

        :param the_future: The future created from the awaitable returned by an event listener
        """
        raised_exception = the_future.exception()
        if raised_exception:
            self.emit("error", raised_exception)
