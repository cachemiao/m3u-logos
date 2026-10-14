"""Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only"""
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from catalog import ROOT, collect, key, report


def build(root=ROOT):
    logos, errors, notices = collect(root)
    report(errors, notices)
    if errors:
        raise ValueError("校验失败，中止构建")
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    aliases = {category: {} for category in ("tv", "radio")}
    for logo in logos:
        for name in [logo["name"], *logo["aliases"]]:
            aliases[logo["category"]][key(name)] = logo["id"]
    stats = {"total": len(logos), "tv": sum(x["category"] == "tv" for x in logos),
             "radio": sum(x["category"] == "radio" for x in logos), "built_at": timestamp}
    with tempfile.TemporaryDirectory(prefix=".build-", dir=root) as temporary:
        output = Path(temporary)
        api = output / "api/v1"
        api.mkdir(parents=True)
        for filename, content in {
            "logos.json": {"version": 1, "built_at": timestamp, "total": len(logos), "logos": logos},
            "aliases.json": {"version": 1, "normalization": "NFKC+strip+casefold", "aliases": aliases},
            "stats.json": stats,
        }.items():
            (api / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", "utf-8")
        for category in ("tv", "radio"):
            (output / category).mkdir()
        for logo in logos:
            relative = logo["path"].lstrip("/")
            shutil.copyfile(root / relative, output / relative)
        dist = root / "dist"
        if dist.is_symlink():
            raise ValueError("dist 不能是符号链接")
        if dist.exists():
            shutil.rmtree(dist)
        shutil.copytree(output, dist)
        for filename in ("logos.json", "aliases.json", "stats.json"):
            shutil.copyfile(dist / "api/v1" / filename, root / "data" / filename)
    print(f"构建完成：{len(logos)} 个台标 → {root / 'dist'}")


if __name__ == "__main__":
    try:
        build()
    except ValueError as exc:
        print(exc)
        raise SystemExit(1)
