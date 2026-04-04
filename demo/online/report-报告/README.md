# online / 报告

这是一个联网在线场景下的完整报告样例。

文件说明：

- [task.md](./task.md)：用户任务说明
- [materials.md](./materials.md)：可核实素材摘要
- [20260404-关于“我的刀盾”网络传播情况的报告-v01.md](./20260404-%E5%85%B3%E4%BA%8E%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E6%83%85%E5%86%B5%E7%9A%84%E6%8A%A5%E5%91%8A-v01.md)：最终 Markdown 成稿
- [20260404-关于“我的刀盾”网络传播情况的报告-v01.docx](./20260404-%E5%85%B3%E4%BA%8E%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E6%83%85%E5%86%B5%E7%9A%84%E6%8A%A5%E5%91%8A-v01.docx)：导出的 Word 文件

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/online/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.md \
  -o demo/online/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.docx \
  --doc-type 报告
```
