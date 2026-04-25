# MDMScan

Автоматизированная система оценки безопасности Docker-образов.
Запускает набор open-source сканеров (Trivy, Grype, Syft, Dockle, OSV-Scanner,
Dive, TruffleHog, ClamAV, Cosign), нормализует и дедуплицирует находки,
складывает в Postgres + MinIO, отдаёт через REST API, web UI и Telegram-бота.

## Статус

🚧 В разработке. Сейчас завершён **Этап 1** (скелет репозитория + CI).

## Стек

- **API:** FastAPI (Python 3.12)
- **Worker:** Celery + Redis
- **Web UI:** Next.js + Tailwind
- **Bot:** aiogram 3
- **БД:** PostgreSQL 16
- **Хранилище артефактов:** MinIO (S3-compatible)
- **Reverse-proxy:** Traefik

## Локальный запуск

Сервисы будут добавлены начиная с Этапа 2. Пока:

```bash
git clone git@github.com:eror-ka/MDMScan.git
cd MDMScan
cp .env.example .env
docker compose up -d
```

## Разработка

```bash
pre-commit install
pre-commit run --all-files
```

## Лицензия

MIT
