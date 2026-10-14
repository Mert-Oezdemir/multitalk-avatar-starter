#!/usr/bin/env bash
set -Eeuo pipefail
# Requires GitHub CLI authentication. Creates a NEW public repository only.
# Usage: bash scripts/publish_github.sh [repo-name]
NAME="${1:-multitalk-avatar-starter}"
if [[ ! "$NAME" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo 'Gecersiz repo adi.' >&2; exit 1
fi
if ! command -v gh >/dev/null || ! command -v git >/dev/null; then
  echo 'Git ve GitHub CLI (gh) gerekli: https://cli.github.com/' >&2; exit 1
fi
gh auth status >/dev/null || { echo 'Once gh auth login ile GitHub oturumu acin.' >&2; exit 1; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [ -e .git ]; then
  echo 'Bu dizinde zaten .git var. Var olan Git gecmisini degistirmiyorum.' >&2; exit 1
fi
USER="$(gh api user --jq .login)"
if gh repo view "$USER/$NAME" >/dev/null 2>&1; then
  echo "Hedef depo zaten var: $USER/$NAME. Var olan depoya yazmiyorum." >&2; exit 1
fi
if find . -maxdepth 1 -type f \( -name '*.safetensors' -o -name '*.mp4' -o -name '*.wav' \) | grep -q .; then
  echo 'Model veya medya dosyalari var. Push iptal.' >&2; exit 1
fi
git init -b main
git add README.md LICENSE .gitignore avatar_kit.py docs scripts tests .github
git commit -m 'Initial MIT-licensed MultiTalk avatar starter kit'
gh repo create "$USER/$NAME" --public --source . --remote origin --push --description 'Independent Turkish starter kit for MultiTalk and ComfyUI (no model weights)'
echo "Depo yayinda: https://github.com/$USER/$NAME"
