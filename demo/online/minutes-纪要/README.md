# online / 纪要

这是一个联网在线场景下的完整纪要样例。

文件说明：

- [task.md](./task.md)：用户任务说明
- [materials.md](./materials.md)：可核实素材摘要
- [20260404-关于研究“刀盾”网络传播热度情况的专题会议纪要-v01.md](./20260404-%E5%85%B3%E4%BA%8E%E7%A0%94%E7%A9%B6%E2%80%9C%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E7%83%AD%E5%BA%A6%E6%83%85%E5%86%B5%E7%9A%84%E4%B8%93%E9%A2%98%E4%BC%9A%E8%AE%AE%E7%BA%AA%E8%A6%81-v01.md)：最终 Markdown 成稿
- [20260404-关于研究“刀盾”网络传播热度情况的专题会议纪要-v01.docx](./20260404-%E5%85%B3%E4%BA%8E%E7%A0%94%E7%A9%B6%E2%80%9C%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E7%83%AD%E5%BA%A6%E6%83%85%E5%86%B5%E7%9A%84%E4%B8%93%E9%A2%98%E4%BC%9A%E8%AE%AE%E7%BA%AA%E8%A6%81-v01.docx)：导出的 Word 文件

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/online/minutes-纪要/20260404-关于研究“刀盾”网络传播热度情况的专题会议纪要-v01.md \
  -o demo/online/minutes-纪要/20260404-关于研究“刀盾”网络传播热度情况的专题会议纪要-v01.docx \
  --doc-type 纪要
```
