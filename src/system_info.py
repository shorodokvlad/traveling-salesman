"""Runtime environment metadata for experiment reports."""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MachineInfo:
    hostname: str
    platform: str
    processor: str
    architecture: str
    python_version: str
    cpu_count: int | None
    timestamp_utc: str

    def as_text(self) -> str:
        lines = [
            f"Host: {self.hostname}",
            f"Platform: {self.platform}",
            f"Processor: {self.processor}",
            f"Architecture: {self.architecture}",
            f"Python: {self.python_version}",
        ]
        if self.cpu_count is not None:
            lines.append(f"CPU cores (logical): {self.cpu_count}")
        lines.append(f"Recorded (UTC): {self.timestamp_utc}")
        return "\n".join(lines)


def get_machine_info() -> MachineInfo:
    cpu_count = None
    try:
        import os

        cpu_count = os.cpu_count()
    except Exception:
        pass

    proc = platform.processor() or platform.machine()
    return MachineInfo(
        hostname=platform.node(),
        platform=platform.platform(),
        processor=proc,
        architecture=platform.machine(),
        python_version=sys.version.split()[0],
        cpu_count=cpu_count,
        timestamp_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    )
