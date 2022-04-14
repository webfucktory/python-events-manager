# events-manager

Python event system support implementation package.

[![Lint & Test](https://github.com/webfucktory/python-events-manager/actions/workflows/lint-test.yml/badge.svg)](https://github.com/webfucktory/python-events-manager/actions/workflows/lint-test.yml)
[![PyPI version](https://badge.fury.io/py/events-manager.svg)](https://pypi.org/project/events-manager)
[![Downloads count](https://img.shields.io/pypi/dm/events-manager)](https://pypistats.org/packages/events-manager)

## Getting started

### Requirements

- Python >= 3.8

### Installation

```bash
pip install events-manager
```

## Usage

### Creating an event

```python
from events_manager import Event

class FooEvent(Event):
    pass
```

### Listening and emitting an Event 

Listen means that when an event of the `type` passed as the `first argument` to the `listen` method is emitted, the 
`callable` passed as `second argument` will be invoked passing the event emitted. 

```python
from events_manager import Event, listen, emit

def on_foo_event(event: Event):
    print(f"Callable invoked on {type(event).__name__}")

if __name__ == '__main__':    
    listen(FooEvent, on_foo_event)   
    
    foo_event = FooEvent()

    print("Emitting event...")
    emit(foo_event)
```

```bash
Emitting event...
Callable invoked on FooEvent

Process finished with exit code 0
```

The Events Manager supports both `sync` and `async` listeners. 

```python
from events_manager import Event, listen, emit
from asyncio import sleep

async def on_foo_event(event: Event) -> None:
    await sleep(10)
    print(f"Awaitable awaited on {type(event).__name__}")

if __name__ == '__main__':    
    listen(FooEvent, on_foo_event)
    
    foo_event = FooEvent()
    
    print("Emitting event...")
    emit(foo_event)
```

```bash
Emitting event...
Awaitable awaited on FooEvent

Process finished with exit code 0
```

### `args` and `kwargs` support

The `listen` method supports also `args` and `kwargs` that will be passed to the listened listener.

```python
from __future__ import annotations
from events_manager import Event, listen, emit

class Bar:
    @staticmethod
    def on_foo_event(event: Event, self: Bar) -> None:
        self.__do_something(event)
        
    def __do_something(self, event: Event) -> None:
        print(self)

if __name__ == '__main__':    
    bar = Bar()
    print(bar)
    
    listen(FooEvent, Bar.on_foo_event, bar)
    
    foo_event = FooEvent()
    
    print("Emitting event...")
    emit(foo_event)
```

```bash
<__main__.Bar object at 0x000001E4541FB4C0> 
Emitting event...
<__main__.Bar object at 0x000001E4541FB4C0>

Process finished with exit code 0
```

### `@on` decorator

Instead of calling `listen` method, you can also use the `@on` decorator.

```python
from events_manager import Event, emit, on

@on(FooEvent)
def on_foo_event(event: Event):
    print(f"Callable invoked on {type(event).__name__}")

if __name__ == '__main__':    
    foo_event = FooEvent()

    print("Emitting event...")
    emit(foo_event)
```

```bash
Emitting event...
Callable invoked on FooEvent

Process finished with exit code 0
```

### Unregister an event listener

Call `unregister` method passing the event type that you want to stop listening and the listener.

```python
from events_manager import Event, emit, listen, unregister

def on_foo_event(event: Event):
    print(f"Callable invoked on {type(event).__name__}")

if __name__ == '__main__':    
    foo_event = FooEvent()
    
    listen(FooEvent, on_foo_event)

    print("Emitting first event...")
    emit(foo_event)
    
    unregister(FooEvent, on_foo_event)
    
    print("Emitting second event...")
    emit(foo_event)
```

```bash
Emitting first event...
Callable invoked on FooEvent
Emitting second event...

Process finished with exit code 0
```

## License

Distributed under the MIT License. See `LICENSE` file for more information.
