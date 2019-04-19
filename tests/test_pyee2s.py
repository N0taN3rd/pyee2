from asyncio import AbstractEventLoop, Future
from typing import Callable, TYPE_CHECKING
import pytest
from mock import Mock

from pyee2 import EventEmitterS

if TYPE_CHECKING:
    from .conftest import EEExceptionHelper


def test_get_listeners_registered_for_event(
    ees: EventEmitterS, arg_swallower: Callable[..., None]
) -> None:
    ees.on("event", arg_swallower)
    ees_listeners = ees.listeners("event")
    assert len(ees_listeners) == 1
    assert ees_listeners[0] is arg_swallower


def test_remove_listener_registered_for_event(
    ees: EventEmitterS, arg_swallower: Callable[..., None]
) -> None:
    ees.on("event", arg_swallower)
    assert ees.listener_count("event") == 1
    assert arg_swallower is ees.listeners("event")[0]
    ees.remove_listener("event", arg_swallower)
    assert ees.listener_count("event") == 0


def test_remove_all_listeners_registered_for_event(
    ees: EventEmitterS, arg_swallower: Callable[..., None]
) -> None:
    ees.on("event", arg_swallower)
    assert ees.listener_count("event") == 1
    assert arg_swallower is ees.listeners("event")[0]
    ees.remove_all_listeners("event")
    assert ees.listener_count("event") == 0


def test_remove_all_listeners(
    ees: EventEmitterS, arg_swallower: Callable[..., None]
) -> None:
    ees.on("event", arg_swallower)
    assert ees.listener_count("event") == 1
    assert arg_swallower is ees.listeners("event")[0]
    ees.remove_all_listeners()
    assert ees.listener_count("event") == 0


def test_get_event_names(ees: EventEmitterS, arg_swallower: Callable[..., None]) -> None:
    events = {"event", "event1", "event2", "event3"}
    for event in events:
        ees.on(event, arg_swallower)
    assert all(
        registered_event_name in events for registered_event_name in ees.event_names()
    )


def test_on(ees: EventEmitterS, mock: Mock) -> None:
    ees.on("event", mock.method)
    assert ees.listener_count("event") == 1
    assert mock.method is ees.listeners("event")[0]
    assert ees.emit("event", 1, data=2)
    mock.method.assert_called_with(1, data=2)
    assert ees.listener_count("event") == 1
    assert mock.method is ees.listeners("event")[0]


def test_on_emits_error_when_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    ees.on("event", error_helper.error_raiser)
    ees.on("error", error_helper.error_listener)
    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 1
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()


def test_on_does_not_emits_error_when_not_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    ees.on("event", error_helper.error_raiser)
    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 0
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()


def test_on_decorator(ees: EventEmitterS, mock: Mock) -> None:
    @ees.on("event")
    def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert handler is ees.listeners("event")[0]
    assert ees.emit("event", 1, data=2)
    mock.method.assert_called_with(1, data=2)
    assert ees.listener_count("event") == 1
    assert handler is ees.listeners("event")[0]


def test_on_decorator_emits_error_when_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    @ees.on("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    @ees.on("error")
    def error_handler(*args, **kwargs) -> None:
        error_helper.error_listener(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 1
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()


def test_on_decorator_does_not_emits_error_when_not_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    @ees.on("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 0
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()


def test_once(ees: EventEmitterS, mock: Mock) -> None:
    ees.once("event", mock.method)

    assert ees.listener_count("event") == 1
    assert mock.method is ees.listeners("event")[0]
    assert ees.emit("event", 1, data=2)
    assert not ees.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ees.listener_count("event") == 0
    assert mock.method not in ees.listeners("event")


def test_once_emits_error_when_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    ees.once("event", error_helper.error_raiser)
    ees.once("error", error_helper.error_listener)
    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 1
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()
    assert ees.listener_count("event") == 0
    assert ees.listener_count("error") == 0


def test_once_does_not_emits_error_when_not_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    ees.once("event", error_helper.error_raiser)
    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 0
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()
    assert ees.listener_count("event") == 0
    assert ees.listener_count("error") == 0


def test_once_decorator(ees: EventEmitterS, mock: Mock) -> None:
    @ees.once("event")
    def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert handler is ees.listeners("event")[0]
    assert ees.emit("event", 1, data=2)
    assert not ees.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ees.listener_count("event") == 0
    assert handler not in ees.listeners("event")


def test_once_decorator_emits_error_when_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    @ees.once("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    @ees.once("error")
    def error_handler(*args, **kwargs) -> None:
        error_helper.error_listener(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 1
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()
    assert ees.listener_count("event") == 0
    assert ees.listener_count("error") == 0


def test_once_decorator_does_not_emits_error_when_not_listening_for_errors(
    ees: EventEmitterS, error_helper: "EEExceptionHelper"
) -> None:
    @ees.once("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    assert ees.listener_count("event") == 1
    assert ees.listener_count("error") == 0
    assert ees.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()
    assert ees.listener_count("event") == 0
    assert ees.listener_count("error") == 0


@pytest.mark.asyncio
async def test_coroutine_listener(
    ees_with_event_loop: EventEmitterS, mock: Mock, deferred: Future
) -> None:
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ees_with_event_loop.on("event", handler)

    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]
    assert ees_with_event_loop.emit("event", 1, data=2)
    assert await deferred
    mock.method.assert_called_with(1, data=2)
    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_emits_error_when_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)
    ees_with_event_loop.on("event", error_helper.error_raiser_async)
    ees_with_event_loop.on("error", error_helper.error_listener_async)
    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 1
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()


@pytest.mark.asyncio
async def test_coroutine_listener_does_not_emits_error_when_not_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)
    ees_with_event_loop.on("event", error_helper.error_raiser_async)
    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 0
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()


@pytest.mark.asyncio
async def test_coroutine_listener_decorator(
    ees_with_event_loop: EventEmitterS, mock: Mock, deferred: Future
) -> None:
    @ees_with_event_loop.on("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]
    assert ees_with_event_loop.emit("event", 1, data=2)
    assert await deferred
    mock.method.assert_called_with(1, data=2)
    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_decorator_emits_error_when_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)

    @ees_with_event_loop.on("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    @ees_with_event_loop.on("error")
    async def error_listener(*args, **kwargs) -> None:
        await error_helper.error_listener_async(*args, **kwargs)

    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 1
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()
    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 1


@pytest.mark.asyncio
async def test_coroutine_listener_decorator_does_not_emits_error_when_not_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)

    @ees_with_event_loop.on("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()
    assert ees_with_event_loop.listener_count("event") == 1


@pytest.mark.asyncio
async def test_coroutine_listener_once(
    ees_with_event_loop: EventEmitterS, mock: Mock, deferred: Future
) -> None:
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ees_with_event_loop.once("event", handler)
    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]
    assert ees_with_event_loop.emit("event", 1, data=2)
    assert await deferred
    assert not ees_with_event_loop.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ees_with_event_loop.listener_count("event") == 0
    assert handler not in ees_with_event_loop.listeners("event")


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator(
    ees_with_event_loop: EventEmitterS, mock: Mock, deferred: Future
) -> None:
    @ees_with_event_loop.once("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ees_with_event_loop.listener_count("event") == 1
    assert handler is ees_with_event_loop.listeners("event")[0]
    assert ees_with_event_loop.emit("event", 1, data=2)
    assert await deferred
    assert not ees_with_event_loop.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ees_with_event_loop.listener_count("event") == 0
    assert handler not in ees_with_event_loop.listeners("event")


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator_emits_error_when_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)

    @ees_with_event_loop.once("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    @ees_with_event_loop.once("error")
    async def error_listener(*args, **kwargs) -> None:
        await error_helper.error_listener_async(*args, **kwargs)

    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 1
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()
    assert ees_with_event_loop.listener_count("event") == 0
    assert ees_with_event_loop.listener_count("error") == 0


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator_does_not_emits_error_when_not_listening_for_errors(
    ees_with_event_loop: EventEmitterS,
    error_helper: "EEExceptionHelper",
    event_loop: AbstractEventLoop,
) -> None:
    error_helper.with_deferred(event_loop)

    @ees_with_event_loop.once("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    assert ees_with_event_loop.listener_count("event") == 1
    assert ees_with_event_loop.listener_count("error") == 0
    assert ees_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()
    assert ees_with_event_loop.listener_count("event") == 0
    assert ees_with_event_loop.listener_count("error") == 0
