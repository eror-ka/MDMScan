# Формат отчёта

MDMScan хранит два вида данных: **структурированные находки** в PostgreSQL и
**сырые артефакты** (JSON/NDJSON-вывод сканеров) в MinIO.

---

## manifest.json (MinIO)

После завершения скана в MinIO по ключу `{scan_id}/manifest.json` записывается сводка:

```json
{
  "scan_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "image": "nginx:latest",
  "findings_count": 42,
  "severity_counts": {
    "CRITICAL": 2,
    "HIGH": 15,
    "MEDIUM": 20,
    "LOW": 5
  },
  "scanner_statuses": {
    "trivy": "ok",
    "syft": "ok",
    "dockle": "ok",
    "osv-scanner": "ok",
    "dive": "ok",
    "trufflehog": "ok",
    "cosign": "error"
  }
}
```

**Статусы сканеров:**
- `ok` — выполнен успешно
- `error` — завершён с ошибкой (например, cosign без подписи)
- `timeout` — превышен `SCAN_TIMEOUT_SECONDS`

---

## Артефакты сканеров (MinIO)

Все файлы хранятся под префиксом `raw-scans/{scan_id}/`:

| Файл | Сканер | Формат |
|------|--------|--------|
| `trivy.json` | Trivy | JSON (официальная схема Trivy) |
| `syft.spdx.json` | Syft | SPDX JSON (SBOM) |
| `dockle.json` | Dockle | JSON |
| `osv.json` | OSV-Scanner | JSON |
| `dive.json` | Dive | JSON |
| `trufflehog.ndjson` | TruffleHog | NDJSON (по одному объекту на строку) |
| `cosign.txt` | Cosign | Plaintext (`cosign tree` output) |
| `manifest.json` | MDMScan | Сводка (см. выше) |

Файлы удаляются через `SCAN_RETENTION_DAYS` дней — автоматически MinIO lifecycle policy.

---

## Finding (PostgreSQL)

Таблица `findings`. Дедупликация по fingerprint = SHA1(`category|raw_ref|package|version|location`).

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | int | PK |
| `scan_job_id` | UUID | Внешний ключ на `scan_jobs` |
| `fingerprint` | string | SHA1-отпечаток для дедупликации |
| `category` | string | `vuln` / `misconfig` / `secret` / `hygiene` / `supply_chain` |
| `severity` | string | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `UNKNOWN` |
| `title` | string | Краткое название (CVE-ID, название правила и т.д.) |
| `description` | string? | Расширенное описание |
| `package` | string? | Имя пакета / компонента |
| `version` | string? | Установленная версия |
| `fix_version` | string? | Версия с исправлением |
| `location` | string? | Путь к файлу / слою |
| `raw_ref` | string | Исходная ссылка из сканера (CVE-ID, rule-id и т.д.) |
| `sources` | JSON array | Какие сканеры нашли эту находку |
| `fix_advice` | string? | Рекомендация по устранению |

### Категории

| Категория | Примеры источников |
|-----------|-------------------|
| `vuln` | Trivy, OSV-Scanner |
| `misconfig` | Dockle, Trivy |
| `secret` | TruffleHog, Trivy |
| `hygiene` | Dive, Syft |
| `supply_chain` | Cosign |

### Severity

Стандартизирован до: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.

---

## ScanJob (PostgreSQL)

Таблица `scan_jobs`:

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | UUID | PK |
| `image_ref` | string | Образ (`nginx:latest`, `ghcr.io/...`) |
| `status` | string | `pending` / `running` / `done` / `failed` |
| `created_at` | datetime | Время постановки в очередь |
| `finished_at` | datetime? | Время завершения |
| `scanner_statuses` | JSONB | `{scanner: "ok|error|timeout"}` |
| `security_score` | int? | 0–100, NULL пока не завершён |

---

## Формула оценки безопасности

```
score = 100 − penalty_vuln − penalty_misconfig − penalty_secret − penalty_hygiene
```

Ограничения:
- При отсутствии CRITICAL-уязвимостей: `score = max(score, 75)`
- Минимальный штраф при наличии любых находок: 1 балл
- Итоговое значение: `max(0, round(score))`
