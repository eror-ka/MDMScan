# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- Базовые системные пакеты ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl wget gnupg lsb-release \
        git jq tar xz-utils file \
        clamav clamav-daemon clamav-freshclam \
    && rm -rf /var/lib/apt/lists/*

# ---------- Docker CLI (только клиент, без daemon) ----------
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg \
        | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
        > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get install -y --no-install-recommends docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# ---------- Trivy ----------
RUN curl -sSfL https://aquasecurity.github.io/trivy-repo/deb/public.key \
        | gpg --dearmor -o /usr/share/keyrings/trivy.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] \
https://aquasecurity.github.io/trivy-repo/deb generic main" \
        > /etc/apt/sources.list.d/trivy.list && \
    apt-get update && apt-get install -y --no-install-recommends trivy && \
    rm -rf /var/lib/apt/lists/*

# ---------- Grype (Anchore) ----------
RUN VERSION=$(curl -fsSL https://api.github.com/repos/anchore/grype/releases/latest \
        | jq -r '.tag_name | ltrimstr("v")') && \
    curl -fsSL -o /tmp/grype.tar.gz \
        "https://github.com/anchore/grype/releases/download/v${VERSION}/grype_${VERSION}_linux_amd64.tar.gz" && \
    tar -xzf /tmp/grype.tar.gz -C /usr/local/bin grype && \
    rm /tmp/grype.tar.gz

# ---------- Syft (Anchore) ----------
RUN VERSION=$(curl -fsSL https://api.github.com/repos/anchore/syft/releases/latest \
        | jq -r '.tag_name | ltrimstr("v")') && \
    curl -fsSL -o /tmp/syft.tar.gz \
        "https://github.com/anchore/syft/releases/download/v${VERSION}/syft_${VERSION}_linux_amd64.tar.gz" && \
    tar -xzf /tmp/syft.tar.gz -C /usr/local/bin syft && \
    rm /tmp/syft.tar.gz

# ---------- TruffleHog ----------
RUN curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh \
        | sh -s -- -b /usr/local/bin

# ---------- Cosign ----------
RUN curl -fsSL -o /usr/local/bin/cosign \
        "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64" && \
    chmod +x /usr/local/bin/cosign

# ---------- OSV-Scanner ----------
RUN curl -fsSL -o /usr/local/bin/osv-scanner \
        "https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd64" && \
    chmod +x /usr/local/bin/osv-scanner

# ---------- Dockle ----------
RUN VERSION=$(curl -fsSL https://api.github.com/repos/goodwithtech/dockle/releases/latest \
        | jq -r '.tag_name | ltrimstr("v")') && \
    curl -fsSL -o /tmp/dockle.tar.gz \
        "https://github.com/goodwithtech/dockle/releases/download/v${VERSION}/dockle_${VERSION}_Linux-64bit.tar.gz" && \
    tar -xzf /tmp/dockle.tar.gz -C /usr/local/bin dockle && \
    rm /tmp/dockle.tar.gz

# ---------- Dive ----------
RUN VERSION=$(curl -fsSL https://api.github.com/repos/wagoodman/dive/releases/latest \
        | jq -r '.tag_name | ltrimstr("v")') && \
    curl -fsSL -o /tmp/dive.tar.gz \
        "https://github.com/wagoodman/dive/releases/download/v${VERSION}/dive_${VERSION}_linux_amd64.tar.gz" && \
    tar -xzf /tmp/dive.tar.gz -C /usr/local/bin dive && \
    rm /tmp/dive.tar.gz

# ---------- Verify-script ----------
COPY scripts/verify-tools.sh /usr/local/bin/verify-tools
RUN chmod +x /usr/local/bin/verify-tools

WORKDIR /app

# Заглушка — на Этапе 3b заменим на запуск Celery-воркера.
CMD ["sleep", "infinity"]
