# 页码自第二页起 实施计划

> **历史计划（已完成）。** 本文件是 2026-04-04 的实施计划记录，相关改动已落地。复选框标记为已完成 `[x]`，仅作过程留档。
> 面向执行者：可配合 superpowers:subagent-driven-development 或 superpowers:executing-plans 按任务逐项推进；步骤用复选框（`- [ ]`）跟踪。

**目标：** 调整导出的 `.docx` 页码，使首页页脚不显示页码，第二页显示页码 `2`。

**架构：** 保留当前单页脚设计，仅更新节属性，让 Word 把首页视为独立的无页脚页；默认页脚继续附着于后续页面，页码字段继续沿用节的页码编号。

**技术栈：** 基于 ZIP 的 DOCX XML 生成（Python）、unittest。

---

### 任务一：为首页抑制补失败测试

**文件：**
- 修改：`tests/test_generate_docx.py`
- 修改：`scripts/generate_docx.py`

- [x] **步骤 1：新增测试，构造 `show_page_number=True` 的文档并断言节 XML 含 `w:titlePg`**

- [x] **步骤 2：运行 docx 单测，确认实现前新测试失败**

执行：`python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

预期：失败，因为生成的节 XML 尚未包含首页抑制。

### 任务二：实现最小的 DOCX 节属性改动

**文件：**
- 修改：`scripts/generate_docx.py`

- [x] **步骤 1：更新节属性，使 `show_page_number=True` 时加入 `w:titlePg`，并对后续页保留默认页脚**

- [x] **步骤 2：显式保留该节的正常页码编号语义**

- [x] **步骤 3：重跑测试**

执行：`python3 -m unittest discover -s tests -p 'test_generate_docx.py'`

预期：全部测试通过。

### 任务三：重建与核对

**文件：**
- 修改：仅在烟雾检查需要时改动生成产物

- [x] **步骤 1：重跑构建烟雾检查**

执行：`python3 scripts/build_all.py`

预期：构建成功。

- [x] **步骤 2：重跑最终 diff 卫生检查**

执行：`git diff --check`

预期：无空白错误。
