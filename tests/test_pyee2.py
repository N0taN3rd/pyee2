from asyncio import AbstractEventLoop, Future

import pytest
from mock import Mock

from pyee2 import EventEmitter


def test_on(ee: EventEmitter, mock: Mock) -> None:
    ee.on("event", mock.method)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]
    assert ee.emit("event", 1, data=2)

    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]


def test_on_emits_error_when_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    ee.on("event", error_helper.error_raiser)
    ee.on("error", error_helper.error_listener)
    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 1
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()


def test_on_does_not_emits_error_when_not_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    ee.on("event", error_helper.error_raiser)
    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 0
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()


def test_on_decorator(ee: EventEmitter, mock: Mock) -> None:
    @ee.on("event")
    def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)

    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]


def test_on_decorator_emits_error_when_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    @ee.on("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    @ee.on("error")
    def error_handler(*args, **kwargs) -> None:
        error_helper.error_listener(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 1
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()


def test_on_decorator_does_not_emits_error_when_not_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    @ee.on("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 0
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()


def test_once(ee: EventEmitter, mock: Mock) -> None:
    ee.once("event", mock.method)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)
    assert not ee.emit("event", 1, data=2)

    mock.method.assert_called_once_with(1, data=2)

    assert ee.listener_count("event") == 0
    assert mock.method not in ee.listeners("event")


def test_once_emits_error_when_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    ee.once("event", error_helper.error_raiser)
    ee.once("error", error_helper.error_listener)
    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 1
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()
    assert ee.listener_count("event") == 0
    assert ee.listener_count("error") == 0


def test_once_does_not_emits_error_when_not_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    ee.once("event", error_helper.error_raiser)
    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 0
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()
    assert ee.listener_count("event") == 0
    assert ee.listener_count("error") == 0


def test_once_decorator(ee: EventEmitter, mock: Mock) -> None:
    @ee.once("event")
    def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)
    assert not ee.emit("event", 1, data=2)

    mock.method.assert_called_once_with(1, data=2)

    assert ee.listener_count("event") == 0
    assert handler not in ee.listeners("event")


def test_once_decorator_emits_error_when_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    @ee.once("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    @ee.once("error")
    def error_handler(*args, **kwargs) -> None:
        error_helper.error_listener(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 1
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_emitted()
    assert ee.listener_count("event") == 0
    assert ee.listener_count("error") == 0


def test_once_decorator_does_not_emits_error_when_not_listening_for_errors(
    ee: EventEmitter, error_helper
) -> None:
    @ee.once("event")
    def handler(*args, **kwargs) -> None:
        error_helper.error_raiser(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert ee.listener_count("error") == 0
    assert ee.emit("event", 1, data=2)
    error_helper.assert_error_was_not_emitted()
    assert ee.listener_count("event") == 0
    assert ee.listener_count("error") == 0


@pytest.mark.asyncio
async def test_coroutine_listener(
    ee_with_event_loop: EventEmitter, mock: Mock, deferred: Future
) -> None:
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee_with_event_loop.on("event", handler)

    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]
    assert ee_with_event_loop.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)

    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_emits_error_when_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)
    ee_with_event_loop.on("event", error_helper.error_raiser_async)
    ee_with_event_loop.on("error", error_helper.error_listener_async)
    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 1
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()


@pytest.mark.asyncio
async def test_coroutine_listener_does_not_emits_error_when_not_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)
    ee_with_event_loop.on("event", error_helper.error_raiser_async)
    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 0
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()


@pytest.mark.asyncio
async def test_coroutine_listener_decorator(
    ee_with_event_loop: EventEmitter, mock: Mock, deferred: Future
) -> None:
    @ee_with_event_loop.on("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]
    assert ee_with_event_loop.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)

    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_decorator_emits_error_when_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)

    @ee_with_event_loop.on("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    @ee_with_event_loop.on("error")
    async def error_listener(*args, **kwargs) -> None:
        await error_helper.error_listener_async(*args, **kwargs)

    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 1
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()
    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 1


@pytest.mark.asyncio
async def test_coroutine_listener_decorator_does_not_emits_error_when_not_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)

    @ee_with_event_loop.on("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()
    assert ee_with_event_loop.listener_count("event") == 1


@pytest.mark.asyncio
async def test_coroutine_listener_once(
    ee_with_event_loop: EventEmitter, mock: Mock, deferred: Future
) -> None:
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee_with_event_loop.once("event", handler)
    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]

    assert ee_with_event_loop.emit("event", 1, data=2)
    assert await deferred

    assert not ee_with_event_loop.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ee_with_event_loop.listener_count("event") == 0
    assert handler not in ee_with_event_loop.listeners("event")


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator(
    ee_with_event_loop: EventEmitter, mock: Mock, deferred: Future
) -> None:
    @ee_with_event_loop.once("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ee_with_event_loop.listener_count("event") == 1
    assert handler is ee_with_event_loop.listeners("event")[0]

    assert ee_with_event_loop.emit("event", 1, data=2)

    assert await deferred
    assert not ee_with_event_loop.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ee_with_event_loop.listener_count("event") == 0
    assert handler not in ee_with_event_loop.listeners("event")


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator_emits_error_when_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)

    @ee_with_event_loop.once("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    @ee_with_event_loop.once("error")
    async def error_listener(*args, **kwargs) -> None:
        await error_helper.error_listener_async(*args, **kwargs)

    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 1
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_emitted_async()
    assert ee_with_event_loop.listener_count("event") == 0
    assert ee_with_event_loop.listener_count("error") == 0


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator_does_not_emits_error_when_not_listening_for_errors(
    ee_with_event_loop: EventEmitter, error_helper, event_loop: AbstractEventLoop
) -> None:
    error_helper.with_deferred(event_loop)

    @ee_with_event_loop.once("event")
    async def error_raiser(*args, **kwargs) -> None:
        await error_helper.error_raiser_async(*args, **kwargs)

    assert ee_with_event_loop.listener_count("event") == 1
    assert ee_with_event_loop.listener_count("error") == 0
    assert ee_with_event_loop.emit("event", 1, data=2)
    await error_helper.assert_error_was_not_emitted_async()
    assert ee_with_event_loop.listener_count("event") == 0
    assert ee_with_event_loop.listener_count("error") == 0
