"""Copyright cachemiao. SPDX-License-Identifier: GPL-2.0-only"""
from catalog import collect, report

if __name__ == "__main__":
    logos, errors, notices = collect()
    report(errors, notices)
    print(f"已校验 {len(logos)} 个台标；{len(errors)} 个错误，{len(notices)} 个提示。")
    raise SystemExit(1 if errors else 0)
