#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FONT_DIR="${PROJECT_DIR}/assets/fonts"
TARGET_DIR="${HOME}/.local/share/fonts/official-document-drafting"

shopt -s nullglob
fonts=(
  "${FONT_DIR}"/*.ttf
  "${FONT_DIR}"/*.TTF
  "${FONT_DIR}"/*.otf
  "${FONT_DIR}"/*.OTF
  "${FONT_DIR}"/*.ttc
  "${FONT_DIR}"/*.TTC
)

if [ ${#fonts[@]} -eq 0 ]; then
  echo "[ERROR] 未在 ${FONT_DIR} 中找到字体文件。"
  echo "请先把 .ttf / .otf / .ttc 文件放到 assets/fonts/。"
  exit 1
fi

mkdir -p "${TARGET_DIR}"
cp "${fonts[@]}" "${TARGET_DIR}/"

echo "[OK] 已复制 ${#fonts[@]} 个字体文件到 ${TARGET_DIR}"

if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "${TARGET_DIR}" >/dev/null 2>&1 || true
  echo "[OK] 已尝试刷新字体缓存"
else
  echo "[WARN] 未找到 fc-cache，请在系统中手动刷新字体缓存"
fi

echo
echo "推荐的 Word 导出命令："
echo "python3 scripts/generate_docx.py demo/output-notice.md -o demo/output-notice.docx --font-preset noto-cjk"
