#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FONT_DIR="${PROJECT_DIR}/assets/fonts"

mkdir -p "${FONT_DIR}"

PROFILE="${1:-minimal}"

download() {
  local url="$1"
  local output="$2"
  echo "[INFO] 下载 ${output}"
  curl -fsSL "${url}" -o "${FONT_DIR}/${output}"
}

download_noto_cjk_minimal() {
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/SubsetOTF/SC/NotoSerifSC-Bold.otf" "NotoSerifSC-Bold.otf"
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/SubsetOTF/SC/NotoSerifSC-Regular.otf" "NotoSerifSC-Regular.otf"
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/SC/NotoSansSC-Bold.otf" "NotoSansSC-Bold.otf"
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf" "NotoSansSC-Regular.otf"
}

download_noto_cjk_all() {
  download_noto_cjk_minimal
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Serif/SubsetOTF/SC/NotoSerifSC-Medium.otf" "NotoSerifSC-Medium.otf"
  download "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/SC/NotoSansSC-Medium.otf" "NotoSansSC-Medium.otf"
}

download_fandol_minimal() {
  download "https://tug.ctan.org/fonts/fandol/FandolFang-Regular.otf" "FandolFang-Regular.otf"
  download "https://tug.ctan.org/fonts/fandol/FandolSong-Regular.otf" "FandolSong-Regular.otf"
}

download_fandol_all() {
  download_fandol_minimal
  download "https://tug.ctan.org/fonts/fandol/FandolHei-Regular.otf" "FandolHei-Regular.otf"
  download "https://tug.ctan.org/fonts/fandol/FandolHei-Bold.otf" "FandolHei-Bold.otf"
  download "https://tug.ctan.org/fonts/fandol/FandolSong-Bold.otf" "FandolSong-Bold.otf"
}

case "${PROFILE}" in
  minimal)
    download_noto_cjk_minimal
    download_fandol_minimal
    ;;
  all)
    download_noto_cjk_all
    download_fandol_all
    ;;
  noto-cjk)
    download_noto_cjk_all
    ;;
  fandol)
    download_fandol_all
    ;;
  *)
    echo "[ERROR] 不支持的下载配置：${PROFILE}"
    echo "可选值：minimal | all | noto-cjk | fandol"
    exit 1
    ;;
esac

echo "[OK] 字体已下载到 ${FONT_DIR}"
echo "[INFO] 下一步可运行：bash scripts/install_fonts.sh"
