#!/usr/bin/env python3
"""
gen_index.py
============
リポジトリ内の HTML ファイルをスキャンし、
  - 各フォルダの index.html（ファイル一覧）
  - ルートの index.html（フォルダ一覧）
を自動生成する。

対象: リポジトリルートに存在する 1 階層目のフォルダ配下の *.html
      （index.html 自身と .github/ は除外）

フォルダのメタ情報は FOLDER_META に定義。
新しいフォルダを追加した場合はここに追記するか、
定義がなければ自動的にデフォルト値が使われる。
"""

import os
import re
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── 設定 ─────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]   # .github/scripts/ の 2 つ上
EXCLUDE_DIRS = {'.github', '.git', 'node_modules', '__pycache__'}
EXCLUDE_FILES = {'index.html'}
JST = timezone(timedelta(hours=9))

# フォルダごとのメタ情報（将来フォルダを追加したらここに追記）
FOLDER_META: dict[str, dict] = {
    'SpecificationsDoc': {
        'icon': '📄',
        'desc': '仕様書テンプレート集 — Windows GUI アプリ・その他',
    },
    # 追加例:
    # 'ArchitectureDocs': {
    #     'icon': '🏗️',
    #     'desc': 'アーキテクチャ設計ドキュメント',
    # },
}

DEFAULT_META = {'icon': '📁', 'desc': '（説明未設定）'}

# ─── ユーティリティ ────────────────────────────────────────

def extract_title(html_path: Path) -> str:
    """<title> タグからタイトルを取得する。なければファイル名を返す。"""
    try:
        text = html_path.read_text(encoding='utf-8', errors='ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
        if m:
            return re.sub(r'\s+', ' ', m.group(1)).strip()
    except Exception:
        pass
    return html_path.stem

def fmt_dt(dt: datetime) -> str:
    return dt.astimezone(JST).strftime('%Y/%m/%d %H:%M JST')

def now_str() -> str:
    return fmt_dt(datetime.now(timezone.utc))

def file_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

# ─── テンプレート読み込み ──────────────────────────────────

def load_template(name: str) -> str:
    """REPO_ROOT 直下のテンプレートファイルを読む。
    なければフォールバック用の最小 HTML を返す。"""
    candidates = [
        REPO_ROOT / name,
        REPO_ROOT / '.github' / 'templates' / name,
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding='utf-8')
    # フォールバック: テンプレートが見つからない場合は空文字
    return ''

# ─── サブフォルダ index.html 生成 ─────────────────────────

def build_file_card(html_file: Path, folder_path: Path) -> str:
    name = html_file.name
    title = extract_title(html_file)
    mtime = fmt_dt(file_mtime(html_file))
    rel = html_file.relative_to(folder_path)
    return f'''      <a class="file-card" href="{rel}">
        <div class="file-icon">📄</div>
        <div class="file-info">
          <div class="file-name">{name}</div>
          <div class="file-title">{title}</div>
          <div class="file-meta">更新: {mtime}</div>
        </div>
        <div class="file-arrow">→</div>
      </a>'''

def build_nav_link(html_file: Path) -> str:
    name = html_file.name
    title = extract_title(html_file)
    short = title[:28] + '…' if len(title) > 30 else title
    return f'    <a class="nav-link" href="{name}" title="{title}"><span class="icon">📄</span>{short}</a>'

def generate_folder_index(folder_path: Path, template: str) -> str:
    html_files = sorted(
        [f for f in folder_path.glob('*.html') if f.name not in EXCLUDE_FILES],
        key=lambda f: f.name
    )
    now = now_str()
    last = fmt_dt(max((file_mtime(f) for f in html_files), default=datetime.now(timezone.utc))) if html_files else now

    cards = '\n'.join(build_file_card(f, folder_path) for f in html_files) if html_files else \
        '      <div class="empty"><div class="icon">📭</div><p>ファイルがありません</p></div>'
    nav_items = '\n'.join(build_nav_link(f) for f in html_files)

    result = template
    result = result.replace('<!-- FILE_CARDS -->', cards)
    result = result.replace('<!-- FILE_NAV_ITEMS -->', nav_items)
    result = result.replace('<!-- FILE_COUNT -->', str(len(html_files)))
    result = result.replace('<!-- UPDATED_AT -->', now)
    result = result.replace('<!-- LAST_UPDATED -->', last)
    return result

# ─── ルート index.html 生成 ───────────────────────────────

def build_folder_card(folder_path: Path, meta: dict, html_files: list[Path]) -> str:
    folder_name = folder_path.name
    icon = meta['icon']
    desc = meta['desc']
    count = len(html_files)
    chips = ''.join(
        f'<span class="folder-file-chip">{f.name}</span>'
        for f in html_files[:6]
    )
    if count > 6:
        chips += f'<span class="folder-file-chip">+{count - 6}</span>'
    return f'''      <a class="folder-card" href="{folder_name}/index.html">
        <div class="folder-stripe"></div>
        <div class="folder-body">
          <div class="folder-top">
            <div class="folder-icon">{icon}</div>
            <span class="folder-name">{folder_name}/</span>
            <span class="folder-count">{count} files</span>
          </div>
          <div class="folder-desc">{desc}</div>
          <div class="folder-files">{chips}</div>
        </div>
        <div class="folder-arrow">→</div>
      </a>'''

def build_folder_nav(folder_path: Path, meta: dict) -> str:
    icon = meta['icon']
    name = folder_path.name
    return f'    <a class="nav-item" href="{name}/index.html">{icon} {name}</a>'

def generate_root_index(folders: list[tuple[Path, dict, list[Path]]], template: str) -> str:
    now = now_str()
    total_files = sum(len(files) for _, _, files in folders)

    all_mtimes = [file_mtime(f) for _, _, files in folders for f in files]
    last = fmt_dt(max(all_mtimes)) if all_mtimes else now

    cards = '\n'.join(build_folder_card(p, m, f) for p, m, f in folders)
    nav_items = '\n'.join(build_folder_nav(p, m) for p, m, _ in folders)

    result = template
    result = result.replace('<!-- FOLDER_CARDS -->', cards)
    result = result.replace('<!-- FOLDER_NAV_ITEMS -->', nav_items)
    result = result.replace('<!-- FOLDER_COUNT -->', str(len(folders)))
    result = result.replace('<!-- TOTAL_FILES -->', str(total_files))
    result = result.replace('<!-- UPDATED_AT -->', now)
    result = result.replace('<!-- LAST_UPDATED -->', last)
    return result

# ─── メイン ───────────────────────────────────────────────

def main():
    folder_tmpl = load_template('SpecificationsDoc/index.html')
    root_tmpl   = load_template('index.html')

    if not folder_tmpl or not root_tmpl:
        print('⚠️  テンプレートが見つかりません。SpecificationsDoc/index.html と index.html をコミットしてください。')
        return

    folders_data: list[tuple[Path, dict, list[Path]]] = []

    # 1 階層目のフォルダをスキャン
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith('.'):
            continue

        html_files = sorted(
            [f for f in entry.glob('*.html') if f.name not in EXCLUDE_FILES],
            key=lambda f: f.name
        )
        if not html_files:
            continue

        meta = FOLDER_META.get(entry.name, {**DEFAULT_META})
        folders_data.append((entry, meta, html_files))

        # フォルダ内 index.html を生成
        folder_index = generate_folder_index(entry, folder_tmpl)
        out_path = entry / 'index.html'
        out_path.write_text(folder_index, encoding='utf-8')
        print(f'✅  生成: {out_path.relative_to(REPO_ROOT)}  ({len(html_files)} files)')

    # ルート index.html を生成
    root_index = generate_root_index(folders_data, root_tmpl)
    root_out = REPO_ROOT / 'index.html'
    root_out.write_text(root_index, encoding='utf-8')
    print(f'✅  生成: index.html  ({len(folders_data)} folders)')

if __name__ == '__main__':
    main()
