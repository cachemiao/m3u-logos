<p align="center">
  <img src="docs/images/logo.svg" width="96" height="96" alt="M3U Logos">
</p>

<h1 align="center">M3U Logos</h1>

<p align="center">TV & Radio Channel Logo Library</p>

<p align="center">
  <a href="tv"><img src="https://img.shields.io/badge/logos-1292-0f766e" alt="1,292 logos"></a>
  <a href="tv"><img src="https://img.shields.io/badge/PNG-300%C3%97180-0f766e" alt="PNG 300×180"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-GPL--2.0--only-orange" alt="Code: GPL-2.0-only"></a>
  <a href="https://github.com/cachemiao/m3u-logos/stargazers"><img src="https://img.shields.io/github/stars/cachemiao/m3u-logos?style=flat&amp;color=0f766e" alt="GitHub Stars"></a>
  <a href="https://t.me/m3ustudio_news"><img src="https://img.shields.io/badge/Telegram-Channel-26A5E4?logo=telegram&amp;logoColor=white" alt="Telegram channel"></a>
  <a href="https://t.me/m3ustudio_chat"><img src="https://img.shields.io/badge/Telegram-Group-26A5E4?logo=telegram&amp;logoColor=white" alt="Telegram group"></a>
</p>

<p align="center"><a href="README.md">简体中文</a> · <strong>English</strong></p>

A **TV and radio channel logo library** for IPTV players, playlist editors and other tools. It contains **1,251 TV logos and 41 radio logos — 1,292 in total**, provided as **300×180 PNG** images with public **JSON indexes**.

The scripts are licensed under **GNU GPL v2.0 (GPL-2.0-only)**. Image usage conditions are described in the [resource policy](RESOURCE_POLICY.md). To report incorrect logos, source information or rights concerns, please [open an issue](https://github.com/cachemiao/m3u-logos/issues).

- [Telegram channel](https://t.me/m3ustudio_news): M3U Studio project news and announcements.
- [Telegram group](https://t.me/m3ustudio_chat): discussion, help and feedback.

---

## Download logos

[Download the complete library](https://github.com/cachemiao/m3u-logos/archive/refs/heads/main.zip) and extract the archive:

- `tv/`: TV channel logos.
- `radio/`: Radio station logos.

You can also browse either directory and download individual images.

## Use a logo URL

Images can be referenced directly through GitHub Raw:

```text
https://raw.githubusercontent.com/cachemiao/m3u-logos/main/tv/CCTV1.png
```

Example in an M3U playlist:

```m3u
#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/cachemiao/m3u-logos/main/tv/CCTV1.png",CCTV1
CHANNEL_STREAM_URL
```

For radio logos, replace `tv/` with `radio/` and use the actual file name.
URL-encode file names that contain spaces, Chinese characters or other special characters.

## JSON indexes

Public indexes help other tools find and reference logos:

| File | Contents |
| --- | --- |
| [logos.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/logos.json) | Logo IDs, names, categories, image paths and source information |
| [aliases.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/aliases.json) | Channel names and registered aliases mapped to logo IDs |
| [stats.json](https://raw.githubusercontent.com/cachemiao/m3u-logos/main/data/stats.json) | Logo counts |

The `path` field in `logos.json` is a resource path, such as `/tv/CCTV1.png`.
Append it to `https://raw.githubusercontent.com/cachemiao/m3u-logos/main` to obtain the image URL.

## Feedback and contributions

Use [Issues](https://github.com/cachemiao/m3u-logos/issues) to report missing, outdated or incorrect logos.
Include the channel name, region and file name. New image contributions should include source information.

See the [contribution guide](CONTRIBUTING.md) (Chinese) for instructions on adding logos and running validation tools.

## License

The scripts are licensed under GNU GPL v2.0 (GPL-2.0-only), copyright cachemiao. See [LICENSE](LICENSE).
Image usage conditions are recorded separately; see the [resource policy](RESOURCE_POLICY.md) (Chinese).
