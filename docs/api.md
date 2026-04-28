# REST API

Базовый URL: `http://localhost:8000`

Интерактивная документация (Swagger UI): `http://localhost:8000/docs`

OpenAPI-схема (JSON): `http://localhost:8000/openapi.json`

---

## Эндпоинты

### `GET /health`

Liveness-проба.

**Ответ `200`**
```json
{ "status": "ok" }
```

---

### `GET /scans`

Список сканов, сортировка по дате создания (новые первые).

**Query-параметры**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `limit` | int (1–100) | `20` | Количество записей |
| `offset` | int (≥0) | `0` | Смещение |

**Ответ `200`** — массив объектов `ScanListItem`:
```json
[
  {
    "scan_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "image_ref": "nginx:latest",
    "status": "done",
    "created_at": "2026-04-28T10:00:00Z",
    "finished_at": "2026-04-28T10:02:37Z",
    "findings_count": 42,
    "security_score": 81
  }
]
```

---

### `POST /scans`

Запустить скан образа. Создаёт `ScanJob` со статусом `pending`, немедленно ставит
задачу в очередь Celery.

**Тело запроса**
```json
{ "image": "nginx:latest" }
```

**Ответ `202`**
```json
{
  "scan_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending"
}
```

---

### `GET /scans/{scan_id}`

Состояние скана, счётчик находок, оценка безопасности.

**Статусы скана:**

| Статус | Описание |
|--------|----------|
| `pending` | В очереди, ещё не начат |
| `running` | Сканирование выполняется |
| `done` | Завершён успешно |
| `failed` | Завершён с ошибкой |

**Ответ `200`**
```json
{
  "scan_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "image_ref": "nginx:latest",
  "status": "done",
  "created_at": "2026-04-28T10:00:00Z",
  "finished_at": "2026-04-28T10:02:37Z",
  "scanner_statuses": {
    "trivy": "ok",
    "syft": "ok",
    "dockle": "ok",
    "osv-scanner": "ok",
    "dive": "ok",
    "trufflehog": "ok",
    "cosign": "error"
  },
  "findings_count": 42,
  "security_score": 81
}
```

**Ответ `404`** — скан не найден.

---

### `DELETE /scans/{scan_id}`

Удалить скан из базы данных (каскадно: findings + artifacts). Файлы в MinIO
**не удаляются** (очищаются lifecycle policy или задачей `cleanup_old_scans`).

**Ответ `204`** — удалён.
**Ответ `404`** — не найден.

---

### `GET /scans/{scan_id}/findings`

Список находок для скана с фильтрацией и пагинацией.

**Query-параметры**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `severity` | string | Фильтр: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN` |
| `category` | string | Фильтр: `vuln`, `misconfig`, `secret`, `hygiene`, `supply_chain` |
| `limit` | int (1–500) | По умолчанию `100` |
| `offset` | int | По умолчанию `0` |

**Ответ `200`**
```json
{
  "scan_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "total": 42,
  "items": [
    {
      "id": 1,
      "fingerprint": "a1b2c3...",
      "category": "vuln",
      "severity": "HIGH",
      "title": "CVE-2024-12345",
      "description": "Buffer overflow in libssl",
      "package": "openssl",
      "version": "3.0.2",
      "fix_version": "3.0.14",
      "location": "/usr/lib/x86_64-linux-gnu/libssl.so.3",
      "raw_ref": "CVE-2024-12345",
      "sources": ["trivy", "osv-scanner"],
      "fix_advice": "Обновите openssl до версии 3.0.14"
    }
  ]
}
```

---

## Prometheus-метрики

`GET /metrics` — метрики HTTP-запросов (prometheus-fastapi-instrumentator):
- `http_requests_total{method,handler,status_code}`
- `http_request_duration_seconds{method,handler}`

Метрики воркера (сканы, тайминги сканеров) — `http://localhost:9090` (beat-контейнер).
