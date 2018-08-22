# -*- coding: utf-8 -*-

import pytest
from mock import Mock
from asyncio import Future

from pyee2 import EventEmitter


def test_on():
    ee = EventEmitter()
    mock = Mock()

    ee.on("event", mock.method)

    ee.emit("event", 1, data=2)
    mock.method.assert_called_with(1, data=2)


def test_on_decorator():
    ee = EventEmitter()
    mock = Mock()

    @ee.on("event")
    def handler(*args, **kwargs):
        mock.method(*args, **kwargs)

    ee.emit("event", 1, data=2)
    mock.method.assert_called_with(1, data=2)


def test_once():
    ee = EventEmitter()
    mock = Mock()

    ee.once("event", mock.method)

    ee.emit("event", 1, data=2)
    ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)


def test_once_decorator():
    ee = EventEmitter()
    mock = Mock()

    @ee.once("event")
    def handler(*args, **kwargs):
        mock.method(*args, **kwargs)

    ee.emit("event", 1, data=2)
    ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)


@pytest.mark.asyncio
async def test_coroutine_listener(event_loop):
    ee = EventEmitter(loop=event_loop)
    deferred = Future(loop=event_loop)
    mock = Mock()

    async def handler(*args, **kwargs):
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.on("event", handler)
    ee.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)


@pytest.mark.asyncio
async def test_coroutine_listener_decorator(event_loop):
    ee = EventEmitter(loop=event_loop)
    deferred = Future(loop=event_loop)
    mock = Mock()

    @ee.on("event")
    async def handler(*args, **kwargs):
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.emit("event", 1, data=2)

    assert await deferred
    mock.method.assert_called_with(1, data=2)


@pytest.mark.asyncio
async def test_coroutine_listener_once(event_loop):
    ee = EventEmitter(loop=event_loop)
    deferred = Future(loop=event_loop)
    mock = Mock()

    async def handler(*args, **kwargs):
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.once("event", handler)
    ee.emit("event", 1, data=2)

    assert await deferred
    ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)


@pytest.mark.asyncio
async def test_coroutine_listener_once_decorator(event_loop):
    ee = EventEmitter(loop=event_loop)
    deferred = Future(loop=event_loop)
    mock = Mock()

    @ee.once("event")
    async def handler(*args, **kwargs):
        mock.method(*args, **kwargs)
        deferred.set_result(True)

    ee.emit("event", 1, data=2)

    assert await deferred
    ee.emit("event", 1, data=2)
    mock.method.assert_called_once_with(1, data=2)
