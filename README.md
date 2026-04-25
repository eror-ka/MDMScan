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

```bash
git clone git@github.com:eror-ka/MDMScan.git
cd MDMScan
cp .env.example .env
# отредактируй .env, замени все CHANGE_ME на сгенерированные пароли:
#   openssl rand -base64 24
docker compose pull
docker compose up -d
```

После запуска должны быть подняты:
- **PostgreSQL** на `127.0.0.1:5432` (логин/БД из `.env`)
- **MinIO** API на `127.0.0.1:9000`, Console на `127.0.0.1:9001` (бакеты создаются автоматически: `raw-scans`, `reports`, `sboms`, `temp`)
- **Redis** на `127.0.0.1:6379`

Все порты прибиты к `127.0.0.1`, доступа из внешней сети нет — это намеренно. Для доступа к MinIO Console с другой машины используй SSH-туннель

## Разработка

```bash
pre-commit install
pre-commit run --all-files
```

## Лицензия

MIT
