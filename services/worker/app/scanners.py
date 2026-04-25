"""Описание сканеров и их запуск.

Каждый сканер запускается отдельным subprocess с таймаутом.
Результат — словарь с stdout/stderr/exit_code. Падения сканеров
не валят всю задачу: пишем status='error' и едем дальше.
"""

from __future__ import annotations

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import structlog

from app.config import settings

log = structlog.get_logger()


@dataclass
class ScannerResult:
    name: str
    status: str  # "ok" | "error" | "timeout"
    exit_code: int | None
    duration_s: float
    output_path: Path | None  # путь к сохранённому JSON
    stderr_tail: str = ""  # последние 2000 символов stderr — для отладки


@dataclass
class ScannerSpec:
    name: str
    # функция, принимающая (image_ref, workdir) и возвращающая (cmd, output_filename)
    build_cmd: Callable[[str, Path], tuple[list[str], str]]
    # некоторые сканеры пишут в stdout, некоторые сразу в файл
    capture_stdout_to_file: bool = False
    extra_env: dict[str, str] = field(default_factory=dict)


# ---------- Команды конкретных сканеров ----------


def _trivy(image: str, workdir: Path) -> tuple[list[str], str]:
    out = "trivy.json"
    cmd = [
        "trivy",
        "image",
        "--format",
        "json",
        "--output",
        str(workdir / out),
        "--scanners",
        "vuln,misconfig,secret,license",
        "--quiet",
        image,
    ]
    return cmd, out


def _syft(image: str, workdir: Path) -> tuple[list[str], str]:
    out = "syft.spdx.json"
    cmd = ["syft", image, "-o", f"spdx-json={workdir / out}"]
    return cmd, out


def _dockle(image: str, workdir: Path) -> tuple[list[str], str]:
    out = "dockle.json"
    cmd = [
        "dockle",
        "--format",
        "json",
        "--output",
        str(workdir / out),
        "--exit-code",
        "0",  # не падать на findings, нам нужен JSON
        image,
    ]
    return cmd, out


def _osv(image: str, workdir: Path) -> tuple[list[str], str]:
    # OSV-Scanner v2: команда переехала на `scan image <ref>`,
    # старый флаг --docker удалён. Использует docker save под капотом.
    out = "osv.json"
    cmd = [
        "osv-scanner",
        "scan",
        "image",
        "--format",
        "json",
        "--output",
        str(workdir / out),
        image,
    ]
    return cmd, out


def _dive(image: str, workdir: Path) -> tuple[list[str], str]:
    out = "dive.json"
    cmd = [
        "dive",
        image,
        "--ci",
        "--json",
        str(workdir / out),
    ]
    return cmd, out


def _trufflehog(image: str, workdir: Path) -> tuple[list[str], str]:
    # trufflehog пишет в stdout NDJSON, перенаправляем в файл сами
    out = "trufflehog.ndjson"
    cmd = ["trufflehog", "docker", "--image", image, "--json", "--no-update"]
    return cmd, out


def _cosign(image: str, workdir: Path) -> tuple[list[str], str]:
    # Cosign verify — без публичного ключа упадёт, это ожидаемо.
    # Используем "tree" чтобы посмотреть подписи/attestations.
    out = "cosign.txt"
    cmd = ["cosign", "tree", image]
    return cmd, out


SCANNERS: list[ScannerSpec] = [
    ScannerSpec("trivy", _trivy),
    ScannerSpec("syft", _syft),
    ScannerSpec("dockle", _dockle),
    ScannerSpec("osv-scanner", _osv),
    ScannerSpec("dive", _dive),
    ScannerSpec("trufflehog", _trufflehog, capture_stdout_to_file=True),
    ScannerSpec("cosign", _cosign, capture_stdout_to_file=True),
]


# ---------- Подготовка: pull + распаковка для ClamAV ----------


def docker_pull(image: str) -> None:
    log.info("docker.pull", image=image)
    subprocess.run(["docker", "pull", image], check=True, timeout=600)


# ---------- Запуск одного сканера ----------


def run_one(spec: ScannerSpec, image: str, workdir: Path) -> ScannerResult:
    cmd, out_filename = spec.build_cmd(image, workdir)
    out_path = workdir / out_filename
    started = time.monotonic()
    log.info("scanner.start", scanner=spec.name, cmd=cmd)

    try:
        proc = subprocess.run(
            cmd,
            timeout=settings.scan_timeout_seconds,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired as e:
        log.warning(
            "scanner.timeout", scanner=spec.name, timeout=settings.scan_timeout_seconds
        )
        return ScannerResult(
            name=spec.name,
            status="timeout",
            exit_code=None,
            duration_s=time.monotonic() - started,
            output_path=None,
            stderr_tail=str(e)[-2000:],
        )
    except FileNotFoundError as e:
        log.error("scanner.missing", scanner=spec.name, err=str(e))
        return ScannerResult(
            name=spec.name,
            status="error",
            exit_code=None,
            duration_s=time.monotonic() - started,
            output_path=None,
            stderr_tail=str(e)[-2000:],
        )

    duration = time.monotonic() - started

    if spec.capture_stdout_to_file:
        out_path.write_text(proc.stdout or "")

    # Логика статуса:
    # - exit_code == 0 → сканер успешно отработал, даже если ничего не нашёл (пустой файл — норма)
    # - exit_code != 0, но файл создан и непустой → typical "найдены findings" (Trivy/Grype с CVE)
    # - exit_code != 0 и нет файла/он пустой → реальная ошибка
    if proc.returncode == 0:
        status = "ok"
    elif out_path.exists() and out_path.stat().st_size > 0:
        status = "ok"
    else:
        status = "error"
    log.info(
        "scanner.done",
        scanner=spec.name,
        status=status,
        exit_code=proc.returncode,
        duration_s=round(duration, 2),
    )
    return ScannerResult(
        name=spec.name,
        status=status,
        exit_code=proc.returncode,
        duration_s=duration,
        output_path=out_path if status == "ok" else None,
        stderr_tail=(proc.stderr or "")[-2000:],
    )


# ---------- Запуск всех сканеров ----------


def run_all(image: str, workdir: Path) -> list[ScannerResult]:
    """Подготовить образ и параллельно прогнать все сканеры."""
    workdir.mkdir(parents=True, exist_ok=True)

    # 1. pull
    docker_pull(image)

    # 2. параллельно прогоняем сканеры (по одному на CPU, не больше 4 одновременно)
    results: list[ScannerResult] = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(run_one, s, image, workdir): s for s in SCANNERS}
        for fut in as_completed(futures):
            results.append(fut.result())

    return results
