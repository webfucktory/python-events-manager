# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# Generic release markers:
#   X.Y.0   # For first release after an increment in Y
#   X.Y.Z   # For bugfix releases
__version__ = '0.2.2'

import logging
from asyncio import CancelledError, create_task, iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, List, Tuple, Type, TypeVar, Union

from .event import Event

EventType = TypeVar('EventType', bound=Event)
CallableType = Callable[[EventType, Any], None]
AsyncCallableType = Callable[[EventType, Any], Awaitable[None]]
ListenerType = Union[CallableType, AsyncCallableType]
ListenersType = Dict[
    Type[Event],
    List[
        Tuple[
            Union[CallableType, AsyncCallableType],
            Tuple[Tuple[Any, ...], Dict[str, Any]],
        ]
    ]
]

_listeners: ListenersType = {}
_background_tasks = set()


class ListenerAlreadyExistsError(ValueError):
    pass


def listen(event_type: Type[Event], listener: ListenerType, check_if_exists: bool = False, *args, **kwargs) -> None:
    logging.debug(f'{listener} listening {event_type}')

    listeners = _listeners.get(event_type) or []

    if check_if_exists:
        for (l_, _) in listeners:
            if l_ == listener:
                raise ListenerAlreadyExistsError

    listeners.append((listener, (args, kwargs)))

    _listeners.update({event_type: listeners})


def unregister(event_type: Type[Event], listener: ListenerType) -> None:
    if event_type not in _listeners:
        return

    _listeners[event_type] = list(filter(lambda x: x[0] != listener, _listeners[event_type]))


def unregister_all() -> None:
    global _listeners

    _listeners = {}


def on(event_type: Type[Event], *args, **kwargs):
    def register(listener: ListenerType) -> Callable[[Event], Awaitable[None]]:
        listen(event_type, listener, *args, **kwargs)

        return listener

    return register


def emit(e: Event) -> None:
    logging.debug(f'emitting {e.__class__}: {e}')

    task = create_task(_run_listeners(e))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


def get_listeners(
        event_type: Type[Event]
) -> List[Tuple[Union[CallableType, AsyncCallableType], Tuple[Tuple[Any, ...], Dict[str, Any]]]]:
    return _listeners.get(event_type, [])


async def _run_listeners(e: Event) -> None:
    listeners = _listeners.get(e.__class__) or []

    for (listener, (args, kwargs)) in listeners:
        task = create_task(_run_listener(e, listener, *args, **kwargs))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)


async def _run_listener(e: Event, listener: ListenerType, *args, **kwargs) -> None:
    # noinspection PyBroadException
    try:
        if iscoroutinefunction(listener):
            await listener(e, *args, **kwargs)

        else:
            listener(e, *args, **kwargs)

    except CancelledError:
        pass

    except Exception:
        logging.exception(f'Exception in {listener.__name__} for {e.__class__}!')
