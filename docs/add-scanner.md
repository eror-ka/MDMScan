# Как добавить новый сканер

Добавление нового сканера занимает четыре шага:
установка бинаря в Dockerfile, описание команды в `scanners.py`,
парсер в `parsers/`, регистрация парсера в `tasks.py`.

---

## 1. Установить бинарь в Dockerfile

Добавить секцию в [services/worker/Dockerfile](../services/worker/Dockerfile)
по образцу существующих сканеров:

```dockerfile
# ---------- MyScanner ----------
RUN curl -fsSL -o /usr/local/bin/myscanner \
        "https://github.com/vendor/myscanner/releases/latest/download/myscanner-linux-amd64" && \
    chmod +x /usr/local/bin/myscanner
```

---

## 2. Описать команду в `scanners.py`

Открыть [services/worker/app/scanners.py](../services/worker/app/scanners.py).

Добавить функцию-строитель команды:

```python
def _myscanner(image: str, workdir: Path) -> tuple[list[str], str]:
    out = "myscanner.json"
    cmd = ["myscanner", "scan", "--format", "json", "--output", str(workdir / out), image]
    return cmd, out
```

Добавить `ScannerSpec` в список `SCANNERS`:

```python
SCANNERS: list[ScannerSpec] = [
    ...
    ScannerSpec("myscanner", _myscanner),
    # Если сканер пишет в stdout (не в файл):
    # ScannerSpec("myscanner", _myscanner, capture_stdout_to_file=True),
]
```

**`capture_stdout_to_file=True`** — нужен когда сканер выводит результаты в `stdout`,
а не в файл (как TruffleHog и Cosign). Тогда `run_one()` сам перенаправит stdout в файл.

---

## 3. Написать парсер

Создать [services/worker/app/parsers/myscanner.py](../services/worker/app/parsers/):

```python
from __future__ import annotations

import json
from pathlib import Path

from app.parsers.base import Finding


def parse(path: Path) -> list[Finding]:
    """Парсит вывод myscanner и возвращает нормализованные Finding."""
    data = json.loads(path.read_text())
    findings: list[Finding] = []

    for item in data.get("results", []):
        findings.append(
            Finding(
                category="vuln",          # vuln | misconfig | secret | hygiene | supply_chain
                severity=_map_severity(item.get("severity", "UNKNOWN")),
                title=item["id"],
                description=item.get("description"),
                package=item.get("package"),
                version=item.get("version"),
                fix_version=item.get("fix_version"),
                location=item.get("path"),
                raw_ref=item["id"],
                sources=["myscanner"],
                fix_advice=item.get("recommendation"),
            )
        )

    return findings


def _map_severity(raw: str) -> str:
    mapping = {
        "critical": "CRITICAL",
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
    }
    return mapping.get(raw.lower(), "UNKNOWN")
```

**Требования к парсеру:**
- Принимает `Path` к файлу.
- Возвращает `list[Finding]` (из `app.parsers.base`).
- Не бросает исключений при пустом/неожиданном файле — пусть возвращает `[]`.
- `fingerprint` вычисляется автоматически в `Finding.__post_init__`.

Поля `Finding`:

| Поле | Обязательное | Описание |
|------|:-----------:|----------|
| `category` | Да | `vuln` / `misconfig` / `secret` / `hygiene` / `supply_chain` |
| `severity` | Да | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `UNKNOWN` |
| `title` | Да | Краткое название |
| `raw_ref` | Да | Исходный идентификатор из сканера |
| `sources` | Да | Список сканеров (`["myscanner"]`) |
| `description` | Нет | Расширенное описание |
| `package` | Нет | Имя пакета |
| `version` | Нет | Установленная версия |
| `fix_version` | Нет | Версия с исправлением |
| `location` | Нет | Путь к файлу / слою |
| `fix_advice` | Нет | Рекомендация |

---

## 4. Зарегистрировать парсер в `tasks.py`

Открыть [services/worker/app/tasks.py](../services/worker/app/tasks.py).

Импортировать парсер:
```python
from app.parsers import myscanner
```

Добавить запись в словарь `_PARSERS`:
```python
_PARSERS: dict[str, tuple] = {
    ...
    "myscanner": (myscanner.parse, "myscanner.json"),
}
```

Имя ключа должно совпадать с `ScannerSpec.name` из шага 2.

---

## 5. Пересобрать и проверить

```bash
docker compose up -d --build worker beat
docker compose exec worker celery -A app.tasks call mdmscan.scan_image --args '["alpine:latest"]'
docker compose logs -f worker
```

В логах должно появиться:
```json
{"event": "scanner.done", "scanner": "myscanner", "status": "ok", ...}
```

А через API:
```bash
curl http://localhost:8000/scans/{scan_id}/findings?category=vuln
```
