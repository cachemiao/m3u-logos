# CacheMiao Logos

电视与广播台标资源库，供 IPTV 播放器、M3U Studio 和其他工具下载、引用。

当前已从维护者本地素材导入并整理 **1,251 个电视台标、41 个广播台标，共 1,292 个**。
GitHub 公共仓库已创建：[cachemiao/logos](https://github.com/cachemiao/logos)。
当前内容已在本地整理，等待首次上传。资源使用条件待维护者确认。
与 `Jennie567/icon` 独立维护，不做自动同步。
第一版通过 GitHub 文件直链与下载包分发，暂不配置 Cloudflare Pages 或域名。

## 目录

```text
tv/                     电视台标，平铺 PNG 文件
radio/                  广播台标，平铺 PNG 文件
data/channels.json      手工维护的频道登记表
data/logos.json         生成的台标索引
data/aliases.json       生成的分类别名映射
data/stats.json         生成的数量统计
scripts/import.py       手动导入已审核素材
scripts/import_folder.py 批量清点和导入本地文件夹
scripts/validate.py     校验登记表与图片
scripts/build.py        生成索引和分发目录
dist/                   本地构建产物，不提交源码
```

## 开始使用

需要 Python 3.10 或以上版本。以下命令在项目目录执行：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py
```

空库也可正常构建。构建生成 `data/` 下的三个公开 JSON 文件，
并将索引与审核通过的 PNG 放入 `dist/`，方便以后制作下载包。
`built_at` 是构建时间，不代表台标内容更新时间。

## 添加台标

先人工确认素材的频道归属、图像质量、来源和使用条件，再执行：

```sh
python scripts/import.py /absolute/path/CCTV1.png \
  --id cctv1 --name 'CCTV-1 综合' --category tv --file CCTV1.png \
  --alias CCTV1 --alias CCTV-1 --alias 央视一套 \
  --region CN --source '填写实际素材来源' --usage '填写已确认的使用条件'
python scripts/validate.py
python scripts/build.py
```

这是命令格式示例，不包含台标素材。请替换来源与使用条件，不能直接保留占位说明。
工具不会调整尺寸、自动修图或覆盖已有文件。也可手动放入图片并编辑 `data/channels.json`。
完整登记格式见 [贡献指南](CONTRIBUTING.md)。

批量导入时可用 `scripts/import_folder.py`，支持 `--tv`、`--radio` 素材目录，
并要求填写 `--source`、`--usage` 和 `--report`。默认只清点，加 `--apply` 才导入。
工具保留图片和文件名，以文件名作为初始频道名称，不推测地区或自动生成频道别名。
非 ASCII 名称的初始 ID 使用 `分类-文件名摘要`，后续发布前可人工调整。
重复像素只提示，已有路径不会覆盖，异常图片和系统文件跳过并记入报告。
报告建议保存到工作区 `archives/`，其中包含本地素材清点信息，不提交源码。

首次导入后的重复整理仅保留 `陶瓷.png`，已移除重复的 `陶瓷频道.png`。
`湖北应城新闻党建.png` 为 252×156，未导入；源图片保持原样。
补充目录新增 117 张电视台标；`Nickelodeon.png` 和 `PlayBoyPlus.png`
与库内同名台标像素完全相同，未重复导入。大写 `.PNG` 扩展名统一为 `.png`。

## 公开引用（发布后使用）

首次上传完成后可使用以下地址；当前远程仓库仍为空：

```text
https://raw.githubusercontent.com/cachemiao/logos/main/tv/CCTV1.png
https://raw.githubusercontent.com/cachemiao/logos/main/data/logos.json
https://raw.githubusercontent.com/cachemiao/logos/main/data/aliases.json
https://raw.githubusercontent.com/cachemiao/logos/main/data/stats.json
```

索引中的 `path` 是资源路径，例如 `/tv/CCTV1.png`。接入程序应将它拼接到
`https://raw.githubusercontent.com/cachemiao/logos/main`，并对每段文件名进行 URL 编码。
图片更新保留原路径；频道 `id` 发布后保持稳定。

索引不包含直播源。后续 M3U Studio 可下载索引并本地缓存，按分类、名称和别名查找台标；
已有台标默认保留，歧义频道由用户选择。本阶段尚未修改编辑器。

别名规范化规则为 Unicode NFKC、去除两端空白、忽略大小写；不自动删除标点、HD、4K 等后缀。
同一类别的冲突别名会阻止构建，电视和广播的名称可以相同。

## 校验和下载包

```sh
python -m unittest discover -s tests -v
python scripts/build.py
```

GitHub Actions 在主分支提交和 PR 时校验并生成 `logos-static` 构建附件。
Actions 不会自动提交生成索引；本地构建后应将三个生成 JSON 与图片、登记表一起提交。
正式 Release 和公开仓库发布由维护者另行执行。

## 授权

脚本代码采用 GNU GPL v2.0（GPL-2.0-only），版权署名 cachemiao，见 [LICENSE](LICENSE)。
台标图片的使用条件独立记录，见 [资源说明](RESOURCE_POLICY.md)。
