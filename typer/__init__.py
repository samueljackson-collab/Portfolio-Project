"""Lightweight Typer compatibility shim used for testing."""

from __future__ import annotations

import inspect
import io
import sys
import typing as _typing
import warnings
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

_SENTINEL = object()
_WARNED = False


def _warn_once() -> None:
    global _WARNED
    if not _WARNED:
        warnings.warn(
            "Typer is not installed - using a very small fallback implementation.",
            RuntimeWarning,
            stacklevel=2,
        )
        _WARNED = True


@dataclass
class _Argument:
    default: Any = _SENTINEL


@dataclass
class _Option:
    default: Any = None
    names: Tuple[str, ...] = ()


def Argument(default: Any = _SENTINEL, *_: Any, **__: Any) -> _Argument:
    """Return a descriptor describing a positional argument."""

    _warn_once()
    if default is Ellipsis:
        default = _SENTINEL
    return _Argument(default=default)


def Option(default: Any = None, *names: str, **__: Any) -> _Option:
    """Return a descriptor describing an optional argument."""

    _warn_once()
    return _Option(default=default, names=names)


def echo(message: Any = "", **kwargs: Any) -> None:
    _warn_once()
    print(message, **kwargs)


class Exit(SystemExit):
    pass


class _Command:
    def __init__(self, func: Callable[..., Any]) -> None:
        self.func = func
        self.signature = inspect.signature(func)

    def invoke(self, argv: Sequence[str]) -> Any:
        positional: List[str] = []
        options: Dict[str, str] = {}

        iterator = iter(argv)
        for token in iterator:
            if token.startswith("-"):
                value = next(iterator, None)
                if value is None or value.startswith("-"):
                    # Flags without a value act like booleans.
                    options[token] = "True"
                    if value is not None:
                        positional.append(value)
                else:
                    options[token] = value
            else:
                positional.append(token)

        args: Dict[str, Any] = {}
        pos_index = 0
        for parameter in self.signature.parameters.values():
            default = parameter.default
            annotation = parameter.annotation
            if isinstance(default, _Argument):
                if pos_index < len(positional):
                    raw = positional[pos_index]
                    pos_index += 1
                elif default.default is not _SENTINEL:
                    raw = default.default
                else:
                    raise SystemExit(2)
                args[parameter.name] = _convert(raw, annotation)
            elif isinstance(default, _Option):
                raw = default.default
                for name in default.names:
                    if name in options:
                        raw = options[name]
                        break
                args[parameter.name] = _convert(raw, annotation)
            else:
                if pos_index < len(positional):
                    raw = positional[pos_index]
                    pos_index += 1
                    args[parameter.name] = _convert(raw, annotation)
                elif default is not inspect._empty:
                    args[parameter.name] = default
                else:
                    raise SystemExit(2)
        return self.func(**args)


def _convert(value: Any, annotation: Any) -> Any:
    if value is None:
        return None
    if annotation is inspect._empty:
        return value
    origin = _typing.get_origin(annotation)
    if origin is _typing.Union:
        args = [arg for arg in _typing.get_args(annotation) if arg is not type(None)]
        if args:
            return _convert(value, args[0])
        return None
    if annotation is Path:
        return Path(value)
    if annotation is float:
        return float(value)
    if annotation is int:
        return int(value)
    if annotation is bool:
        return str(value).lower() in {"1", "true", "yes", "on"}
    return value


class Typer:
    def __init__(self, help: Optional[str] = None) -> None:
        _warn_once()
        self.help = help
        self._commands: Dict[str, _Command] = {}

    def command(self, name: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            command_name = name or func.__name__
            self._commands[command_name] = _Command(func)
            return func

        return decorator

    def _execute(self, argv: Sequence[str]) -> Any:
        if not argv:
            raise SystemExit(0)
        command_name = argv[0]
        if command_name not in self._commands:
            raise SystemExit(2)
        command = self._commands[command_name]
        return command.invoke(list(argv[1:]))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        argv: Sequence[str]
        if args:
            argv = args[0]
        else:
            argv = sys.argv[1:]
        return self._execute(argv)


class _Result:
    def __init__(self, exit_code: int, output: str) -> None:
        self.exit_code = exit_code
        self.stdout = output
        self.output = output


class CliRunner:
    def invoke(self, app: Typer, args: Optional[Sequence[str]] = None) -> _Result:
        _warn_once()
        buffer = io.StringIO()
        exit_code = 0
        argv = list(args or [])
        try:
            with redirect_stdout(buffer):
                app._execute(argv)
        except SystemExit as exc:  # pragma: no cover - mirrors Typer behaviour
            code = exc.code if isinstance(exc.code, int) else 0
            exit_code = code
        except Exception:  # pragma: no cover - debug helper
            exit_code = 1
            import traceback

            buffer.write(traceback.format_exc())
        return _Result(exit_code=exit_code, output=buffer.getvalue())


__all__ = [
    "Typer",
    "Argument",
    "Option",
    "echo",
    "CliRunner",
    "Exit",
]
