# flake8: noqa

# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
#   X.Y.0   # For first release after an increment in Y
#   X.Y.Z   # For bugfix releases
__version__ = '0.1.0'

import logging
from asyncio import CancelledError, create_task, iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, Tuple, Type, TypeVar, Union

from .event import Event

EventType = TypeVar('EventType', bound=Event)
CallableType = Callable[[EventType, Any], None]
AsyncCallableType = Callable[[EventType, Any], Awaitable[None]]

_listeners: Dict[str, Dict[Union[CallableType, AsyncCallableType], Tuple[Tuple[Any, ...], Dict[str, Any]]]] = {}


def listen(e: Type[Event], listener: Union[CallableType, AsyncCallableType], *args, **kwargs) -> None:
    logging.debug(f'{listener} listening {e.__name__}')
    listeners = _listeners.get(e.__name__) or {}
    listeners[listener] = (args, kwargs)
    _listeners.update({e.__name__: listeners})


def unregister(e: Type[Event], listener: Union[CallableType, AsyncCallableType]) -> None:
    if e.__name__ not in _listeners:
        return

    try:
        del _listeners[e.__name__][listener]

    except KeyError:
        pass


def unregister_all() -> None:
    global _listeners

    _listeners = {}


def on(e: Type[Event], *args, **kwargs):
    def register(listener: Union[CallableType, AsyncCallableType]) -> Callable[[Event], Awaitable[None]]:
        listen(e, listener, *args, **kwargs)

        return listener

    return register


def emit(e: Event) -> None:
    create_task(__run_listeners(e))


def get_listeners(e: Type[Event]) \
        -> Dict[str, Dict[Union[CallableType, AsyncCallableType], Tuple[Tuple[Any, ...], Dict[str, Any]]]]:
    return _listeners.get(e.__name__, {})


async def __run_listeners(e: Event) -> None:
    listeners = _listeners.get(e.__class__.__name__) or {}

    for listener, (args, kwargs) in listeners.items():
        create_task(__run_listener(e, listener, *args, **kwargs))


async def __run_listener(e: Event, listener: Union[CallableType, AsyncCallableType], *args, **kwargs) -> None:
    # noinspection PyBroadException
    try:
        if iscoroutinefunction(listener):
            await listener(e, *args, **kwargs)

        else:
            listener(e, *args, **kwargs)

    except CancelledError:
        pass

    except Exception:
        logging.exception(f'Exception in {listener.__name__} for {e.__class__.__name__}!')
