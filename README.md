# M3U Logos

电视与广播台标资源库，供 IPTV 播放器、频道编辑器及其他工具下载、引用。

收录 **1,251 个电视台标、41 个广播台标，共 1,292 个**，图片采用 **300×180 PNG** 格式。

## 下载台标

[下载完整资源库](https://github.com/cachemiao/m3u-logos/archive/refs/heads/main.zip)，解压后：

- `tv/`：电视台标。
- `radio/`：广播台标。

也可以在对应目录中查找并下载单张图片。

## 引用台标

图片可通过 GitHub Raw 直链引用，例如：

```text
https://raw.githubusercontent.com/cachemiao/m3u-logos/main/tv/CCTV1.png
```

在 M3U 中使用：

```m3u
#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/cachemiao/m3u-logos/main/tv/CCTV1.png",CCTV1
频道播放地址
```

广播台标使用相同方式，将路径中的 `tv/` 改为 `radio/`，并填写实际文件名。
包含中文、空格等字符的文件名，生成 URL 时需进行 URL 编码。

## JSON 索引

提供以下索引，方便其他工具查找和引用台标：

| 文件 | 内容 |
| --- | --- |
| [logos.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/logos.json) | 台标 ID、名称、分类、图片路径及来源信息 |
| [aliases.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/aliases.json) | 频道名称与已登记别名的映射 |
| [stats.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/stats.json) | 台标数量统计 |

`logos.json` 中的 `path` 为资源路径，例如 `/tv/CCTV1.png`。
将其拼接到 `https://raw.githubusercontent.com/cachemiao/m3u-logos/main` 即可得到图片直链。

## 反馈与贡献

欢迎通过 [Issues](https://github.com/cachemiao/m3u-logos/issues) 反馈缺失、过时或错误的台标。
请注明频道名称、地区及对应文件名；提供新素材时附上来源说明。

添加台标和运行校验工具的方法见 [贡献指南](CONTRIBUTING.md)。

## 授权

脚本代码采用 GNU GPL v2.0（GPL-2.0-only），版权署名 cachemiao，见 [LICENSE](LICENSE)。
台标图片的使用条件独立记录，见 [资源说明](RESOURCE_POLICY.md)。
