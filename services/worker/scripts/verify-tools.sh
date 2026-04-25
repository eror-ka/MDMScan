#!/usr/bin/env bash
set -euo pipefail

# Все CLI должны отвечать на свою version-команду без ошибок.
# Если хотя бы одна не отрабатывает — выходим с ненулевым кодом.

declare -a checks=(
    "docker --version"
    "trivy --version"
    "grype version"
    "syft version"
    "dockle --version"
    "osv-scanner --version"
    "dive --version"
    "trufflehog --version"
    "clamscan --version"
    "cosign version"
)

echo "=== Verifying scanner tools ==="
fail=0
for cmd in "${checks[@]}"; do
    printf -- "--- %s\n" "$cmd"
    if ! eval "$cmd" 2>&1; then
        echo "!!! FAILED: $cmd"
        fail=1
    fi
    echo
done

if [[ $fail -ne 0 ]]; then
    echo "=== Some tools failed verification ==="
    exit 1
fi
echo "=== All tools OK ==="
