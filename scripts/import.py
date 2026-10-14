"""手动导入一个已经审核的台标，不覆盖已有文件。
Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only
"""
import argparse
import json
import shutil
from catalog import ROOT, collect, inspect_png


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="本地 PNG 路径")
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--category", required=True, choices=["tv", "radio"])
    parser.add_argument("--file", required=True, help="公开文件名，例如 CCTV1.png")
    parser.add_argument("--alias", action="append", default=[])
    parser.add_argument("--region", default="")
    parser.add_argument("--source", required=True, help="来源链接或来源说明")
    parser.add_argument("--usage", required=True, help="已确认的资源使用条件")
    args = parser.parse_args()
    from pathlib import Path
    import tempfile
    source = Path(args.image)
    inspect_png(source)
    entries = json.loads((ROOT / "data/channels.json").read_text("utf-8"))
    entry = {k: getattr(args, k) for k in ("id", "name", "category", "file", "region", "source", "usage")}
    entry["aliases"] = args.alias
    # 在临时副本中校验全部记录，失败时不修改项目。
    with tempfile.TemporaryDirectory(prefix="logo-import-") as temporary:
        staging = Path(temporary)
        for category in ("tv", "radio", "data"):
            shutil.copytree(ROOT / category, staging / category)
        if Path(args.file).name != args.file or "\\" in args.file:
            raise ValueError("file 不能含目录")
        target = staging / args.category / args.file
        if target.exists():
            raise ValueError("目标文件已存在；替换台标请人工审核后操作")
        shutil.copyfile(source, target)
        content = json.dumps([*entries, entry], ensure_ascii=False, indent=2) + "\n"
        (staging / "data/channels.json").write_text(content, "utf-8")
        _, errors, notices = collect(staging)
        if errors:
            raise ValueError("\n".join(errors))
        from catalog import report
        report([], notices)
        destination = ROOT / args.category / args.file
        with destination.open("xb") as output:
            output.write(target.read_bytes())
        try:
            (ROOT / "data/channels.json").write_text(content, "utf-8")
        except OSError:
            destination.unlink()
            raise
    print(f"已导入 {args.category}/{args.file}，请检查后提交。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"导入失败：{exc}")
        raise SystemExit(1)
