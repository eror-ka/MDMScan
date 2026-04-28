# Changelog

## v0.1.0 — 2026-04-28

Первый публичный релиз MDMScan.

### Добавлено

**Worker (Celery)**
- Параллельный запуск 7 сканеров через `ThreadPoolExecutor`: Trivy, Syft, Dockle, OSV-Scanner, Dive, TruffleHog, Cosign
- Нормализация и дедупликация находок по SHA1-fingerprint
- Вычисление оценки безопасности (0–100) с тиерными штрафами
- Загрузка сырых артефактов в MinIO (bucket `raw-scans`)
- `docker_pull` с fallback на локальный кэш при недоступности registry

**API (FastAPI)**
- `POST /scans` — отправка скана в очередь, немедленный ответ с `scan_id`
- `GET /scans/{id}` — статус + security_score + counts
- `GET /scans/{id}/findings` — фильтрация по severity и category, пагинация
- `DELETE /scans/{id}` — каскадное удаление из БД
- `/metrics` — Prometheus HTTP-метрики (prometheus-fastapi-instrumentator)

**Web UI (Next.js 14)**
- Форма запуска скана
- Авто-обновление статуса каждые 4 с
- Таблица находок с разбивкой по категориям

**Telegram-боты**
- Основной бот: `/scan`, `/status`, `/list`, `/help`, FSM для интерактивного ввода
- Mini-app бот: открытие веб-интерфейса кнопкой

**Очистка (Celery Beat)**
- `cleanup_orphan_temp` — каждый час: зависшие рабочие директории и сканы
- `cleanup_old_scans` — ежедневно: удаление старых сканов из БД + MinIO
- `prune_docker_images` — каждый час: `docker image prune -f`
- MinIO lifecycle policy (ILM) — автоматическое удаление объектов по сроку хранения

**Наблюдаемость**
- Структурированные JSON-логи через structlog
- Prometheus-метрики воркера: счётчики сканов, находок, тайминги сканеров
- Опциональный мониторинг-стек: Prometheus + Grafana + Loki + Promtail (`docker-compose.monitoring.yml`)

**Документация**
- [README](README.md) с архитектурной диаграммой (Mermaid) и quick-start
- [docs/api.md](docs/api.md) — описание всех REST-эндпоинтов
- [docs/report-format.md](docs/report-format.md) — схема Finding и manifest.json
- [docs/add-scanner.md](docs/add-scanner.md) — руководство по добавлению нового сканера

**CI/CD**
- GitHub Actions: lint (ruff) на push/PR в `main`
- GitHub Actions: `release.yml` — сборка образов, self-scan (dogfooding), публикация GitHub Release с отчётами
