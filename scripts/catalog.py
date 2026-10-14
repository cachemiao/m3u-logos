"""Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only"""
import hashlib
import json
import re
import unicodedata
import warnings
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def key(value):
    return unicodedata.normalize("NFKC", value).strip().casefold()


def inspect_png(path):
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as im:
            if im.format != "PNG":
                raise ValueError("必须是 PNG 文件")
            if im.size != (300, 180):
                raise ValueError(f"画布必须为 300×180，实际为 {im.size}")
            if getattr(im, "n_frames", 1) != 1:
                raise ValueError("不接受动画 PNG")
            im.verify()
        with Image.open(path) as im:
            im.load()
            rgba = im.convert("RGBA")
            transparent = rgba.getchannel("A").getextrema()[0] < 255
            pixels = hashlib.sha256(rgba.tobytes()).hexdigest()
    return {
        "width": 300, "height": 180, "transparent": transparent,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pixel_hash": pixels,
    }


def collect(root=ROOT):
    errors, notices, results = [], [], []
    try:
        entries = json.loads((root / "data/channels.json").read_text("utf-8"))
        if not isinstance(entries, list):
            raise ValueError("顶层必须是数组")
    except (ValueError, OSError) as exc:
        return [], [f"channels.json: {exc}"], []
    ids, paths, names, pixel_hashes = set(), set(), {}, {}
    for index, entry in enumerate(entries):
        label = f"第 {index + 1} 条"
        try:
            if not isinstance(entry, dict):
                raise ValueError("记录必须是对象")
            for field in ("id", "name", "category", "file", "source", "usage"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError(f"缺少非空字符串 {field}")
            label = entry["id"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]):
                raise ValueError("id 只允许小写字母、数字和单连字符")
            if entry["id"] in ids:
                raise ValueError("id 重复")
            ids.add(entry["id"])
            category, filename = entry["category"], entry["file"]
            if category not in ("tv", "radio"):
                raise ValueError("category 必须为 tv 或 radio")
            if (filename != filename.strip() or filename in (".", "..")
                    or any(c in filename for c in '/\\?#%')
                    or any(ord(c) < 32 or ord(c) == 127 for c in filename)
                    or not filename.endswith(".png")):
                raise ValueError("file 必须为安全的 .png 文件名，不含目录")
            relative = f"{category}/{filename}"
            if key(relative) in paths:
                raise ValueError("资源路径重复（忽略大小写与 Unicode 形式）")
            paths.add(key(relative))
            path = root / relative
            if path.is_symlink() or path.resolve().parent != (root / category).resolve():
                raise ValueError("不接受符号链接或目录外文件")
            aliases = entry.get("aliases", [])
            if not isinstance(aliases, list) or any(not isinstance(a, str) or not a.strip() for a in aliases):
                raise ValueError("aliases 必须为非空字符串数组")
            for name in set(key(n) for n in [entry["name"], *aliases]):
                scope = (category, name)
                if scope in names and names[scope] != entry["id"]:
                    raise ValueError(f"名称或别名 {name!r} 与 {names[scope]} 冲突；请使用明确名称")
                names[scope] = entry["id"]
            if "region" in entry and not isinstance(entry["region"], str):
                raise ValueError("region 必须为字符串")
            info = inspect_png(path)
            if not info["transparent"]:
                notices.append(f"{label}: 无透明像素，请人工确认背景")
            if info["pixel_hash"] in pixel_hashes:
                notices.append(f"{label}: 与 {pixel_hashes[info['pixel_hash']]} 像素相同，请确认是否重复")
            pixel_hashes[info["pixel_hash"]] = label
            results.append({
                "id": entry["id"], "name": entry["name"], "aliases": aliases,
                "category": category, "region": entry.get("region", ""),
                "path": "/" + relative, "source": entry["source"], "usage": entry["usage"],
                **{k: v for k, v in info.items() if k != "pixel_hash"},
            })
        except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            errors.append(f"{label}: {exc}")
    for category in ("tv", "radio"):
        folder = root / category
        if not folder.is_dir() or folder.is_symlink():
            errors.append(f"{category}: 必须是普通目录")
            continue
        for path in folder.rglob("*"):
            if path.name == ".gitkeep" and path.is_file():
                continue
            if path.is_dir():
                errors.append(f"{path.relative_to(root)}: 不使用子目录")
            elif key(str(path.relative_to(root))) not in paths:
                errors.append(f"{path.relative_to(root)}: 未登记在 channels.json")
    return sorted(results, key=lambda x: x["id"]), errors, notices


def report(errors, notices):
    for notice in notices:
        print("提示:", notice)
    for error in errors:
        print("错误:", error)
