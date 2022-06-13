[![Lint & Test](https://github.com/webfucktory/python-events-manager/actions/workflows/lint-test.yml/badge.svg)](https://github.com/webfucktory/python-events-manager/actions/workflows/lint-test.yml)
[![PyPI version](https://badge.fury.io/py/events-manager.svg)](https://pypi.org/project/events-manager)
[![Downloads count](https://img.shields.io/pypi/dm/events-manager)](https://pypistats.org/packages/events-manager)

# Events Manager

Python implementation of the **Events Management** system (aka [Observer pattern](https://en.wikipedia.org/wiki/Observer_pattern)).

## Getting started

### Requirements

- Python >= 3.8

### Installation

```bash
pip install events-manager
```

## Usage

### Listening and emitting an Event

Listener is invoked when the event is emitted.

```python
from asyncio import run, sleep

from events_manager import Event, emit, listen


class FooEvent(Event):
    pass


def foo_listener(event: FooEvent):
    print(f"'foo_listener' invoked with {event}")


async def main():
    listen(FooEvent, foo_listener)

    print("Emitting event...")
    emit(FooEvent())

    # do the other stuff...
    await sleep(1)


if __name__ == '__main__':
    run(main())
```

Output:

```
Emitting event...
'foo_listener' invoked with <__main__.FooEvent object at 0x7fdce6f5a0a0>

Process finished with exit code 0
```

### `sync` and `async` listeners

```python
from asyncio import run, sleep

from events_manager import Event, emit, listen


class FooEvent(Event):
    pass


async def foo_listener(event: FooEvent):
    print(f"'foo_listener' invoked with {event}")


async def main():
    listen(FooEvent, foo_listener)

    print("Emitting event...")
    emit(FooEvent())

    # do the other stuff...
    await sleep(1)


if __name__ == '__main__':
    run(main())
```

Output:

```
Emitting event...
'foo_listener' invoked with <__main__.FooEvent object at 0x7f81e76ad0a0>

Process finished with exit code 0
```

### `args` and `kwargs` support

The `listen` method supports also `args` and `kwargs` that will be passed to the listened listener.

```python
from asyncio import run, sleep

from events_manager import Event, emit, listen


class FooEvent(Event):
    pass


async def foo_listener(event: FooEvent, bar, baz):
    print(f"'foo_listener' invoked with {event}, {bar} and {baz}")


async def main():
    listen(FooEvent, foo_listener, False, 'bar', baz='baz')

    print("Emitting event...")
    emit(FooEvent())

    # do the other stuff...
    await sleep(1)


if __name__ == '__main__':
    run(main())

```

Output:

```
Emitting event...
'foo_listener' invoked with <__main__.FooEvent object at 0x7fdbd0fa50d0>, bar and baz

Process finished with exit code 0
```

### Register a listener with `@on` decorator

Instead of calling `listen` method, you can also use the `@on` decorator.

```python
from asyncio import run, sleep

from events_manager import Event, emit, on


class FooEvent(Event):
    pass


@on(FooEvent)
def foo_listener(event: FooEvent):
    print(f"'foo_listener' invoked with {event}")


async def main():
    print("Emitting event...")
    emit(FooEvent())

    # do the other stuff...
    await sleep(1)


if __name__ == '__main__':
    run(main())

```

Output:

```
Emitting event...
'foo_listener' invoked with <__main__.FooEvent object at 0x7fa0a9a47100>

Process finished with exit code 0
```

### Unregister a listener

Call `unregister` method passing the event type that you want to stop listening and the listener.

```python
from asyncio import run, sleep

from events_manager import Event, emit, listen, unregister


class FooEvent(Event):
    pass


def foo_listener(event: FooEvent):
    print(f"'foo_listener' invoked with {event}")


async def main():
    listen(FooEvent, foo_listener)

    print("Emitting first event...")
    emit(FooEvent())

    # let the event be processed
    await sleep(1)

    unregister(FooEvent, foo_listener)

    print("Emitting second event...")
    emit(FooEvent())

    # do the other stuff...
    await sleep(1)


if __name__ == '__main__':
    run(main())

```

Output:

```
Emitting first event...
'foo_listener' invoked with <__main__.FooEvent object at 0x7f92c79b9070>
Emitting second event...

Process finished with exit code 0
```

## Development

### Run Tests

```shell script
./test
```

### Style Check

```shell script
./lint
```

## License

Distributed under the MIT License. See `LICENSE` file for more information.
