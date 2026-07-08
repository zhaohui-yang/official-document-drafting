"""pytest 根配置：把 src/ 加入导入路径。

代码统一放在 src/ 下（src/adapters、src/scripts、src/renderers、src/docgen）。测试仍以
`from adapters.shared import ...`、`from scripts.check_sections import ...` 的形式导入，
因此把 src/ 插入 sys.path，使这些顶层包可被解析。
"""

import pathlib
import sys

SRC_DIR = pathlib.Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
