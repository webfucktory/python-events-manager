import logging
from asyncio import sleep
from unittest.mock import AsyncMock, Mock

from _pytest.monkeypatch import MonkeyPatch
from pytest import mark
from pytest_asyncio import fixture

from events_manager import Event, listen, emit, unregister_all, unregister, on, get_listeners


class FooEvent(Event):
    pass


class BarEvent(Event):
    pass


@fixture
def foo_event() -> FooEvent:
    return FooEvent()


@fixture
def uses_events() -> None:
    yield
    unregister_all()


@fixture
def bar_event() -> BarEvent:
    return BarEvent()


@fixture
def foo_value() -> int:
    return 1


@fixture
def bar_value() -> str:
    return "a"


@mark.asyncio
async def test_emit_calls_listeners_once_with_passed_event(uses_events, foo_event: FooEvent):
    # Arrange
    mock = Mock()

    listen(FooEvent, mock)

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_called_once_with(foo_event)


@mark.asyncio
async def test_emit_awaits_async_listeners_once_with_passed_event(uses_events, foo_event: FooEvent):
    # Arrange
    mock = AsyncMock()

    listen(FooEvent, mock)

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_awaited_once_with(foo_event)


@mark.asyncio
async def test_emit_awaits_async_listeners_once_with_passed_event_and_passed_args(uses_events, foo_event: FooEvent,
                                                                                  foo_value: int, bar_value: str):
    # Arrange
    mock = AsyncMock()

    listen(FooEvent, mock, foo=foo_value, bar=bar_value)

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_awaited_once_with(foo_event, foo=foo_value, bar=bar_value)


@mark.asyncio
async def test_emit_not_calls_listeners_for_other_events(uses_events, foo_event: FooEvent):
    # Arrange
    mock = AsyncMock()

    listen(FooEvent, AsyncMock())
    listen(BarEvent, mock)

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_not_awaited()


@mark.asyncio
async def test_emit_catches_exception(uses_events, foo_event: FooEvent):
    # Arrange
    mock = AsyncMock()

    # noinspection PyUnusedLocal
    @on(FooEvent)
    async def listener(e: Event) -> None:
        raise Exception

    listen(FooEvent, mock)

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_awaited_once_with(foo_event)


@mark.asyncio
async def test_emit_writes_log_for_exception(monkeypatch: MonkeyPatch, uses_events, foo_event: FooEvent):
    # Arrange
    mock = Mock()
    monkeypatch.setattr(logging, 'exception', mock)

    # noinspection PyUnusedLocal
    @on(FooEvent)
    async def listener(e: Event) -> None:
        raise Exception

    # Act
    emit(foo_event)
    await sleep(.001)

    # Assert
    mock.assert_called_once()


def test_listen(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) > 0


def test_listen_unregister(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)
    unregister(FooEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) == 0


def test_listen_multiple(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)
    listen(BarEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) == 1
    assert len(get_listeners(BarEvent)) == 1


def test_on(uses_events):
    # Arrange
    @on(FooEvent)
    async def listener() -> None:
        pass

    # Assert
    assert len(get_listeners(FooEvent)) == 1


def test_on_unregister(uses_events):
    # Arrange
    @on(FooEvent)
    async def listener() -> None:
        pass

    # Act
    unregister(FooEvent, listener)

    # Assert
    assert len(get_listeners(FooEvent)) == 0


def test_on_multiple(uses_events):
    # Arrange
    @on(FooEvent)
    async def foo_listener() -> None:
        pass

    @on(BarEvent)
    async def bar_listener() -> None:
        pass

    # Assert
    assert len(get_listeners(FooEvent)) == 1
    assert len(get_listeners(BarEvent)) == 1


def test_unregister_one_listener(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)
    unregister(FooEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) == 0


def test_unregister_no_listener(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)
    unregister(BarEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) == 1


def test_unregister_all(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    listen(FooEvent, mock)
    listen(BarEvent, mock)
    unregister_all()

    # Assert
    assert len(get_listeners(FooEvent)) == 0
    assert len(get_listeners(BarEvent)) == 0


def test_unregister_none(uses_events):
    # Arrange
    mock = AsyncMock()

    # Act
    unregister(FooEvent, mock)

    # Assert
    assert len(get_listeners(FooEvent)) == 0
