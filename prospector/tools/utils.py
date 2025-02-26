import sys
from io import TextIOWrapper
from typing import Optional


class CaptureStream(TextIOWrapper):
    def __init__(self) -> None:
        self.contents = ""

    def write(self, text: str, /) -> int:
        self.contents += text
        return len(text)

    def close(self) -> None:
        pass

    def flush(self) -> None:
        pass


class CaptureOutput:
    _prev_streams = None
    stdout: Optional[TextIOWrapper] = None
    stderr: Optional[TextIOWrapper] = None

    def __init__(self, hide: bool) -> None:
        self.hide = hide

    def __enter__(self) -> "CaptureOutput":
        if self.hide:
            self._prev_streams = (
                sys.stdout,
                sys.stderr,
                sys.__stdout__,
                sys.__stderr__,
            )
            self.stdout = CaptureStream()
            self.stderr = CaptureStream()
            sys.stdout, sys.__stdout__ = self.stdout, self.stdout  # type: ignore[misc]
            sys.stderr, sys.__stderr__ = self.stderr, self.stderr  # type: ignore[misc]
        return self

    def get_hidden_stdout(self) -> str:
        assert isinstance(self.stdout, CaptureStream)
        return self.stdout.contents

    def get_hidden_stderr(self) -> str:
        assert isinstance(self.stderr, CaptureStream)
        return self.stderr.contents

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: type) -> None:
        if self.hide:
            assert self._prev_streams is not None
            sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__ = self._prev_streams  # type: ignore[misc]
            del self._prev_streams
