# offline / 报告

这是一个离线提示词场景下的完整报告样例。

文件说明：

- [task.md](./task.md)：用户任务说明。
- [materials.md](./materials.md)：从长原始素材中提炼出的报告写作要点。
- [20260404-关于“我的刀盾”网络传播情况的报告-v01-提示词.md](./20260404-%E5%85%B3%E4%BA%8E%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E6%83%85%E5%86%B5%E7%9A%84%E6%8A%A5%E5%91%8A-v01-%E6%8F%90%E7%A4%BA%E8%AF%8D.md)：喂给离线宿主的完整提示词。
- [20260404-关于“我的刀盾”网络传播情况的报告-v01.md](./20260404-%E5%85%B3%E4%BA%8E%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E6%83%85%E5%86%B5%E7%9A%84%E6%8A%A5%E5%91%8A-v01.md)：模拟离线生成后的 Markdown 成稿。
- [20260404-关于“我的刀盾”网络传播情况的报告-v01.docx](./20260404-%E5%85%B3%E4%BA%8E%E2%80%9C%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE%E2%80%9D%E7%BD%91%E7%BB%9C%E4%BC%A0%E6%92%AD%E6%83%85%E5%86%B5%E7%9A%84%E6%8A%A5%E5%91%8A-v01.docx)：用 Python 导出的 Word 文件。

推荐流程：

1. 先阅读 [../raw-materials/20260404-我的刀盾-原始素材汇编-v01.md](../raw-materials/20260404-%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE-%E5%8E%9F%E5%A7%8B%E7%B4%A0%E6%9D%90%E6%B1%87%E7%BC%96-v01.md)。
2. 再看本目录的 [materials.md](./materials.md)，确认哪些事实被提炼进了报告。
3. 通过 `adapters/offline/build.py` 生成提示词。
4. 将提示词粘贴到离线宿主，得到报告成稿后再导出 `.docx`。

从当前 Markdown 成稿重新导出 `.docx`：

```bash
python3 renderers/docx.py \
  demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.md \
  -o demo/offline/report-报告/20260404-关于“我的刀盾”网络传播情况的报告-v01.docx \
  --doc-type 报告
```
