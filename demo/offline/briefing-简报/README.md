# offline / 简报

这是一个离线提示词场景下的完整简报样例。

文件说明：

- [task.md](./task.md)：用户任务说明。
- [materials.md](./materials.md)：从长原始素材中提炼出的简报写作要点。
- [20260404-“我的刀盾”网络动态简报-v01.md](./20260404-%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E5%8A%A8%E6%80%81%E7%AE%80%E6%8A%A5-v01.md)：模拟离线生成后的 Markdown 成稿。
- [20260404-“我的刀盾”网络动态简报-v01-提示词.md](./20260404-%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E5%8A%A8%E6%80%81%E7%AE%80%E6%8A%A5-v01-%E6%8F%90%E7%A4%BA%E8%AF%8D.md)：喂给离线宿主的完整提示词。
- [20260404-“我的刀盾”网络动态简报-v01.docx](./20260404-%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E5%8A%A8%E6%80%81%E7%AE%80%E6%8A%A5-v01.docx)：用 Python 导出的 Word 文件。

推荐流程：

1. 先阅读 [../raw-materials/20260404-我的刀盾-原始素材汇编-v01.md](../raw-materials/20260404-%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE-%E5%8E%9F%E5%A7%8B%E7%B4%A0%E6%9D%90%E6%B1%87%E7%BC%96-v01.md)。
2. 再看本目录的 [materials.md](./materials.md)，确认哪些事实被提炼进了简报。
3. 中强模型可直接使用本目录现成的 [20260404-“我的刀盾”网络动态简报-v01-提示词.md](./20260404-%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E5%8A%A8%E6%80%81%E7%AE%80%E6%8A%A5-v01-%E6%8F%90%E7%A4%BA%E8%AF%8D.md)，或 [default 简报 prompt](../../../dist/offline/default/doc-types/briefing-%E7%AE%80%E6%8A%A5/prompt.md)。
4. 弱模型优先改用 [small-local 简报 prompt](../../../dist/offline/small-local/doc-types/briefing-%E7%AE%80%E6%8A%A5/prompt.md)。

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/offline/briefing-简报/20260404-“我的刀盾”网络动态简报-v01.md \
  -o demo/offline/briefing-简报/20260404-“我的刀盾”网络动态简报-v01.docx \
  --doc-type 简报
```
