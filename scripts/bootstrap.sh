#!/usr/bin/env bash
set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.12}"

if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: uv is required."
    echo
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo
    echo "Then restart your shell or run:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    exit 1
fi

echo "Using Python ${PYTHON_VERSION}"

uv python install "${PYTHON_VERSION}"

# Recreate the environment if it is using the wrong Python version.
if [[ -d ".venv" ]]; then
    CURRENT_VERSION=$(
        .venv/bin/python -c \
        'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' \
        2>/dev/null || echo "unknown"
    )

    if [[ "${CURRENT_VERSION}" != "${PYTHON_VERSION}" ]]; then
        echo "Existing .venv uses Python ${CURRENT_VERSION}; recreating it."
        rm -rf .venv
    fi
fi

if [[ ! -d ".venv" ]]; then
    uv venv --python "${PYTHON_VERSION}" .venv
fi

source .venv/bin/activate

echo
echo "Python:"
python --version

echo
echo "Installing project dependencies..."
uv pip install -e ".[dev]"

echo
echo "Running tests..."
pytest

echo
echo "Running demo..."
mkdir -p out

autonomous-dataops run \
    examples/sample_input.json \
    --output out/result.json

echo
echo "============================================"
echo "Bootstrap complete."
echo "============================================"
echo
echo "Virtual environment:"
echo "  $(python --version)"
echo
echo "Demo output:"
echo "  out/result.json"
echo
echo "Next:"
echo "  source .venv/bin/activate"
echo "  codex"
echo
echo "Have Codex read:"
echo "  SKILL.md"
echo "  AGENTS.md"
echo
