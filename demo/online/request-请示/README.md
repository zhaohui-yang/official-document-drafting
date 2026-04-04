# online / 请示

这是一个联网在线场景下的完整请示样例。

文件说明：

- [task.md](./task.md)：用户任务说明
- [materials.md](./materials.md)：可核实素材摘要
- [20260404-关于申请开展“我的刀盾”传播案例梳理工作的请示-v01.md](./20260404-%E5%85%B3%E4%BA%8E%E7%94%B3%E8%AF%B7%E5%BC%80%E5%B1%95%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E4%BC%A0%E6%92%AD%E6%A1%88%E4%BE%8B%E6%A2%B3%E7%90%86%E5%B7%A5%E4%BD%9C%E7%9A%84%E8%AF%B7%E7%A4%BA-v01.md)：最终 Markdown 成稿
- [20260404-关于申请开展“我的刀盾”传播案例梳理工作的请示-v01.docx](./20260404-%E5%85%B3%E4%BA%8E%E7%94%B3%E8%AF%B7%E5%BC%80%E5%B1%95%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E4%BC%A0%E6%92%AD%E6%A1%88%E4%BE%8B%E6%A2%B3%E7%90%86%E5%B7%A5%E4%BD%9C%E7%9A%84%E8%AF%B7%E7%A4%BA-v01.docx)：导出的 Word 文件

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/online/request-请示/20260404-关于申请开展“我的刀盾”传播案例梳理工作的请示-v01.md \
  -o demo/online/request-请示/20260404-关于申请开展“我的刀盾”传播案例梳理工作的请示-v01.docx \
  --doc-type 请示
```
