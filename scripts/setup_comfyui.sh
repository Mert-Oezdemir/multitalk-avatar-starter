#!/usr/bin/env bash
set -Eeuo pipefail

# Clones upstream projects as independent repositories; never vendors their code.
ROOT="${1:-$HOME/multitalk-env}"
mkdir -p "$ROOT"
ROOT="$(cd "$ROOT" && pwd)"
if ! command -v git >/dev/null || ! command -v python3 >/dev/null; then
  echo 'Git ve Python 3 gerekli.' >&2; exit 1
fi
if [ ! -d "$ROOT/ComfyUI/.git" ]; then
  if [ -e "$ROOT/ComfyUI" ]; then echo 'Mevcut ComfyUI dizini Git deposu degil.' >&2; exit 1; fi
  git clone https://github.com/Comfy-Org/ComfyUI.git "$ROOT/ComfyUI"
fi
WRAPPER="$ROOT/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper"
mkdir -p "$ROOT/ComfyUI/custom_nodes"
if [ ! -d "$WRAPPER/.git" ]; then
  if [ -e "$WRAPPER" ]; then echo 'Mevcut wrapper dizini Git deposu degil.' >&2; exit 1; fi
  git clone https://github.com/kijai/ComfyUI-WanVideoWrapper.git "$WRAPPER"
fi
if [ ! -d "$ROOT/ComfyUI/.venv" ]; then python3 -m venv "$ROOT/ComfyUI/.venv"; fi
PYTHON="$ROOT/ComfyUI/.venv/bin/python"
"$PYTHON" -m pip install -r "$ROOT/ComfyUI/requirements.txt"
"$PYTHON" -m pip install -r "$WRAPPER/requirements.txt"
echo "Hazirlanan yerel ortam: $ROOT/ComfyUI"
echo 'GPU surucusu/PyTorch uyumlulugu ve modeller icin docs/LOCAL.md oku.'
echo "Baslat: cd '$ROOT/ComfyUI' && .venv/bin/python main.py"
