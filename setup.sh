#!/bin/bash
# Forge setup.sh
# Creates the Python virtual environment and installs dependencies.
# Run once after copying forge/ to your machine.
# Usage: bash setup.sh

set -e

FORGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$FORGE_DIR/.venv"

echo ""
echo "┌─────────────────────────────────────────────────────┐"
echo "│  Forge Setup                                         │"
echo "└─────────────────────────────────────────────────────┘"
echo ""

# Check Python 3.10+
PYTHON=$(command -v python3 || true)
if [ -z "$PYTHON" ]; then
    echo "[setup] ERROR: python3 not found. Install Python 3.10 or higher."
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || ([ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]); then
    echo "[setup] ERROR: Python 3.10+ required. Found: $PY_VERSION"
    exit 1
fi

echo "[setup] Python $PY_VERSION found at $PYTHON"

# Check Ollama is running
if ! curl -s http://127.0.0.1:11434/api/version > /dev/null 2>&1; then
    echo "[setup] WARNING: Ollama does not appear to be running at http://127.0.0.1:11434"
    echo "[setup] Start it with: systemctl start ollama"
    echo "[setup] Continuing setup — Ollama must be running before you start Forge."
else
    echo "[setup] Ollama is running."
fi

# Check qwen3:8b is available
MODELS=$(curl -s http://127.0.0.1:11434/api/tags 2>/dev/null || echo "")
if echo "$MODELS" | grep -q "qwen3:8b"; then
    echo "[setup] qwen3:8b is available."
else
    echo "[setup] WARNING: qwen3:8b not found in Ollama. Pull it with:"
    echo "        ollama pull qwen3:8b"
fi

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "[setup] Virtual environment already exists at $VENV_DIR"
else
    echo "[setup] Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    echo "[setup] Virtual environment created."
fi

# Activate and install
echo "[setup] Installing dependencies..."
"$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
"$VENV_DIR/bin/python" -m pip install --quiet -r "$FORGE_DIR/requirements.txt"
echo "[setup] Dependencies installed."

# Make main.py executable
chmod +x "$FORGE_DIR/main.py"

# Verify structure
echo ""
echo "[setup] Verifying directory structure..."
REQUIRED_DIRS=(
    "agents/forge"
    "config"
    "logs"
    "memory"
)
REQUIRED_FILES=(
    "agents/forge/agent.py"
    "agents/forge/tools.py"
    "agents/forge/permissions.py"
    "agents/forge/context_builder.py"
    "agents/forge/memory.py"
    "config/approved_paths.json"
    "config/blocked_paths.json"
    "config/filetype_policy.json"
    "config/tool_registry.json"
    "config/session_scope.json"
    "logs/forge_audit.log"
    "logs/forge_error.log"
    "memory/user_profile.json"
    "memory/project_profile.json"
    "memory/known_errors.json"
    "memory/rollback_registry.json"
    "memory/forge_kb_manifest.json"
    "main.py"
)

ALL_OK=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$FORGE_DIR/$dir" ]; then
        echo "[setup] MISSING DIR: $dir"
        ALL_OK=false
    fi
done
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$FORGE_DIR/$file" ]; then
        echo "[setup] MISSING FILE: $file"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = true ]; then
    echo "[setup] All files and directories present."
fi

echo ""
echo "┌─────────────────────────────────────────────────────┐"
echo "│  Setup complete.                                     │"
echo "│                                                      │"
echo "│  To start Forge:                                     │"
echo "│    source .venv/bin/activate                         │"
echo "│    python main.py                                    │"
echo "│                                                      │"
echo "│  To approve a project path first:                    │"
echo "│    python main.py approve ~/your/project             │"
echo "│                                                      │"
echo "│  To check status:                                    │"
echo "│    python main.py status                             │"
echo "└─────────────────────────────────────────────────────┘"
echo ""
