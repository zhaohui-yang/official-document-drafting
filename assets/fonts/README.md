# 字体目录

这个目录只用于存放你自行准备或通过 `scripts/download_fonts.sh` 下载的字体文件。

- 推荐文件名、安装流程和授权注意事项见仓库根目录 [README.md](../../README.md)
- 字体族到文件的映射由 [catalog.toml](./catalog.toml) 统一维护。
- 将字体放入本目录后，可运行 `bash scripts/install_fonts.sh`
- 当前仓库默认不提交开源替代字体文件；需要时请运行 `bash scripts/download_fonts.sh minimal`
- 当前目录中保留的中文字体文件：
- `方正小标宋简.TTF`
- `仿宋_GB2312.ttf`
- `黑体公文字体.ttf`
- `楷体_GB2312.ttf`
- 上述前两个字体文件的来源页备注为：
- https://life.scnu.edu.cn/a/20220309/5508.html
- 新增 `黑体公文字体.ttf`、`楷体_GB2312.ttf` 的来源和授权边界同样需使用者自行确认。
- 源码仓库可以保留这些字体文件；如通过 ClawHub 发布 skill，`.clawhubignore` 会排除本目录中的 `.ttf`、`.otf` 字体二进制，发布包默认不携带字体文件。
- 使用前仍应自行确认授权、适用范围和分发边界。
