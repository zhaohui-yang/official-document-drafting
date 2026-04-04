# online / 通知

这是一个联网在线场景下的完整通知样例。

文件说明：

- [task.md](./task.md)：用户任务说明
- [materials.md](./materials.md)：可核实素材摘要
- [20260404-关于开展“我的刀盾”传播素材整理工作的通知-v01.md](./20260404-%E5%85%B3%E4%BA%8E%E5%BC%80%E5%B1%95%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E4%BC%A0%E6%92%AD%E7%B4%A0%E6%9D%90%E6%95%B4%E7%90%86%E5%B7%A5%E4%BD%9C%E7%9A%84%E9%80%9A%E7%9F%A5-v01.md)：最终 Markdown 成稿
- [20260404-关于开展“我的刀盾”传播素材整理工作的通知-v01.docx](./20260404-%E5%85%B3%E4%BA%8E%E5%BC%80%E5%B1%95%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E4%BC%A0%E6%92%AD%E7%B4%A0%E6%9D%90%E6%95%B4%E7%90%86%E5%B7%A5%E4%BD%9C%E7%9A%84%E9%80%9A%E7%9F%A5-v01.docx)：导出的 Word 文件

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/online/notice-通知/20260404-关于开展“我的刀盾”传播素材整理工作的通知-v01.md \
  -o demo/online/notice-通知/20260404-关于开展“我的刀盾”传播素材整理工作的通知-v01.docx \
  --doc-type 通知
```
