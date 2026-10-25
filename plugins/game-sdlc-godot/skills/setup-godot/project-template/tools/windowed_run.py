"""Run a windowed Godot (or any command) while holding this checkout's window lock.

    python3 tools/windowed_run.py [--timeout SECONDS] [--] <command> [arguments...]

Parallel agents opening game windows in one checkout steal each other's focus, and a game that loses
focus pauses. So every windowed run (a capture, a playtest, the editor) goes through this wrapper: it
holds .agents/local/windowed-run.lock for the run, waits up to --timeout seconds (default 600) while
another run holds it, and always releases it. The lock is the operating system's, so it is released
even when this process is killed. Headless runs (tests, imports, exports) don't need it.

A command whose first word is `godot` runs the project's Godot, found in the order the hooks use:
GODOT_BIN, then .agents/local/godot, then `godot` on PATH. Exits with the command's exit code, or 75
when the wait timed out. Standard library only.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / ".agents" / "local" / "windowed-run.lock"
DEFAULT_TIMEOUT = 600.0
POLL_SECONDS = 0.25
TIMED_OUT = 75
# Windows file locks are mandatory, so the lock sits on a byte past the holder's note: a waiting run
# can still read who holds it.
LOCK_BYTE = 1 << 20


def parse(arguments: list[str]) -> tuple[float, list[str]]:
    timeout = DEFAULT_TIMEOUT
    rest = list(arguments)
    while rest:
        if rest[0] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if rest[0] == "--timeout" and len(rest) > 1:
            timeout, rest = float(rest[1]), rest[2:]
        elif rest[0].startswith("--timeout="):
            timeout, rest = float(rest[0].split("=", 1)[1]), rest[1:]
        elif rest[0] == "--":
            rest = rest[1:]
            break
        else:
            break
    if not rest:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    return timeout, rest


def godot() -> str:
    local = ROOT / ".agents" / "local" / "godot"
    candidates = [os.environ.get("GODOT_BIN", "")]
    if local.is_file():
        candidates.append(local.read_text(encoding="utf-8").strip())
    for candidate in candidates:
        if candidate and (Path(candidate).is_file() or shutil.which(candidate)):
            return candidate
    return "godot"


def try_lock(fd: int) -> bool:
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, LOCK_BYTE, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def unlock(fd: int) -> None:
    if os.name == "nt":
        import msvcrt

        os.lseek(fd, LOCK_BYTE, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_UN)


def holder() -> str:
    try:
        return LOCK.read_text(encoding="utf-8", errors="replace").strip() or "another run"
    except OSError:
        return "another run"


def write_note(fd: int, note: str) -> None:
    os.ftruncate(fd, 0)
    os.lseek(fd, 0, os.SEEK_SET)
    if note:
        os.write(fd, note.encode("utf-8"))


def acquire(fd: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    waiting = False
    while not try_lock(fd):
        if not waiting:
            print(f"windowed_run: waiting up to {timeout:g}s for the window lock ({holder()})", file=sys.stderr)
            waiting = True
        if time.monotonic() >= deadline:
            print(f"windowed_run: still held after {timeout:g}s ({holder()}); giving up", file=sys.stderr)
            return False
        time.sleep(POLL_SECONDS)
    return True


def main() -> int:
    timeout, command = parse(sys.argv[1:])
    if command[0] == "godot":
        command[0] = godot()
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        if not acquire(fd, timeout):
            return TIMED_OUT
        try:
            write_note(fd, f"pid {os.getpid()} since {time.strftime('%H:%M:%S')}: {' '.join(command)}")
            return subprocess.run(command).returncode
        except FileNotFoundError:
            print(f"windowed_run: command not found: {command[0]}", file=sys.stderr)
            return 127
        except KeyboardInterrupt:
            return 130
        finally:
            write_note(fd, "")
            unlock(fd)
    finally:
        os.close(fd)


if __name__ == "__main__":
    sys.exit(main())
