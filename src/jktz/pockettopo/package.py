"""P06 complete artifact packages, published once with atomic no-replace rename."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from jktz.pockettopo.compilation import validate_surveys
from jktz.pockettopo.drawings import DEFAULT_DRAWING_SETTINGS, DrawingSettings, export_drawings
from jktz.pockettopo.export import export_surveys
from jktz.pockettopo.export_policy import CorrectionPolicy
from jktz.pockettopo.report import ProcessingPlan

VARIANTS = {"plan-sketch", "plan-measurements", "side-sketch", "side-measurements"}


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def _destination(path: Path) -> Path:
    # Check both the written path and symlink-resolved parent, including dangling links.
    if "_raw" in {part.lower() for part in path.parts + path.resolve().parts}:
        raise ValueError("Output inside _RAW is forbidden; choose a separate working directory")
    target = path.absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Output already exists (collision policy: error): {target}")
    if not target.parent.is_dir():
        raise FileNotFoundError(f"Output parent directory does not exist: {target.parent}")
    return target.parent.resolve() / target.name


def _rename_noreplace(source: Path, target: Path) -> None:
    """One filesystem operation; even an empty concurrent target is never replaced.

    Windows rename already refuses an existing target. POSIX rename does not,
    so use the platform's exclusive variant and fail closed if unavailable.
    """
    if sys.platform == "win32":
        os.rename(source, target)
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        operation = libc.renamex_np
        operation.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        arguments = (os.fsencode(source), os.fsencode(target), 4)  # RENAME_EXCL
    elif sys.platform.startswith("linux"):
        operation = libc.renameat2
        operation.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        arguments = (-100, os.fsencode(source), -100, os.fsencode(target), 1)  # RENAME_NOREPLACE
    else:
        raise OSError(f"Atomic no-replace directory publication is unsupported on {sys.platform}")
    operation.restype = ctypes.c_int
    if operation(*arguments) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(target))


def _publish(target: Path, files: dict[str, bytes]) -> None:
    # The staging directory shares the destination filesystem. No output path is
    # exposed before all writes and flushes have succeeded. A crash can leave a
    # hidden staging directory, but never a partially published output package.
    with tempfile.TemporaryDirectory(prefix=".pockettopo-", dir=target.parent) as temporary:
        stage = Path(temporary) / "package"
        stage.mkdir()
        for name, content in files.items():
            with (stage / name).open("xb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        try:
            _rename_noreplace(stage, target)
        except AttributeError as error:
            raise OSError("Atomic no-replace rename is unavailable on this system") from error


def _finish_report(
    drawings, surveys, validation: dict, source: Path, settings: DrawingSettings
) -> dict:
    report = drawings.report
    for document in (drawings.source_document, report):
        document["provenance"].update(algorithm_version="p06-1", source_name=source.name)
    report["stage"] = "P06"
    report["settings"]["drawing_settings"] = asdict(settings)
    report["exports"]["validation"] = validation
    report["limitations"] = [
        item for item in report["limitations"] if not item.startswith("CLI, atomic package")
    ]
    report["limitations"].append(
        "Compilation uses Survex for both formats; it is not a runtime test in Walls. "
        "Completeness does not establish dates, repeats, CRS or historical correctness."
    )
    notices = sorted(
        {
            notice
            for artifact in report["drawings"]["artifacts"].values()
            for notice in artifact["overlay_notices"]
        }
    )
    report["completeness"].update(
        atomic_package_created=True,
        package_artifacts_complete=True,
        compilation_complete=validation["complete"],
        drawing_overlay_complete=not notices,
        conversion_complete=(
            surveys.report["completeness"]["measurement_export_complete"]
            and validation["complete"]
            and not notices
        ),
    )
    report["package"] = {
        "collision_policy": "error",
        "publication": "atomic_directory_rename_without_replacement",
        "drawing_notices": notices,
        "report_manifest_excludes_itself": True,
    }
    return report


def convert_package(
    source: Path,
    destination: Path,
    *,
    plan: ProcessingPlan | None = None,
    correction_policy: CorrectionPolicy | None = None,
    settings: DrawingSettings = DEFAULT_DRAWING_SETTINGS,
    resvg_path: str = "resvg",
    cavern: str = "cavern",
    dump3d: str = "dump3d",
    min_resultant: float = 1e-12,
) -> dict:
    """Publish all twelve artifacts or leave the target absent/unchanged.

    Compiler limitations still produce a full diagnostic package whose
    conversion_complete is false. Parser, renderer and filesystem errors raise
    before publication. Existing outputs have one policy: refuse, never replace.
    """
    target = _destination(destination)
    data = source.read_bytes()
    options = {"plan": plan, "correction_policy": correction_policy, "min_resultant": min_resultant}
    surveys = export_surveys(data, **options)
    drawings = export_drawings(data, **options, settings=settings, resvg_path=resvg_path)
    if set(drawings.svgs) != VARIANTS or set(drawings.pngs) != VARIANTS:
        raise ValueError("A package requires all four SVG and four PNG artifacts")
    validation = validate_surveys(surveys, cavern=cavern, dump3d=dump3d)
    report = _finish_report(drawings, surveys, validation, source, settings)
    files = {"survey.SRV": surveys.srv.encode("ascii"), "survey.svx": surveys.svx.encode("ascii")}
    files.update({name + ".svg": svg.encode("utf-8") for name, svg in drawings.svgs.items()})
    files.update({name + ".png": png for name, png in drawings.pngs.items()})
    files["source.json"] = json_bytes(drawings.source_document)
    report["package"]["artifacts"] = {
        name: {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
        for name, content in files.items()
    }
    files["conversion-report.json"] = json_bytes(report)
    _publish(target, files)
    return report
