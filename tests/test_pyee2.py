from asyncio import AbstractEventLoop

import pytest
from mock import Mock

from pyee2 import EventEmitter


def test_on() -> None:
    ee = EventEmitter()
    mock = Mock()

    ee.on("event", mock.method)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]
    assert ee.emit("event", 1, data=2)

    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]


def test_on_decorator() -> None:
    ee = EventEmitter()
    mock = Mock()

    @ee.on("event")
    def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)

    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]


def test_once() -> None:
    ee = EventEmitter()
    mock = Mock()

    ee.once("event", mock.method)

    assert ee.listener_count("event") == 1
    assert mock.method is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)
    assert not ee.emit("event", 1, data=2)

    mock.method.assert_called_once_with(1, data=2)

    assert ee.listener_count("event") == 0
    assert mock.method not in ee.listeners("event")


def test_once_decorator() -> None:
    ee = EventEmitter()
    mock = Mock()

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


@pytest.mark.asyncio
async def test_coroutine_listener(event_loop: AbstractEventLoop) -> None:
    ee = EventEmitter(loop=event_loop)
    deferred = event_loop.create_future()
    mock = Mock()

    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.on("event", handler)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]
    assert ee.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_decorator(event_loop: AbstractEventLoop) -> None:
    ee = EventEmitter(loop=event_loop)
    deferred = event_loop.create_future()
    mock = Mock()

    @ee.on("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]
    assert ee.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]


@pytest.mark.asyncio
async def test_coroutine_listener_once(event_loop: AbstractEventLoop) -> None:
    ee = EventEmitter(loop=event_loop)
    deferred = event_loop.create_future()
    mock = Mock()

    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.once("event", handler)
    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)
    assert await deferred

    assert not ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ee.listener_count("event") == 0
    assert handler not in ee.listeners("event")


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator(event_loop: AbstractEventLoop) -> None:
    ee = EventEmitter(loop=event_loop)
    deferred = event_loop.create_future()
    mock = Mock()

    @ee.once("event")
    async def handler(*args, **kwargs) -> None:
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    assert ee.listener_count("event") == 1
    assert handler is ee.listeners("event")[0]

    assert ee.emit("event", 1, data=2)

    assert await deferred
    assert not ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
    assert ee.listener_count("event") == 0
    assert handler not in ee.listeners("event")

