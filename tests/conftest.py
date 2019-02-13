from asyncio import AbstractEventLoop, Future, gather
from typing import Any, Callable, Optional

import pytest
from mock import Mock

from pyee2 import EventEmitter


@pytest.fixture
def ee() -> EventEmitter:
    return EventEmitter()


@pytest.fixture
def mock() -> Mock:
    return Mock()


@pytest.fixture
def ee_with_event_loop(event_loop: AbstractEventLoop) -> EventEmitter:
    return EventEmitter(loop=event_loop)


@pytest.fixture
def deferred(event_loop: AbstractEventLoop) -> Future:
    return event_loop.create_future()


@pytest.fixture
def arg_swallower() -> Callable[..., None]:
    def swallower(*args, **kwargs) -> None:
        return None

    return swallower


class EEExceptionHelper(object):
    def __init__(self) -> None:
        self.exception: Exception = Exception("An exception was raised")
        self.emitted_exception: Optional[Exception] = None
        self._deferred_raised_exception: Optional[Future] = None
        self._deferred_error_received: Optional[Future] = None

    def with_deferred(self, loop: AbstractEventLoop) -> None:
        self._deferred_raised_exception = loop.create_future()
        self._deferred_error_received = loop.create_future()

    def error_listener(self, emitted_exception: Exception) -> None:
        self.emitted_exception = emitted_exception

    async def error_listener_async(self, emitted_exception: Exception) -> None:
        self.emitted_exception = emitted_exception
        if self._deferred_error_received:
            self._deferred_error_received.set_result(True)

    def error_raiser(self, *args: Any, **kwargs: Any) -> None:
        raise self.exception

    async def error_raiser_async(self, *args: Any, **kwargs: Any) -> None:
        if self._deferred_raised_exception:
            self._deferred_raised_exception.set_result(True)
        raise self.exception

    def assert_error_was_emitted(self) -> None:
        assert self.emitted_exception is self.emitted_exception

    async def assert_error_was_emitted_async(self) -> None:
        assert (
            self._deferred_raised_exception is not None
            and self._deferred_error_received is not None
        )
        await gather(self._deferred_raised_exception, self._deferred_error_received)
        assert self.emitted_exception is self.emitted_exception

    def assert_error_was_not_emitted(self) -> None:
        assert self.emitted_exception is None

    async def assert_error_was_not_emitted_async(self) -> None:
        assert (
            self._deferred_raised_exception is not None
            and self._deferred_error_received is not None
        )
        await self._deferred_raised_exception
        assert not self._deferred_error_received.done()
        self._deferred_error_received.set_result(True)
        assert self.emitted_exception is None


@pytest.fixture
def error_helper() -> EEExceptionHelper:
    return EEExceptionHelper()
