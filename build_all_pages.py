import json
import os
import re

OUTPUT_DIR = r"C:\Users\Gordon\.gemini\antigravity\scratch\acnh-wallpaper-assets"
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
os.makedirs(PAGES_DIR, exist_ok=True)

def generate_rug_grid_svg(grid_size_str, size=52):
    m = re.search(r'(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)', grid_size_str)
    if m:
        w = float(m.group(1))
        h = float(m.group(2))
    else:
        w, h = 3.0, 3.0
    rw = w * 10
    rh = h * 10
    rx = 0
    ry = 50 - rh
    svg = f"""<svg class="rug-grid-svg" width="{size}" height="{size}" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" style="display: block;">
    <rect x="0" y="0" width="50" height="50" fill="#faeedb" />
    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="#f29b0a" />
    <line x1="10" y1="0" x2="10" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="20" y1="0" x2="20" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="30" y1="0" x2="30" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="40" y1="0" x2="40" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="0" y1="10" x2="50" y2="10" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="0" y1="20" x2="50" y2="20" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="0" y1="30" x2="50" y2="30" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <line x1="0" y1="40" x2="50" y2="40" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" />
    <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="#68340d" stroke-width="1.8" />
    <rect x="0.9" y="0.9" width="48.2" height="48.2" fill="none" stroke="#68340d" stroke-width="1.8" />
</svg>"""
    return svg

def generate_gallery_page(
    items_data,
    page_type, # "wallpapers", "floors", "rugs"
    page_title, # "壁紙圖庫全輯", "地板圖庫全輯", "地毯圖庫全輯"
    page_icon, # "🖼️", "🪵", "🧶"
    storage_key, # "acnh_wallpaper_favorites_v1", ...
    out_filename, # "wallpapers.html", ...
    stats_counts, # dict of total counts for nav
):
    # Sorting logic
    if page_type == "rugs":
        def rug_sort_key(item):
            grid = item.get("grid_size", "")
            m = re.search(r'(\d+(?:\.\d+)?)\s*[×xX]\s*(\d+(?:\.\d+)?)', grid)
            if m:
                w = float(m.group(1))
                h = float(m.group(2))
                area = w * h
            else:
                w, h, area = 0, 0, 0
            return (-area, -max(w, h), -min(w, h), item.get("name_en", "").lower())
        sorted_items = sorted(items_data, key=rug_sort_key)
    else:
        # Sort: items with in-game screenshots first, then alphabetically by English name
        sorted_items = sorted(items_data, key=lambda x: (not x.get("has_in_game_screenshot", False), x.get("name_en", "").lower()))
    
    for idx, it in enumerate(sorted_items):
        it["index"] = idx

    cards_html = []
    has_screenshot_count = sum(1 for x in sorted_items if x.get("has_in_game_screenshot"))
    no_screenshot_count = len(sorted_items) - has_screenshot_count
    
    for idx, item in enumerate(sorted_items):
        rel_path = item.get("local_rel_path", "")
        name_zh = item.get("name_zh", "")
        name_en = item.get("name_en", "")
        name_ja = item.get("name_ja", "")
        has_shot = item.get("has_in_game_screenshot", False)
        width = item.get("width", 0)
        height = item.get("height", 0)
        
        if page_type == "rugs":
            grid_sz = item.get("grid_size", "")
            sz_cat = item.get("size_category", "")
            sz_lbl = item.get("size_label", "")
            filter_type = sz_cat
            dim_text = f"佔地尺寸：<strong>{grid_sz}</strong>（{sz_lbl}）"
            rug_grid_box = f'<div class="rug-grid-box" title="佔地規格：{grid_sz}（{sz_lbl}）">{generate_rug_grid_svg(grid_sz, size=52)}</div>'
        else:
            filter_type = "screenshot" if has_shot else "icon"
            dim_text = f"{width} &times; {height} px"
            rug_grid_box = ""
        
        # Escape quotes
        safe_en = name_en.replace("'", "\\'")
        
        card = f"""
        <div class="card" data-index="{idx}" data-type="{filter_type}" data-name="{name_zh.lower()} {name_en.lower()} {name_ja.lower()}" onclick="openLightboxByIndex({idx})">
            <button class="card-fav-btn" id="fav-btn-{idx}" onclick="toggleFavorite('{safe_en}', event)" title="加入我的最愛"><svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg></button>
            <div class="img-container">
                <img src="{rel_path}" alt="{name_zh}" loading="lazy">
            </div>
            <div class="info">
                <div class="info-content">
                    <div class="info-texts">
                        <h3 class="name-zh">{name_zh}</h3>
                        <p class="name-en">{name_en}</p>
                        <p class="name-ja">{name_ja}</p>
                        <p class="dim">{dim_text}</p>
                    </div>
                    {rug_grid_box}
                </div>
            </div>
        </div>
        """
        cards_html.append(card)
        
    cards_str = "\n".join(cards_html)
    gallery_data_json = json.dumps(sorted_items, ensure_ascii=False)
    
    # Nav active classes
    nav_wall_active = "active" if page_type == "wallpapers" else ""
    nav_floor_active = "active" if page_type == "floors" else ""
    nav_rug_active = "active" if page_type == "rugs" else ""

    # Filter buttons: rugs have L/M/S size filters
    if page_type == "rugs":
        count_L = sum(1 for x in sorted_items if x.get("size_category") == "L")
        count_M = sum(1 for x in sorted_items if x.get("size_category") == "M")
        count_S = sum(1 for x in sorted_items if x.get("size_category") == "S")
        filter_buttons_html = f"""
            <button class="filter-btn active" onclick="setFilter('all', this)">全部 ({len(sorted_items)})</button>
            <button class="filter-btn" onclick="setFilter('L', this)">大型 L ({count_L})</button>
            <button class="filter-btn" onclick="setFilter('M', this)">中型 M ({count_M})</button>
            <button class="filter-btn" onclick="setFilter('S', this)">小型 S ({count_S})</button>
            <button class="filter-btn fav-filter-btn" id="favFilterBtn" onclick="setFilter('favorite', this)">♥ 我的最愛 (<span id="favCount">0</span>)</button>
            <button class="filter-btn clear-fav-btn" id="clearFavBtn" onclick="clearFavorites()" title="清空所有已收藏的項目" style="display: none;">🗑 清空最愛</button>
        """
    else:
        filter_buttons_html = f"""
            <button class="filter-btn active" onclick="setFilter('all', this)">全部 ({len(sorted_items)})</button>
            <button class="filter-btn" onclick="setFilter('screenshot', this)">實景大圖 ({has_screenshot_count})</button>
            <button class="filter-btn" onclick="setFilter('icon', this)">尚無大圖 ({no_screenshot_count})</button>
            <button class="filter-btn fav-filter-btn" id="favFilterBtn" onclick="setFilter('favorite', this)">♥ 我的最愛 (<span id="favCount">0</span>)</button>
            <button class="filter-btn clear-fav-btn" id="clearFavBtn" onclick="clearFavorites()" title="清空所有已收藏的項目" style="display: none;">🗑 清空最愛</button>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>集合啦！動物森友會 - {page_title}</title>
    <style>
        :root {{
            --primary: #2b5c5f;
            --primary-light: #3d797d;
            --bg-color: #f6f8f5;
            --card-bg: #ffffff;
            --text-main: #333333;
            --text-sub: #666666;
            --accent: #f5a623;
            --accent-red: #ff4757;
            --tag-green: #2a9d8f;
            --tag-orange: #e76f51;
            --nav-bg: #ffffff;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        /* Top Navigation Bar */
        .site-nav {{
            background: var(--nav-bg);
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: var(--primary);
            font-size: 1.25rem;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        .nav-links {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .nav-link {{
            text-decoration: none;
            color: var(--text-sub);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .nav-link:hover {{
            color: var(--primary);
            background: #eef3ef;
        }}
        .nav-link.active {{
            background: var(--primary);
            color: #ffffff;
        }}

        /* Main Container */
        .main-wrapper {{
            flex: 1;
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }}

        header {{
            margin-bottom: 24px;
            text-align: center;
        }}
        h1 {{
            font-size: 2.1rem;
            color: var(--primary);
            margin-bottom: 18px;
            letter-spacing: 0.5px;
        }}
        .controls {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 24px;
            align-items: center;
        }}
        .search-box {{
            padding: 10px 18px;
            font-size: 1rem;
            border: 2px solid #ddd;
            border-radius: 24px;
            width: 320px;
            outline: none;
            transition: all 0.2s;
            background: #fff;
        }}
        .search-box:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 8px rgba(43,92,95,0.2);
        }}
        .filter-btn {{
            padding: 9px 18px;
            border: 1px solid #ccc;
            background-color: #fff;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.92rem;
            font-weight: 500;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .filter-btn:hover {{
            background-color: #eee;
        }}
        .filter-btn.active {{
            background-color: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}
        .fav-filter-btn.active {{
            background-color: var(--accent-red);
            border-color: var(--accent-red);
            color: #fff;
        }}
        .clear-fav-btn {{
            border-color: #ffd2d2;
            color: #d63031;
            background: #fff5f5;
        }}
        .clear-fav-btn:hover {{
            background: #ffe3e3;
            border-color: #ff7675;
        }}
        
        /* Grid Layout */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
        }}
        .card {{
            background-color: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            cursor: pointer;
            position: relative;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }}
        .card-fav-btn {{
            position: absolute;
            top: 10px;
            left: 10px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.92);
            border: none;
            outline: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            padding: 0;
            margin: 0;
        }}
        .card-fav-btn svg {{
            width: 19px;
            height: 19px;
            display: block;
            pointer-events: none;
            fill: none;
            stroke: #718096;
            stroke-width: 2.2;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: transform 0.15s ease, fill 0.15s ease, stroke 0.15s ease;
        }}
        .card-fav-btn:hover {{
            transform: scale(1.15);
            background: #ffffff;
        }}
        .card-fav-btn:hover svg {{
            stroke: var(--accent-red);
        }}
        .card-fav-btn.active {{
            background: #ffffff;
        }}
        .card-fav-btn.active svg {{
            fill: var(--accent-red);
            stroke: var(--accent-red);
        }}
        .img-container {{
            width: 100%;
            height: 200px;
            background-color: #e9ecef;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        .img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }}
        .card:hover .img-container img {{
            transform: scale(1.05);
        }}
        .badge {{
            position: absolute;
            bottom: 8px;
            right: 8px;
            padding: 4px 8px;
            font-size: 0.72rem;
            border-radius: 12px;
            color: #fff;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.25);
        }}
        .badge-screenshot {{ background-color: var(--tag-green); }}
        .badge-icon {{ background-color: var(--tag-orange); }}
        .badge-rug-size {{ background-color: var(--primary); }}
        .info {{
            padding: 14px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}
        .info-content {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            gap: 10px;
            width: 100%;
            height: 100%;
        }}
        .info-texts {{
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
        }}
        .name-zh {{
            font-size: 1.15rem;
            font-weight: bold;
            color: var(--text-main);
            margin-bottom: 4px;
        }}
        .name-en {{
            font-size: 0.9rem;
            color: var(--text-sub);
            margin-bottom: 2px;
        }}
        .name-ja {{
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 8px;
        }}
        .dim {{
            font-size: 0.8rem;
            color: #aaa;
            margin-top: auto;
        }}
        .dim strong {{
            color: var(--primary);
            font-size: 0.85rem;
        }}
        .rug-grid-box {{
            background: #faeedb;
            padding: 4px;
            border-radius: 6px;
            box-shadow: 0 1px 4px rgba(104, 52, 13, 0.15);
            flex-shrink: 0;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2px;
            border: 1px solid rgba(104, 52, 13, 0.2);
            transition: transform 0.2s;
        }}
        .card:hover .rug-grid-box {{
            transform: scale(1.05);
        }}
        .lightbox-rug-grid-wrap {{
            background: #faeedb;
            padding: 4px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
            display: inline-flex;
            flex-shrink: 0;
            border: 1px solid rgba(104, 52, 13, 0.3);
        }}

        /* Empty State */
        .empty-state {{
            max-width: 500px;
            margin: 60px auto;
            text-align: center;
            padding: 32px 20px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        .empty-state h3 {{
            color: var(--primary);
            font-size: 1.3rem;
            margin-bottom: 8px;
        }}
        .empty-state p {{
            color: var(--text-sub);
            font-size: 0.95rem;
            line-height: 1.6;
        }}

        /* Enhanced Lightbox Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(10, 12, 16, 0.93);
            z-index: 999;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            user-select: none;
        }}
        .modal.active {{ display: flex; }}

        .modal-close {{
            position: absolute;
            top: 18px;
            right: 28px;
            color: #fff;
            font-size: 2.4rem;
            cursor: pointer;
            transition: all 0.2s;
            z-index: 1002;
            background: none;
            border: none;
            outline: none;
            line-height: 1;
        }}
        .modal-close:hover {{
            color: var(--accent);
            transform: scale(1.15);
        }}

        /* Navigation Zones & Buttons with Expanded Hit Areas */
        .nav-zone {{
            position: fixed;
            top: 70px;
            bottom: 85px;
            width: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1001;
            transition: background 0.2s;
            user-select: none;
        }}
        .prev-zone {{ left: 0; }}
        .next-zone {{ right: 0; }}
        .nav-zone:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}

        .nav-btn {{
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.16);
            border: 2px solid rgba(255, 255, 255, 0.45);
            color: #ffffff;
            font-size: 2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            backdrop-filter: blur(8px);
            outline: none;
            position: relative;
        }}
        .nav-btn::before {{
            content: '';
            position: absolute;
            top: -24px;
            bottom: -24px;
            left: -24px;
            right: -24px;
            border-radius: 50%;
            cursor: pointer;
        }}
        .nav-zone:hover .nav-btn, .nav-btn:hover {{
            background: rgba(255, 255, 255, 0.38);
            border-color: #ffffff;
            transform: scale(1.15);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.35);
        }}

        /* Main Image & Caption */
        .lightbox-main {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            max-height: calc(100vh - 160px);
            z-index: 1000;
            padding: 0 80px;
        }}
        .lightbox-img-wrapper {{
            display: flex;
            align-items: center;
            justify-content: center;
            max-width: 90vw;
            max-height: calc(100vh - 240px);
        }}
        .lightbox-img-wrapper img {{
            max-width: 100%;
            max-height: calc(100vh - 240px);
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }}
        .lightbox-info {{
            margin-top: 14px;
            text-align: center;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }}
        .modal-caption {{
            font-size: 1.15rem;
        }}
        .lightbox-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .lightbox-fav-btn {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.4);
            color: #fff;
            padding: 6px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.95rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}
        .lightbox-fav-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        .lightbox-fav-btn.active {{
            background: var(--accent-red);
            border-color: var(--accent-red);
            color: #fff;
        }}
        .lightbox-counter {{
            font-size: 0.88rem;
            color: #aaa;
        }}

        /* Bottom Thumbnail Strip */
        .thumb-strip-wrapper {{
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1002;
            background: rgba(20, 24, 30, 0.75);
            padding: 6px 14px;
            border-radius: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            max-width: 92vw;
            overflow-x: auto;
        }}
        .thumb-strip {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .thumb-item {{
            width: 48px;
            height: 48px;
            border-radius: 8px;
            overflow: hidden;
            cursor: pointer;
            opacity: 0.55;
            transition: all 0.2s;
            border: 2px solid transparent;
            flex-shrink: 0;
            background: #222;
        }}
        .thumb-item img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .thumb-item:hover {{
            opacity: 0.9;
            transform: scale(1.08);
        }}
        .thumb-item.active {{
            opacity: 1;
            border-color: #2a9d8f;
            transform: scale(1.16);
            box-shadow: 0 0 14px rgba(42, 157, 143, 0.9);
            z-index: 2;
        }}
        .thumb-strip-arrow {{
            color: #888;
            font-size: 0.85rem;
            padding: 0 4px;
            user-select: none;
        }}

        /* Confirm Modal Dialog */
        .confirm-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(18, 30, 24, 0.65);
            backdrop-filter: blur(6px);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
        }}
        .confirm-overlay.active {{
            opacity: 1;
        }}
        .confirm-box {{
            background: #ffffff;
            border-radius: 20px;
            padding: 30px 28px 26px;
            max-width: 400px;
            width: 88%;
            text-align: center;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);
            transform: scale(0.92);
            transition: transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            user-select: none;
        }}
        .confirm-overlay.active .confirm-box {{
            transform: scale(1);
        }}
        .confirm-icon {{
            font-size: 2.6rem;
            line-height: 1;
            margin-bottom: 12px;
            display: inline-block;
        }}
        .confirm-title {{
            font-size: 1.3rem;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 10px;
        }}
        .confirm-desc {{
            font-size: 0.95rem;
            color: var(--text-sub);
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .confirm-desc strong {{
            color: var(--accent-red);
            font-size: 1.15rem;
        }}
        .confirm-actions {{
            display: flex;
            gap: 12px;
            justify-content: center;
        }}
        .confirm-btn {{
            padding: 10px 22px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            outline: none;
            transition: all 0.2s ease;
        }}
        .confirm-btn-cancel {{
            background: #eef2ec;
            color: #556052;
        }}
        .confirm-btn-cancel:hover {{
            background: #dfe5dc;
            color: #2b3329;
            transform: translateY(-1px);
        }}
        .confirm-btn-danger {{
            background: var(--accent-red);
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
        }}
        .confirm-btn-danger:hover {{
            background: #e03746;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(255, 71, 87, 0.4);
        }}

        /* Site Footer */
        .site-footer {{
            background: #ffffff;
            border-top: 1px solid rgba(0, 0, 0, 0.08);
            padding: 24px;
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-sub);
            margin-top: 40px;
            line-height: 1.6;
        }}
        .site-footer a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}
        .site-footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="site-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-brand">動森室內圖庫</a>
            <div class="nav-links">
                <a href="index.html" class="nav-link">首頁導覽</a>
                <a href="wallpapers.html" class="nav-link {nav_wall_active}">壁紙 ({stats_counts.get('wallpapers', 312)})</a>
                <a href="floors.html" class="nav-link {nav_floor_active}">地板 ({stats_counts.get('floors', 215)})</a>
                <a href="rugs.html" class="nav-link {nav_rug_active}">地毯 ({stats_counts.get('rugs', 210)})</a>
            </div>
        </div>
    </nav>

    <div class="main-wrapper">
        <header>
            <h1>集合啦！動物森友會 - {page_title}</h1>
            <div class="controls">
                <input type="text" id="search" class="search-box" placeholder="搜尋中文、英文、日文名稱..." oninput="filterCards()">
                {filter_buttons_html}
            </div>
        </header>

        <div class="empty-state" id="emptyState" style="display: none;">
            <h3>沒有找到相符的項目</h3>
            <p>請嘗試其他搜尋關鍵字或切換篩選分類標籤。</p>
        </div>

        <div class="grid" id="galleryGrid">
            {cards_str}
        </div>
    </div>

    <!-- Enhanced Lightbox Modal -->
    <div class="modal" id="lightboxModal" onclick="closeLightbox(event)">
        <button class="modal-close" onclick="closeLightbox(event)" title="關閉 (Esc)">&times;</button>
        
        <!-- Left & Right Navigation Zones & Buttons -->
        <div class="nav-zone prev-zone" onclick="navigateLightbox(-1, event)" title="上一張 (← 方向鍵)">
            <button class="nav-btn prev-btn" id="prevBtn" onclick="navigateLightbox(-1, event)">&#10094;</button>
        </div>
        <div class="nav-zone next-zone" onclick="navigateLightbox(1, event)" title="下一張 (→ 方向鍵)">
            <button class="nav-btn next-btn" id="nextBtn" onclick="navigateLightbox(1, event)">&#10095;</button>
        </div>
        
        <!-- Center Image & Info -->
        <div class="lightbox-main" onclick="event.stopPropagation()">
            <div class="lightbox-img-wrapper">
                <img id="lightboxImg" src="" alt="">
            </div>
            <div class="lightbox-info">
                <div class="modal-caption" id="lightboxCaption"></div>
                <div class="lightbox-actions">
                    <button class="lightbox-fav-btn" id="lightboxFavBtn" onclick="toggleFavoriteCurrent(event)">
                        <span id="lightboxFavIcon"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg></span> <span id="lightboxFavText">收藏</span>
                    </button>
                    <div class="lightbox-counter" id="lightboxCounter"></div>
                </div>
            </div>
        </div>

        <!-- Bottom Thumbnail Strip / Pager -->
        <div class="thumb-strip-wrapper" onclick="event.stopPropagation()">
            <div class="thumb-strip" id="thumbStrip"></div>
        </div>
    </div>

    <!-- Custom Style Confirm Dialog -->
    <div class="confirm-overlay" id="confirmModal" onclick="closeConfirmModal(event)">
        <div class="confirm-box" onclick="event.stopPropagation()">
            <div class="confirm-icon">🗑️</div>
            <div class="confirm-title">清空我的最愛</div>
            <div class="confirm-desc">
                確定要清空已收藏的 <strong id="confirmFavCount">0</strong> 款項目嗎？<br>
                清空後將無法復原。
            </div>
            <div class="confirm-actions">
                <button class="confirm-btn confirm-btn-cancel" onclick="closeConfirmModal()">取消</button>
                <button class="confirm-btn confirm-btn-danger" onclick="executeClearFavorites()">確認清空</button>
            </div>
        </div>
    </div>

    <!-- Site Footer with Image Sources -->
    <footer class="site-footer">
        <p>資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)</p>
        <p style="margin-top: 6px; font-size: 0.82rem; color: #88998a;">非官方社群圖庫工具，僅供個人鑑賞與交流用途。</p>
    </footer>

    <script>
        const galleryData = {gallery_data_json};
        const STORAGE_KEY = '{storage_key}';
        let favorites = new Set();
        let currentFilter = 'all';
        let filteredIndices = galleryData.map((_, i) => i);
        let currentPos = 0; // index in filteredIndices

        function loadFavorites() {{
            try {{
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {{
                    favorites = new Set(JSON.parse(saved));
                }}
            }} catch (e) {{
                console.error("Failed to load favorites", e);
            }}
            updateFavUI();
        }}

        function saveFavorites() {{
            try {{
                localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(favorites)));
            }} catch (e) {{
                console.error("Failed to save favorites", e);
            }}
            updateFavUI();
        }}

        function toggleFavorite(id, event) {{
            if (event) event.stopPropagation();
            if (favorites.has(id)) {{
                favorites.delete(id);
            }} else {{
                favorites.add(id);
            }}
            saveFavorites();
            if (currentFilter === 'favorite') {{
                filterCards();
            }}
        }}

        function toggleFavoriteCurrent(event) {{
            if (event) event.stopPropagation();
            if (filteredIndices.length === 0) return;
            const item = galleryData[filteredIndices[currentPos]];
            toggleFavorite(item.name_en, event);
            updateLightboxFavBtn();
        }}

        function clearFavorites() {{
            if (favorites.size === 0) return;
            document.getElementById('confirmFavCount').textContent = favorites.size;
            const modal = document.getElementById('confirmModal');
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('active'), 10);
        }}

        function closeConfirmModal(event) {{
            if (event && event.target && event.target.id !== 'confirmModal' && !event.target.classList.contains('confirm-btn-cancel')) {{
                return;
            }}
            const modal = document.getElementById('confirmModal');
            modal.classList.remove('active');
            setTimeout(() => {{
                modal.style.display = 'none';
            }}, 200);
        }}

        function executeClearFavorites() {{
            favorites.clear();
            saveFavorites();
            closeConfirmModal();
            if (currentFilter === 'favorite') {{
                filterCards();
            }}
        }}

        function updateFavUI() {{
            const count = favorites.size;
            const countSpan = document.getElementById('favCount');
            if (countSpan) countSpan.textContent = count;
            
            const clearBtn = document.getElementById('clearFavBtn');
            if (clearBtn) {{
                clearBtn.style.display = count > 0 ? 'inline-flex' : 'none';
            }}

            galleryData.forEach((item, idx) => {{
                const btn = document.getElementById(`fav-btn-${{idx}}`);
                if (btn) {{
                    const isFav = favorites.has(item.name_en);
                    btn.classList.toggle('active', isFav);
                    btn.title = isFav ? '取消收藏' : '加入我的最愛';
                }}
            }});
            updateLightboxFavBtn();
        }}

        function updateLightboxFavBtn() {{
            const btn = document.getElementById('lightboxFavBtn');
            const icon = document.getElementById('lightboxFavIcon');
            const text = document.getElementById('lightboxFavText');
            if (!btn || filteredIndices.length === 0) return;
            const item = galleryData[filteredIndices[currentPos]];
            const isFav = favorites.has(item.name_en);
            btn.classList.toggle('active', isFav);
            if (icon) {{
                icon.innerHTML = isFav 
                    ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
                    : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
            }}
            if (text) {{
                text.textContent = isFav ? '已收藏' : '加入最愛';
            }}
            btn.title = isFav ? '點擊取消收藏' : '點擊加入我的最愛';
        }}

        function setFilter(type, btn) {{
            currentFilter = type;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCards();
        }}

        function filterCards() {{
            const query = document.getElementById('search').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.card');
            filteredIndices = [];
            
            cards.forEach((card, idx) => {{
                const item = galleryData[idx];
                const type = card.getAttribute('data-type');
                const name = card.getAttribute('data-name');
                const isFav = favorites.has(item.name_en);

                let matchesType = false;
                if (currentFilter === 'all') matchesType = true;
                else if (currentFilter === 'screenshot') matchesType = (type === 'screenshot');
                else if (currentFilter === 'icon') matchesType = (type === 'icon');
                else if (currentFilter === 'L' || currentFilter === 'M' || currentFilter === 'S') matchesType = (type === currentFilter);
                else if (currentFilter === 'favorite') matchesType = isFav;

                const matchesQuery = !query || name.includes(query);
                if (matchesType && matchesQuery) {{
                    card.style.display = 'flex';
                    filteredIndices.push(idx);
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            const emptyState = document.getElementById('emptyState');
            if (filteredIndices.length === 0) {{
                emptyState.style.display = 'block';
            }} else {{
                emptyState.style.display = 'none';
            }}
        }}

        function openLightboxByIndex(itemIndex) {{
            const pos = filteredIndices.indexOf(itemIndex);
            if (pos !== -1) {{
                currentPos = pos;
            }} else {{
                currentPos = 0;
            }}
            updateLightbox();
            document.getElementById('lightboxModal').classList.add('active');
        }}

        function getRugGridSvg(gridSize, size) {{
            size = size || 48;
            var m = (gridSize || '').match(/(\\d+(?:\\.\\d+)?)\\s*[×xX]\\s*(\\d+(?:\\.\\d+)?)/);
            var w = m ? parseFloat(m[1]) : 3;
            var h = m ? parseFloat(m[2]) : 3;
            var rw = w * 10;
            var rh = h * 10;
            var rx = 0;
            var ry = 50 - rh;
            return `<div class="lightbox-rug-grid-wrap"><svg class="rug-grid-svg" width="${{size}}" height="${{size}}" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" style="display:block;"><rect x="0" y="0" width="50" height="50" fill="#faeedb" /><rect x="${{rx}}" y="${{ry}}" width="${{rw}}" height="${{rh}}" fill="#f29b0a" /><line x1="10" y1="0" x2="10" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="20" y1="0" x2="20" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="30" y1="0" x2="30" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="40" y1="0" x2="40" y2="50" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="0" y1="10" x2="50" y2="10" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="0" y1="20" x2="50" y2="20" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="0" y1="30" x2="50" y2="30" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><line x1="0" y1="40" x2="50" y2="40" stroke="#87532b" stroke-width="0.9" stroke-dasharray="1.5,1.5" /><rect x="${{rx}}" y="${{ry}}" width="${{rw}}" height="${{rh}}" fill="none" stroke="#68340d" stroke-width="1.8" /><rect x="0.9" y="0.9" width="48.2" height="48.2" fill="none" stroke="#68340d" stroke-width="1.8" /></svg></div>`;
        }}

        function updateLightbox() {{
            if (filteredIndices.length === 0) return;
            const itemIndex = filteredIndices[currentPos];
            const item = galleryData[itemIndex];

            const img = document.getElementById('lightboxImg');
            img.src = item.local_rel_path;
            img.alt = item.name_zh;

            let detailInfo = '';
            if (item.grid_size) {{
                detailInfo = `
                    <div style="display:flex; align-items:center; justify-content:center; gap:14px; margin-top:8px;">
                        ${{getRugGridSvg(item.grid_size, 50)}}
                        <div style="text-align:left; font-size:0.95rem; color:#fff;">
                            <div>佔地尺寸: <strong>${{item.grid_size}}</strong>（${{item.size_label}}）</div>
                            <div style="font-size:0.8rem; color:#bbb; margin-top:2px;">房間 5×5 基準網格</div>
                        </div>
                    </div>`;
            }} else {{
                detailInfo = `<div style="font-size: 0.85rem; color: #aaa; margin-top: 4px;">解析度: ${{item.width}} &times; ${{item.height}} px</div>`;
            }}

            document.getElementById('lightboxCaption').innerHTML = 
                `<strong>${{item.name_zh}}</strong> / ${{item.name_en}} (${{item.name_ja}})` + detailInfo;

            document.getElementById('lightboxCounter').textContent = `${{currentPos + 1}} / ${{filteredIndices.length}}`;

            updateLightboxFavBtn();
            renderThumbnailStrip();

            // Preload adjacent images for butter-smooth keyboard navigation
            if (currentPos + 1 < filteredIndices.length) {{
                const nextItem = galleryData[filteredIndices[currentPos + 1]];
                if (nextItem && nextItem.local_rel_path) {{
                    const nextImg = new Image();
                    nextImg.src = nextItem.local_rel_path;
                }}
            }}
            if (currentPos - 1 >= 0) {{
                const prevItem = galleryData[filteredIndices[currentPos - 1]];
                if (prevItem && prevItem.local_rel_path) {{
                    const prevImg = new Image();
                    prevImg.src = prevItem.local_rel_path;
                }}
            }}
        }}

        function renderThumbnailStrip() {{
            const strip = document.getElementById('thumbStrip');
            strip.innerHTML = '';
            const total = filteredIndices.length;
            if (total <= 1) return;

            const windowSize = 7;
            const half = Math.floor(windowSize / 2);
            let start = currentPos - half;
            let end = currentPos + half;

            if (start < 0) {{
                end = Math.min(total - 1, end - start);
                start = 0;
            }}
            if (end >= total) {{
                start = Math.max(0, start - (end - total + 1));
                end = total - 1;
            }}

            if (start > 0) {{
                const indicator = document.createElement('span');
                indicator.className = 'thumb-strip-arrow';
                indicator.textContent = '◀';
                strip.appendChild(indicator);
            }}

            for (let pos = start; pos <= end; pos++) {{
                const idx = filteredIndices[pos];
                const it = galleryData[idx];
                const div = document.createElement('div');
                div.className = 'thumb-item' + (pos === currentPos ? ' active' : '');
                div.title = `${{it.name_zh}} (${{it.name_en}})`;
                div.onclick = (e) => {{
                    e.stopPropagation();
                    currentPos = pos;
                    updateLightbox();
                }};

                const thumbImg = document.createElement('img');
                thumbImg.src = it.local_rel_path;
                thumbImg.alt = it.name_zh;
                thumbImg.loading = 'lazy';
                div.appendChild(thumbImg);
                strip.appendChild(div);
            }}

            if (end < total - 1) {{
                const indicator = document.createElement('span');
                indicator.className = 'thumb-strip-arrow';
                indicator.textContent = '▶';
                strip.appendChild(indicator);
            }}
        }}

        function navigateLightbox(delta, event) {{
            if (event) event.stopPropagation();
            if (filteredIndices.length === 0) return;
            currentPos = (currentPos + delta + filteredIndices.length) % filteredIndices.length;
            updateLightbox();
        }}

        function closeLightbox(e) {{
            if (!e || e.target.id === 'lightboxModal' || e.target.classList.contains('modal-close')) {{
                document.getElementById('lightboxModal').classList.remove('active');
            }}
        }}

        // Keyboard navigation
        window.addEventListener('keydown', (e) => {{
            const confirmModal = document.getElementById('confirmModal');
            if (confirmModal && confirmModal.classList.contains('active')) {{
                if (e.key === 'Escape') {{
                    closeConfirmModal();
                }}
                return;
            }}
            const modal = document.getElementById('lightboxModal');
            if (!modal.classList.contains('active')) return;
            if (e.key === 'ArrowLeft') {{
                navigateLightbox(-1);
            }} else if (e.key === 'ArrowRight') {{
                navigateLightbox(1);
            }} else if (e.key === 'Escape') {{
                closeLightbox();
            }}
        }});

        // Initialize favorites on load
        loadFavorites();
    </script>
</body>
</html>
"""
    dest_path = os.path.join(PAGES_DIR, out_filename)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {dest_path}")
    return dest_path

def generate_index_page(stats_counts):
    index_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>集合啦！動物森友會 - 室內裝潢圖庫全輯 (壁紙 / 地板 / 地毯)</title>
    <style>
        :root {{
            --primary: #2b5c5f;
            --primary-light: #3d797d;
            --bg-color: #f6f8f5;
            --card-bg: #ffffff;
            --text-main: #333333;
            --text-sub: #556052;
            --accent: #f5a623;
            --accent-red: #ff4757;
            --tag-green: #2a9d8f;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        /* Top Navigation Bar */
        .site-nav {{
            background: #ffffff;
            border-bottom: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .nav-container {{
            max-width: 1300px;
            margin: 0 auto;
            padding: 14px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .nav-brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
            color: var(--primary);
            font-size: 1.3rem;
            font-weight: bold;
            letter-spacing: 0.5px;
        }}
        .nav-links {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .nav-link {{
            text-decoration: none;
            color: var(--text-sub);
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .nav-link:hover {{
            color: var(--primary);
            background: #eef3ef;
        }}
        .nav-link.active {{
            background: var(--primary);
            color: #ffffff;
        }}

        /* Hero Section */
        .hero {{
            text-align: center;
            padding: 60px 20px 40px;
            max-width: 900px;
            margin: 0 auto;
        }}
        .hero-badge {{
            display: inline-block;
            background: rgba(43, 92, 95, 0.1);
            color: var(--primary);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-bottom: 16px;
        }}
        .hero h1 {{
            font-size: 2.8rem;
            color: var(--primary);
            margin-bottom: 16px;
            line-height: 1.25;
            letter-spacing: 0.5px;
        }}
        .hero p {{
            font-size: 1.15rem;
            color: var(--text-sub);
            line-height: 1.7;
        }}

        /* Feature Cards Grid */
        .portal-grid {{
            max-width: 1200px;
            margin: 20px auto 60px;
            padding: 0 24px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 28px;
        }}
        .portal-card {{
            background: #ffffff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: inherit;
            border: 2px solid transparent;
            border-top: 6px solid var(--primary);
        }}
        .portal-card.wallpapers {{ border-top-color: #2a9d8f; }}
        .portal-card.floors {{ border-top-color: #8f654b; }}
        .portal-card.rugs {{ border-top-color: #e76f51; }}

        .portal-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
        }}
        .portal-card.wallpapers:hover {{ border-color: rgba(42, 157, 143, 0.25); border-top-color: #2a9d8f; }}
        .portal-card.floors:hover {{ border-color: rgba(143, 101, 75, 0.25); border-top-color: #8f654b; }}
        .portal-card.rugs:hover {{ border-color: rgba(231, 111, 81, 0.25); border-top-color: #e76f51; }}

        .portal-card.wallpapers .enter-btn {{ background: #2a9d8f; }}
        .portal-card.wallpapers:hover .enter-btn {{ background: #238276; }}
        .portal-card.floors .enter-btn {{ background: #8f654b; }}
        .portal-card.floors:hover .enter-btn {{ background: #735039; }}
        .portal-card.rugs .enter-btn {{ background: #e76f51; }}
        .portal-card.rugs:hover .enter-btn {{ background: #cf5538; }}
        .card-body {{
            padding: 28px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}
        .card-title {{
            font-size: 1.6rem;
            font-weight: bold;
            color: var(--primary);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .card-count {{
            font-size: 1.05rem;
            background: #eef3ef;
            color: var(--primary);
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
        }}
        .card-desc {{
            font-size: 0.95rem;
            color: var(--text-sub);
            line-height: 1.6;
            margin-bottom: 24px;
            flex-grow: 1;
        }}
        .card-specs {{
            display: flex;
            gap: 12px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .spec-tag {{
            font-size: 0.82rem;
            background: #f1f4f0;
            color: #556052;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 500;
        }}
        .enter-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: var(--primary);
            color: #ffffff;
            font-weight: bold;
            padding: 12px 20px;
            border-radius: 20px;
            transition: all 0.2s;
        }}
        .portal-card:hover .enter-btn {{
            background: var(--primary-light);
            box-shadow: 0 4px 14px rgba(43, 92, 95, 0.3);
        }}

        /* Highlights Section */
        .features {{
            background: #ffffff;
            border-radius: 24px;
            max-width: 1200px;
            margin: 0 auto 60px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }}
        .features-title {{
            text-align: center;
            font-size: 1.6rem;
            color: var(--primary);
            margin-bottom: 30px;
        }}
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 24px;
        }}
        .feature-item {{
            text-align: center;
            padding: 16px;
        }}
        .feature-icon {{
            font-size: 2.4rem;
            margin-bottom: 12px;
        }}
        .feature-name {{
            font-size: 1.15rem;
            font-weight: bold;
            color: var(--text-main);
            margin-bottom: 8px;
        }}
        .feature-desc {{
            font-size: 0.92rem;
            color: var(--text-sub);
            line-height: 1.6;
        }}

        /* Site Footer */
        .site-footer {{
            background: #ffffff;
            border-top: 1px solid rgba(0, 0, 0, 0.08);
            padding: 28px 20px;
            text-align: center;
            font-size: 0.92rem;
            color: var(--text-sub);
            margin-top: auto;
            line-height: 1.6;
        }}
        .site-footer a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}
        .site-footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="site-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-brand">動森室內圖庫</a>
            <div class="nav-links">
                <a href="index.html" class="nav-link active">首頁導覽</a>
                <a href="wallpapers.html" class="nav-link">壁紙 ({stats_counts.get('wallpapers', 312)})</a>
                <a href="floors.html" class="nav-link">地板 ({stats_counts.get('floors', 215)})</a>
                <a href="rugs.html" class="nav-link">地毯 ({stats_counts.get('rugs', 210)})</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero">
        <div class="hero-badge">Animal Crossing: New Horizons</div>
        <h1>集合啦！動物森友會<br>室內裝潢圖庫全輯</h1>
        <p>收錄全系列壁紙、地板與地毯的 1280x720 高清遊戲實景截圖與官方圖示。<br>支援實景大圖優先排序、即時搜尋、鍵盤方向鍵導航與離線個人最愛收藏。</p>
    </div>

    <!-- Portal Cards -->
    <div class="portal-grid">
        <!-- Wallpapers Card -->
        <a href="wallpapers.html" class="portal-card wallpapers">
            <div class="card-body">
                <div class="card-title">
                    <span>壁紙圖庫</span>
                    <span class="card-count">{stats_counts.get('wallpapers', 312)} 款</span>
                </div>
                <div class="card-desc">
                    涵蓋常規商店、駱嵐不可思議壁紙、非賣品活動獎勵與三麗鷗聯名款。260 款室內 1280x720 實拍大圖與 52 款官方高畫質備選圖示。
                </div>
                <div class="card-specs">
                    <span class="spec-tag">📸 260 款實景大圖</span>
                    <span class="spec-tag">✨ 實景優先 + 名稱排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn">
                    進入壁紙圖庫 ➔
                </div>
            </div>
        </a>

        <!-- Floors Card -->
        <a href="floors.html" class="portal-card floors">
            <div class="card-body">
                <div class="card-title">
                    <span>地板圖庫</span>
                    <span class="card-count">{stats_counts.get('floors', 215)} 款</span>
                </div>
                <div class="card-desc">
                    收錄實木拼花、復古磁磚、戶外自然場景、動態地磚與特殊材質地板。187 款室內鋪設 1280x720 實拍照與 28 款官方圖示。
                </div>
                <div class="card-specs">
                    <span class="spec-tag">📸 187 款實景大圖</span>
                    <span class="spec-tag">✨ 實景優先 + 名稱排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn">
                    進入地板圖庫 ➔
                </div>
            </div>
        </a>

        <!-- Rugs Card -->
        <a href="rugs.html" class="portal-card rugs">
            <div class="card-body">
                <div class="card-title">
                    <span>地毯圖庫</span>
                    <span class="card-count">{stats_counts.get('rugs', 210)} 款</span>
                </div>
                <div class="card-desc">
                    全系列大、中、小型與趣味特殊造型地毯，包括駱嵐限定地毯、蔬果造型地毯與季節限定圖騰。完整標註遊戲內 1×1 ~ 5×5 佔地尺寸與 S/M/L 篩選分類。
                </div>
                <div class="card-specs">
                    <span class="spec-tag">📐 S / M / L 尺寸篩選</span>
                    <span class="spec-tag">✨ 尺寸大到小 + 字母排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn">
                    進入地毯圖庫 ➔
                </div>
            </div>
        </a>
    </div>

    <!-- Highlights Section -->
    <div class="features">
        <h2 class="features-title">✨ 核心功能特色</h2>
        <div class="features-grid">
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <div class="feature-name">三語即時搜尋</div>
                <div class="feature-desc">支援繁體中文（台灣繁中）、英文以及日文原文即時過濾查找。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔤</div>
                <div class="feature-name">英文字母 A-Z 排序</div>
                <div class="feature-desc">依照英文名稱字母順序整齊編排，方便精確定位與參照社群資料。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">♥</div>
                <div class="feature-name">獨立最愛收藏</div>
                <div class="feature-desc">各類別具備獨立 LocalStorage 最愛清單，搭配自訂風格確認彈窗與快速切換。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🖼️</div>
                <div class="feature-name">大圖檢視與底部分頁</div>
                <div class="feature-desc">支援超廣角點擊感應立柱、全螢幕輪播切換與底部前伸後延縮圖分頁條。</div>
            </div>
        </div>
    </div>

    <!-- Site Footer with Image Sources -->
    <footer class="site-footer">
        <p>資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)</p>
        <p style="margin-top: 6px; font-size: 0.82rem; color: #88998a;">非官方社群圖庫工具，僅供個人鑑賞與交流用途。</p>
    </footer>
</body>
</html>
"""
    dest_path = os.path.join(PAGES_DIR, "index.html")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Generated {dest_path}")
    return dest_path

def build_all():
    # Load Wallpapers
    with open(os.path.join(OUTPUT_DIR, "wallpapers.json"), "r", encoding="utf-8") as f:
        wallpapers = json.load(f)
    
    # Load Floors
    floors_file = os.path.join(OUTPUT_DIR, "floors.json")
    floors = []
    if os.path.exists(floors_file):
        with open(floors_file, "r", encoding="utf-8") as f:
            floors = json.load(f)

    # Load Rugs
    rugs_file = os.path.join(OUTPUT_DIR, "rugs.json")
    rugs = []
    if os.path.exists(rugs_file):
        with open(rugs_file, "r", encoding="utf-8") as f:
            rugs = json.load(f)

    stats = {
        "wallpapers": len(wallpapers),
        "floors": len(floors) if floors else 215,
        "rugs": len(rugs) if rugs else 210
    }

    # Generate wallpapers.html in pages/
    generate_gallery_page(
        items_data=wallpapers,
        page_type="wallpapers",
        page_title="壁紙圖庫全輯",
        page_icon="🖼️",
        storage_key="acnh_wallpaper_favorites_v1",
        out_filename="wallpapers.html",
        stats_counts=stats
    )

    # Generate floors.html if floors data exists
    if floors:
        generate_gallery_page(
            items_data=floors,
            page_type="floors",
            page_title="地板圖庫全輯",
            page_icon="🪵",
            storage_key="acnh_flooring_favorites_v1",
            out_filename="floors.html",
            stats_counts=stats
        )

    # Generate rugs.html if rugs data exists
    if rugs:
        generate_gallery_page(
            items_data=rugs,
            page_type="rugs",
            page_title="地毯圖庫全輯",
            page_icon="🧶",
            storage_key="acnh_rug_favorites_v1",
            out_filename="rugs.html",
            stats_counts=stats
        )

    # Generate index.html (Portal / Guide page)
    generate_index_page(stats)
    print("All pages generated successfully!")

if __name__ == "__main__":
    build_all()
