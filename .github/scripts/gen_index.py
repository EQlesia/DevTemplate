#!/usr/bin/env python3
"""
gen_index.py
============
リポジトリ内の HTML ファイルをスキャンし、
  - 各フォルダの index.html（ファイル一覧）
  - ルートの index.html（フォルダ一覧）
を自動生成する。

テンプレートはこのスクリプト内に直接埋め込まれている。
（ファイルから読み込む方式だと、生成済み index.html を
  テンプレートとして読んでしまいプレースホルダーが消える問題を回避）
"""

import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── 設定 ─────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).resolve().parents[2]  # .github/scripts/ の 2 つ上
EXCLUDE_DIRS  = {'.github', '.git', 'node_modules', '__pycache__'}
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

# ─── 埋め込みテンプレート ──────────────────────────────────
# ※ テンプレートをファイルから読むと、既に生成済みの index.html
#   （プレースホルダーなし）を読んでしまい何も置換されなくなる。
#   スクリプト内に埋め込むことでその問題を回避する。

FOLDER_INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TMPL_FOLDER_NAME — DevTemplate</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  :root{--ink:#0f1117;--ink-light:#4a5060;--ink-faint:#9aa0b0;--accent:#1a6bff;--accent-dim:#d6e5ff;--accent-glow:rgba(26,107,255,0.10);--surface:#fff;--surface-2:#f5f7fb;--surface-3:#eef1f8;--border:#dde2ed;--sidebar-w:240px;--header-h:56px}
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{font-family:'Noto Sans JP',sans-serif;font-size:14px;line-height:1.8;color:var(--ink);background:var(--surface);display:flex;min-height:100vh}
  #sidebar{width:var(--sidebar-w);height:100vh;position:fixed;top:0;left:0;background:var(--ink);color:#e2e8f0;overflow-y:auto;z-index:100;display:flex;flex-direction:column}
  #sidebar-logo{padding:24px 20px 20px;border-bottom:1px solid rgba(255,255,255,.08)}
  #sidebar-logo .repo{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.15em;color:var(--accent);margin-bottom:6px}
  #sidebar-logo .title{font-family:'Syne',sans-serif;font-size:17px;font-weight:800;color:#fff;line-height:1.2}
  #sidebar nav{padding:16px 0 24px;flex:1}
  .nav-label{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.28);padding:10px 20px 4px}
  .nav-folder{display:flex;align-items:center;gap:8px;padding:8px 20px;font-size:13px;color:rgba(255,255,255,.85);font-weight:600;border-left:2px solid var(--accent);background:rgba(26,107,255,.1)}
  .nav-link{display:flex;align-items:center;gap:8px;padding:7px 20px 7px 32px;font-size:12px;color:rgba(255,255,255,.52);text-decoration:none;border-left:2px solid transparent;transition:all .15s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .nav-link:hover{color:#fff;background:rgba(255,255,255,.06);border-left-color:var(--accent)}
  .nav-other{display:flex;align-items:center;gap:8px;padding:7px 20px;font-size:12px;color:rgba(255,255,255,.4);text-decoration:none;transition:all .15s}
  .nav-other:hover{color:rgba(255,255,255,.75)}
  #main{margin-left:var(--sidebar-w);flex:1}
  #topbar{height:var(--header-h);background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 48px;position:sticky;top:0;z-index:50;gap:8px}
  .breadcrumb{font-size:12px;color:var(--ink-faint);display:flex;align-items:center;gap:6px;flex:1;font-family:'DM Mono',monospace}
  .breadcrumb a{color:var(--accent);text-decoration:none}
  .breadcrumb a:hover{text-decoration:underline}
  .breadcrumb .current{color:var(--ink)}
  .updated-badge{font-size:11px;font-family:'DM Mono',monospace;color:var(--ink-faint)}
  #content{max-width:840px;margin:0 auto;padding:48px 48px 120px}
  .section-header{background:var(--ink);margin:-48px -48px 40px;padding:48px 48px 40px;position:relative;overflow:hidden}
  .section-header::before{content:'';position:absolute;top:-60px;right:-40px;width:260px;height:260px;border-radius:50%;background:radial-gradient(circle,rgba(26,107,255,.2) 0%,transparent 70%)}
  .section-header .eyebrow{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:10px}
  .section-header h1{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:#fff;margin-bottom:6px;position:relative;z-index:1}
  .section-header .sub{font-size:13px;color:rgba(255,255,255,.45);position:relative;z-index:1}
  .stats-bar{display:flex;gap:24px;margin-bottom:32px;padding:16px 20px;background:var(--surface-2);border:1px solid var(--border);border-radius:8px}
  .stat{display:flex;flex-direction:column;gap:2px}
  .stat .k{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)}
  .stat .v{font-size:18px;font-weight:700;color:var(--ink);font-family:'Syne',sans-serif}
  .file-grid{display:grid;grid-template-columns:1fr;gap:10px;margin-bottom:40px}
  .file-card{display:flex;align-items:center;gap:16px;padding:16px 20px;border:1px solid var(--border);border-radius:8px;text-decoration:none;color:inherit;transition:border-color .15s,box-shadow .15s,background .15s;background:var(--surface)}
  .file-card:hover{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow);background:var(--surface-2)}
  .file-icon{width:40px;height:40px;background:var(--accent-dim);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
  .file-info{flex:1;min-width:0}
  .file-name{font-family:'DM Mono',monospace;font-size:13px;font-weight:500;color:var(--accent);margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .file-title{font-size:13px;color:var(--ink);font-weight:600;margin-bottom:2px}
  .file-meta{font-size:12px;color:var(--ink-faint)}
  .file-arrow{color:var(--ink-faint);font-size:16px;transition:transform .15s,color .15s}
  .file-card:hover .file-arrow{transform:translateX(4px);color:var(--accent)}
  .empty{text-align:center;padding:60px 20px;color:var(--ink-faint);border:1px dashed var(--border);border-radius:8px}
  .page-footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--ink-faint);display:flex;justify-content:space-between;font-family:'DM Mono',monospace}
  #sidebar::-webkit-scrollbar{width:4px}
  #sidebar::-webkit-scrollbar-thumb{background:rgba(255,255,255,.15);border-radius:2px}
</style>
</head>
<body>
<aside id="sidebar">
  <div id="sidebar-logo">
    <div class="repo">EQlesia / DevTemplate</div>
    <div class="title">Dev<br>Template</div>
  </div>
  <nav>
    <div class="nav-label">ドキュメント</div>
    <div class="nav-folder"><span>📂</span> TMPL_FOLDER_NAME</div>
    TMPL_FILE_NAV_ITEMS
    <div style="height:16px"></div>
    <div class="nav-label">リポジトリ</div>
    <a class="nav-other" href="../index.html">🏠 ルートへ戻る</a>
    <a class="nav-other" href="https://github.com/EQlesia/DevTemplate" target="_blank">⎋ GitHub</a>
  </nav>
</aside>
<div id="main">
  <div id="topbar">
    <div class="breadcrumb">
      <a href="../index.html">DevTemplate</a>
      <span>/</span>
      <span class="current">TMPL_FOLDER_NAME</span>
    </div>
    <span class="updated-badge">更新: TMPL_UPDATED_AT</span>
  </div>
  <div id="content">
    <div class="section-header">
      <div class="eyebrow">EQlesia / DevTemplate</div>
      <h1>TMPL_FOLDER_NAME</h1>
      <p class="sub">TMPL_FOLDER_DESC</p>
    </div>
    <div class="stats-bar">
      <div class="stat"><span class="k">ファイル数</span><span class="v">TMPL_FILE_COUNT</span></div>
      <div class="stat"><span class="k">最終更新</span><span class="v" style="font-size:13px;padding-top:4px">TMPL_LAST_UPDATED</span></div>
      <div class="stat"><span class="k">フォルダ</span><span class="v" style="font-size:13px;padding-top:4px">TMPL_FOLDER_NAME/</span></div>
    </div>
    <div class="file-grid">TMPL_FILE_CARDS</div>
    <div class="page-footer">
      <span>EQlesia/DevTemplate — TMPL_FOLDER_NAME</span>
      <span>自動生成 by GitHub Actions</span>
    </div>
  </div>
</div>
</body>
</html>
"""

ROOT_INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DevTemplate — EQlesia</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  :root{--ink:#0f1117;--ink-light:#4a5060;--ink-faint:#9aa0b0;--accent:#1a6bff;--accent-dim:#d6e5ff;--accent-glow:rgba(26,107,255,0.10);--surface:#fff;--surface-2:#f5f7fb;--surface-3:#eef1f8;--border:#dde2ed;--sidebar-w:240px;--header-h:56px}
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{font-family:'Noto Sans JP',sans-serif;font-size:14px;line-height:1.8;color:var(--ink);background:var(--surface);display:flex;min-height:100vh}
  #sidebar{width:var(--sidebar-w);height:100vh;position:fixed;top:0;left:0;background:var(--ink);color:#e2e8f0;overflow-y:auto;z-index:100;display:flex;flex-direction:column}
  #sidebar-logo{padding:24px 20px 20px;border-bottom:1px solid rgba(255,255,255,.08)}
  #sidebar-logo .owner{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.15em;color:var(--accent);margin-bottom:6px}
  #sidebar-logo .title{font-family:'Syne',sans-serif;font-size:19px;font-weight:800;color:#fff;line-height:1.2}
  #sidebar nav{padding:16px 0 24px;flex:1}
  .nav-label{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.28);padding:10px 20px 4px}
  .nav-item{display:flex;align-items:center;gap:8px;padding:8px 20px;font-size:13px;color:rgba(255,255,255,.6);text-decoration:none;border-left:2px solid transparent;transition:all .15s}
  .nav-item:hover{color:#fff;background:rgba(255,255,255,.06);border-left-color:var(--accent)}
  .nav-ext{display:flex;align-items:center;gap:8px;padding:7px 20px;font-size:12px;color:rgba(255,255,255,.38);text-decoration:none;transition:color .15s}
  .nav-ext:hover{color:rgba(255,255,255,.75)}
  #main{margin-left:var(--sidebar-w);flex:1}
  #topbar{height:var(--header-h);background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 48px;position:sticky;top:0;z-index:50;gap:8px}
  .breadcrumb{font-size:12px;font-family:'DM Mono',monospace;color:var(--ink);flex:1}
  .updated-badge{font-size:11px;font-family:'DM Mono',monospace;color:var(--ink-faint)}
  #content{max-width:840px;margin:0 auto;padding:48px 48px 120px}
  .hero{background:var(--ink);margin:-48px -48px 48px;padding:56px 48px 48px;position:relative;overflow:hidden}
  .hero::before{content:'';position:absolute;top:-80px;right:-60px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(26,107,255,.22) 0%,transparent 70%)}
  .hero .eyebrow{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
  .hero h1{font-family:'Syne',sans-serif;font-size:44px;font-weight:800;color:#fff;line-height:1.1;margin-bottom:10px;position:relative;z-index:1}
  .hero p{font-size:15px;color:rgba(255,255,255,.48);position:relative;z-index:1}
  .stats-bar{display:flex;gap:24px;margin-bottom:40px;padding:16px 20px;background:var(--surface-2);border:1px solid var(--border);border-radius:8px}
  .stat .k{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)}
  .stat .v{font-size:18px;font-weight:700;color:var(--ink);font-family:'Syne',sans-serif}
  .folder-grid{display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:48px}
  .folder-card{display:flex;align-items:stretch;border:1px solid var(--border);border-radius:10px;text-decoration:none;color:inherit;overflow:hidden;transition:border-color .15s,box-shadow .15s}
  .folder-card:hover{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
  .folder-stripe{width:6px;background:var(--accent);flex-shrink:0}
  .folder-body{padding:20px 24px;flex:1}
  .folder-top{display:flex;align-items:center;gap:10px;margin-bottom:8px}
  .folder-icon{width:36px;height:36px;background:var(--accent-dim);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}
  .folder-name{font-family:'DM Mono',monospace;font-size:14px;font-weight:500;color:var(--accent)}
  .folder-count{margin-left:auto;font-size:11px;font-family:'DM Mono',monospace;background:var(--accent-dim);color:var(--accent);padding:2px 8px;border-radius:4px}
  .folder-desc{font-size:13px;color:var(--ink-light);margin-bottom:10px}
  .folder-files{display:flex;flex-wrap:wrap;gap:6px}
  .folder-file-chip{font-family:'DM Mono',monospace;font-size:11px;background:var(--surface-3);color:var(--ink-light);padding:2px 8px;border-radius:4px;border:1px solid var(--border)}
  .folder-arrow{display:flex;align-items:center;padding:0 20px;font-size:20px;color:var(--ink-faint);transition:transform .15s,color .15s}
  .folder-card:hover .folder-arrow{transform:translateX(4px);color:var(--accent)}
  .page-footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--border);font-size:12px;color:var(--ink-faint);display:flex;justify-content:space-between;font-family:'DM Mono',monospace}
  #sidebar::-webkit-scrollbar{width:4px}
  #sidebar::-webkit-scrollbar-thumb{background:rgba(255,255,255,.15);border-radius:2px}
</style>
</head>
<body>
<aside id="sidebar">
  <div id="sidebar-logo">
    <div class="owner">EQlesia</div>
    <div class="title">Dev<br>Template</div>
  </div>
  <nav>
    <div class="nav-label">フォルダ</div>
    TMPL_FOLDER_NAV_ITEMS
    <div style="height:16px"></div>
    <div class="nav-label">リンク</div>
    <a class="nav-ext" href="https://github.com/EQlesia/DevTemplate" target="_blank">⎋ GitHub</a>
  </nav>
</aside>
<div id="main">
  <div id="topbar">
    <div class="breadcrumb">EQlesia / DevTemplate</div>
    <span class="updated-badge">更新: TMPL_UPDATED_AT</span>
  </div>
  <div id="content">
    <div class="hero">
      <div class="eyebrow">EQlesia / DevTemplate</div>
      <h1>DevTemplate</h1>
      <p>開発用テンプレート・仕様書・設計ドキュメント集</p>
    </div>
    <div class="stats-bar">
      <div class="stat"><div class="k">フォルダ数</div><div class="v">TMPL_FOLDER_COUNT</div></div>
      <div class="stat"><div class="k">総ファイル数</div><div class="v">TMPL_TOTAL_FILES</div></div>
      <div class="stat"><div class="k">最終更新</div><div class="v" style="font-size:13px;padding-top:4px">TMPL_LAST_UPDATED</div></div>
    </div>
    <div class="folder-grid">TMPL_FOLDER_CARDS</div>
    <div class="page-footer">
      <span>EQlesia/DevTemplate</span>
      <span>自動生成 by GitHub Actions</span>
    </div>
  </div>
</div>
</body>
</html>
"""

# ─── ユーティリティ ────────────────────────────────────────

def extract_title(html_path: Path) -> str:
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

# ─── サブフォルダ index.html 生成 ─────────────────────────

def build_file_card(html_file: Path, folder_path: Path) -> str:
    name  = html_file.name
    title = extract_title(html_file)
    mtime = fmt_dt(file_mtime(html_file))
    rel   = html_file.relative_to(folder_path)
    return (
        f'<a class="file-card" href="{rel}">'
        f'<div class="file-icon">📄</div>'
        f'<div class="file-info">'
        f'<div class="file-name">{name}</div>'
        f'<div class="file-title">{title}</div>'
        f'<div class="file-meta">更新: {mtime}</div>'
        f'</div><div class="file-arrow">→</div></a>'
    )

def build_nav_link(html_file: Path) -> str:
    name  = html_file.name
    title = extract_title(html_file)
    short = title[:28] + '…' if len(title) > 30 else title
    return f'<a class="nav-link" href="{name}" title="{title}"><span>📄</span>{short}</a>'

def generate_folder_index(folder_path: Path, meta: dict) -> str:
    html_files = sorted(
        [f for f in folder_path.glob('*.html') if f.name not in EXCLUDE_FILES],
        key=lambda f: f.name
    )
    now  = now_str()
    last = fmt_dt(max((file_mtime(f) for f in html_files),
                      default=datetime.now(timezone.utc))) if html_files else now
    cards     = ''.join(build_file_card(f, folder_path) for f in html_files) if html_files \
                else '<div class="empty"><div class="icon">📭</div><p>ファイルがありません</p></div>'
    nav_items = ''.join(build_nav_link(f) for f in html_files)

    return (FOLDER_INDEX_TEMPLATE
        .replace('TMPL_FOLDER_NAME',    folder_path.name)
        .replace('TMPL_FILE_CARDS',     cards)
        .replace('TMPL_FILE_NAV_ITEMS', nav_items)
        .replace('TMPL_FILE_COUNT',     str(len(html_files)))
        .replace('TMPL_UPDATED_AT',     now)
        .replace('TMPL_LAST_UPDATED',   last)
        .replace('TMPL_FOLDER_DESC',    meta.get('desc', '')))

# ─── ルート index.html 生成 ───────────────────────────────

def build_folder_card(folder_path: Path, meta: dict, html_files: list) -> str:
    name  = folder_path.name
    count = len(html_files)
    chips = ''.join(f'<span class="folder-file-chip">{f.name}</span>' for f in html_files[:6])
    if count > 6:
        chips += f'<span class="folder-file-chip">+{count - 6}</span>'
    return (
        f'<a class="folder-card" href="{name}/index.html">'
        f'<div class="folder-stripe"></div>'
        f'<div class="folder-body">'
        f'<div class="folder-top">'
        f'<div class="folder-icon">{meta["icon"]}</div>'
        f'<span class="folder-name">{name}/</span>'
        f'<span class="folder-count">{count} files</span>'
        f'</div>'
        f'<div class="folder-desc">{meta["desc"]}</div>'
        f'<div class="folder-files">{chips}</div>'
        f'</div><div class="folder-arrow">→</div></a>'
    )

def build_folder_nav(folder_path: Path, meta: dict) -> str:
    return (f'<a class="nav-item" href="{folder_path.name}/index.html">'
            f'{meta["icon"]} {folder_path.name}</a>')

def generate_root_index(folders: list) -> str:
    now         = now_str()
    total_files = sum(len(files) for _, _, files in folders)
    all_mtimes  = [file_mtime(f) for _, _, files in folders for f in files]
    last        = fmt_dt(max(all_mtimes)) if all_mtimes else now
    cards       = ''.join(build_folder_card(p, m, f) for p, m, f in folders)
    nav_items   = ''.join(build_folder_nav(p, m)      for p, m, _ in folders)

    return (ROOT_INDEX_TEMPLATE
        .replace('TMPL_FOLDER_CARDS',     cards)
        .replace('TMPL_FOLDER_NAV_ITEMS', nav_items)
        .replace('TMPL_FOLDER_COUNT',     str(len(folders)))
        .replace('TMPL_TOTAL_FILES',      str(total_files))
        .replace('TMPL_UPDATED_AT',       now)
        .replace('TMPL_LAST_UPDATED',     last))

# ─── メイン ───────────────────────────────────────────────

def main():
    print(f'REPO_ROOT: {REPO_ROOT}')
    folders_data = []

    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in EXCLUDE_DIRS or entry.name.startswith('.'):
            continue

        html_files = sorted(
            [f for f in entry.glob('*.html') if f.name not in EXCLUDE_FILES],
            key=lambda f: f.name
        )
        print(f'  scan: {entry.name}/  → {len(html_files)} html files')
        if not html_files:
            continue

        meta = FOLDER_META.get(entry.name, dict(DEFAULT_META))
        folders_data.append((entry, meta, html_files))

        out = entry / 'index.html'
        out.write_text(generate_folder_index(entry, meta), encoding='utf-8')
        print(f'  ✅ 生成: {out.relative_to(REPO_ROOT)}')

    # ルート index.html
    root_out = REPO_ROOT / 'index.html'
    root_out.write_text(generate_root_index(folders_data), encoding='utf-8')
    print(f'  ✅ 生成: index.html  ({len(folders_data)} folders)')

if __name__ == '__main__':
    main()
