"""批量导入本地文件夹；默认只生成清点报告，--apply 才写入项目。
Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only
"""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from catalog import ROOT, collect, inspect_png, key


def import_folders(folders, source, usage, report_path, apply=False, root=ROOT):
    existing = json.loads((root / "data/channels.json").read_text("utf-8"))
    ids = {e["id"] for e in existing}
    paths = {key(e["category"] + "/" + e["file"]) for e in existing}
    names = {(e["category"], key(n)) for e in existing for n in [e["name"], *e.get("aliases", [])]}
    report = {"applied": False, "accepted": [], "skipped": [], "duplicate_pixels": []}
    entries, files, hashes = [], [], {}
    for category, folder in folders.items():
        folder = Path(folder)
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError(f"素材目录不存在或为符号链接：{folder}")
        for path in sorted(folder.rglob("*")):
            if not path.is_file() and not path.is_symlink():
                continue
            relative = str(path.relative_to(folder))
            label = {"category": category, "original": relative}
            try:
                if path.is_symlink():
                    raise ValueError("跳过符号链接")
                if path.name.startswith('.') or path.suffix.lower() != '.png':
                    raise ValueError("非 PNG 或隐藏文件")
                filename = path.stem + '.png'
                if filename != filename.strip() or any(c in filename for c in '/\\?#%') or any(ord(c) < 32 or ord(c) == 127 for c in filename):
                    raise ValueError("文件名需要人工整理")
                resource = key(category + '/' + filename)
                name = path.stem
                if resource in paths or (category, key(name)) in names:
                    raise ValueError("路径或频道名称已存在")
                info = inspect_png(path)
                # 非 ASCII 名称使用文件名摘要，避免猜测拼音或频道身份。
                slug = re.sub(r'[^a-z0-9]+', '-', key(name)).strip('-') if name.isascii() else ''
                if not slug:
                    slug = hashlib.sha256(key(filename).encode('utf-8')).hexdigest()[:16]
                identifier = f'{category}-{slug}'
                if identifier in ids:
                    identifier += '-' + hashlib.sha256(key(filename).encode('utf-8')).hexdigest()[:16]
                if identifier in ids:
                    raise ValueError("ID 冲突，需要人工登记")
                entry = {"id": identifier, "name": name, "category": category,
                         "file": filename, "aliases": [], "source": source, "usage": usage}
                ids.add(identifier)
                paths.add(resource)
                names.add((category, key(name)))
                entries.append(entry)
                files.append((path, category, filename))
                report['accepted'].append({**label, 'id': identifier, 'file': filename})
                hashes.setdefault(info['pixel_hash'], []).append(f'{category}/{filename}')
            except (ValueError, OSError) as exc:
                report['skipped'].append({**label, 'reason': str(exc)})
    report['duplicate_pixels'] = [v for v in hashes.values() if len(v) > 1]
    report['counts'] = {c: sum(e['category'] == c for e in entries) for c in ('tv', 'radio')}
    content = json.dumps([*existing, *entries], ensure_ascii=False, indent=2) + '\n'
    with tempfile.TemporaryDirectory(prefix='logo-batch-') as temporary:
        staging = Path(temporary)
        for category in ('tv', 'radio', 'data'):
            shutil.copytree(root / category, staging / category)
        for path, category, filename in files:
            shutil.copyfile(path, staging / category / filename)
        (staging / 'data/channels.json').write_text(content, 'utf-8')
        _, errors, notices = collect(staging)
        report['notices'] = notices
        if errors:
            raise ValueError('\n'.join(errors))
        if apply:
            written = []
            try:
                for _, category, filename in files:
                    target = root / category / filename
                    with target.open('xb') as output:
                        written.append(target)
                        output.write((staging / category / filename).read_bytes())
                metadata_temp = root / 'data/channels.json.tmp'
                metadata_temp.write_text(content, 'utf-8')
                metadata_temp.replace(root / 'data/channels.json')
            except OSError:
                for path in written:
                    path.unlink()
                raise
            report['applied'] = True
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps({'applied': report['applied'], 'counts': report['counts'],
                      'skipped': len(report['skipped']), 'duplicate_groups': len(report['duplicate_pixels']),
                      'report': str(report_path)}, ensure_ascii=False))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tv', type=Path)
    parser.add_argument('--radio', type=Path)
    parser.add_argument('--source', required=True)
    parser.add_argument('--usage', required=True)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not args.tv and not args.radio:
        parser.error('至少提供 --tv 或 --radio')
    try:
        import_folders({c: p for c, p in [('tv', args.tv), ('radio', args.radio)] if p},
                       args.source, args.usage, args.report, args.apply)
    except (OSError, ValueError) as exc:
        print(f'批量导入失败：{exc}')
        raise SystemExit(1)
