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
                <div class="img-placeholder" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
                </div>
                <img src="{rel_path}" alt="{name_zh}" onload="this.classList.add('loaded');if(this.parentElement)this.parentElement.classList.add('loaded');" onerror="if(this.parentElement)this.parentElement.classList.add('error');">
            </div>
            <div class="info">
                <div class="info-content">
                    <div class="info-texts">
                        <h3 class="name-zh name-primary" id="title-{idx}">{name_zh}</h3>
                        <p class="name-ja name-sub1" id="sub1-{idx}">{name_ja}</p>
                        <p class="name-en name-sub2" id="sub2-{idx}">{name_en}</p>
                        <p class="dim" id="dim-{idx}">{dim_text}</p>
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
            <button class="filter-btn active" id="filterBtnAll" onclick="setFilter('all', this)" title="全部項目"><span class="filter-icon">✨</span> <span class="filter-label">全部</span> <span class="filter-count">({len(sorted_items)})</span></button>
            <button class="filter-btn" id="filterBtnL" onclick="setFilter('L', this)" title="大型 L (3×3)"><span class="filter-label">L</span> <span class="filter-count">({count_L})</span></button>
            <button class="filter-btn" id="filterBtnM" onclick="setFilter('M', this)" title="中型 M (2×2)"><span class="filter-label">M</span> <span class="filter-count">({count_M})</span></button>
            <button class="filter-btn" id="filterBtnS" onclick="setFilter('S', this)" title="小型 S (1×1)"><span class="filter-label">S</span> <span class="filter-count">({count_S})</span></button>
            <div class="filter-btn-break"></div>
            <button class="filter-btn fav-filter-btn" id="favFilterBtn" onclick="setFilter('favorite', this)" title="我的最愛"><span class="filter-icon">❤️</span> <span class="filter-label">最愛</span> <span class="filter-count">(<span id="favCount">0</span>)</span></button>
            <button class="filter-btn clear-fav-btn" id="clearFavBtn" onclick="clearFavorites()" title="清空所有已收藏的項目" style="display: none;"><span class="filter-icon">🗑️</span> <span class="filter-label">清空</span></button>
        """
    else:
        count_L = count_M = count_S = 0
        filter_buttons_html = f"""
            <button class="filter-btn active" id="filterBtnAll" onclick="setFilter('all', this)" title="全部項目"><span class="filter-icon">✨</span> <span class="filter-label">全部</span> <span class="filter-count">({len(sorted_items)})</span></button>
            <button class="filter-btn" id="filterBtnShot" onclick="setFilter('screenshot', this)" title="實景照片"><span class="filter-icon">📸</span> <span class="filter-label">實景</span> <span class="filter-count">({has_screenshot_count})</span></button>
            <button class="filter-btn" id="filterBtnIcon" onclick="setFilter('icon', this)" title="尚無大圖 (僅圖示)"><span class="filter-icon">🎨</span> <span class="filter-label">圖示</span> <span class="filter-count">({no_screenshot_count})</span></button>
            <div class="filter-btn-break"></div>
            <button class="filter-btn fav-filter-btn" id="favFilterBtn" onclick="setFilter('favorite', this)" title="我的最愛"><span class="filter-icon">❤️</span> <span class="filter-label">最愛</span> <span class="filter-count">(<span id="favCount">0</span>)</span></button>
            <button class="filter-btn clear-fav-btn" id="clearFavBtn" onclick="clearFavorites()" title="清空所有已收藏的項目" style="display: none;"><span class="filter-icon">🗑️</span> <span class="filter-label">清空</span></button>
        """

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
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
        html, body {{
            overflow-x: hidden;
            width: 100%;
            max-width: 100vw;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
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
            gap: 16px;
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
            flex-shrink: 0;
            order: 1;
        }}
        .nav-links {{
            display: flex;
            gap: 8px;
            align-items: center;
            margin-left: auto;
            order: 2;
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

        /* Language Switcher */
        .lang-selector-wrap {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #eef3ef;
            padding: 3px 8px 3px 12px;
            border-radius: 20px;
            border: 1px solid rgba(43, 92, 95, 0.22);
            transition: all 0.2s ease;
            flex-shrink: 0;
            margin-left: 6px;
            order: 3;
        }}
        .lang-selector-wrap:hover {{
            background: #e5ede7;
            border-color: var(--primary);
        }}
        .lang-globe {{
            font-size: 0.95rem;
            line-height: 1;
            user-select: none;
        }}
        .lang-select {{
            background: transparent;
            border: none;
            outline: none;
            color: var(--primary);
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 4px 4px 0;
            font-family: inherit;
        }}
        .lang-select option {{
            background: #ffffff;
            color: #333333;
        }}

        /* Main Container */
        .main-wrapper {{
            flex: 1;
            padding: 24px;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
            box-sizing: border-box;
            overflow-x: hidden;
        }}

        header {{
            margin-bottom: 24px;
            text-align: center;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
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
            margin-bottom: 14px;
            align-items: center;
            width: 100%;
            max-width: 100%;
            min-width: 0;
            box-sizing: border-box;
        }}
        .showing-stats {{
            text-align: center;
            font-size: 0.92rem;
            color: var(--text-sub);
            margin-bottom: 20px;
            font-weight: 500;
        }}
        .showing-stats strong {{
            color: var(--primary);
            font-weight: 700;
        }}
        .search-box {{
            padding: 10px 18px;
            font-size: 1rem;
            border: 2px solid #ddd;
            border-radius: 24px;
            width: 320px;
            max-width: 100%;
            box-sizing: border-box;
            outline: none;
            transition: all 0.3s;
            background: #fff;
        }}
        .search-box:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 8px rgba(43, 92, 95, 0.2);
        }}
        .filter-buttons-scroll {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            max-width: 100%;
            min-width: 0;
            box-sizing: border-box;
        }}
        .filter-btn-break {{
            display: none;
        }}
        .filter-btn {{
            height: 38px;
            padding: 0 16px;
            font-size: 0.92rem;
            border: 2px solid #ddd;
            border-radius: 20px;
            background: #fff;
            color: var(--text-sub);
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            box-sizing: border-box;
            line-height: 1;
        }}
        .filter-btn .filter-icon {{
            font-size: 0.95rem;
            line-height: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .filter-btn:hover {{
            background: #eef3ef;
            border-color: #cbdad0;
        }}
        .filter-btn.active {{
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }}
        .filter-btn.fav-filter-btn {{
            color: var(--accent-red);
            border-color: #ffd2d6;
            background: #fff9f9;
        }}
        .filter-btn.fav-filter-btn:hover {{
            background: #ffebee;
            border-color: var(--accent-red);
        }}
        .filter-btn.fav-filter-btn.active {{
            background: var(--accent-red);
            color: #fff;
            border-color: var(--accent-red);
        }}
        .filter-btn.clear-fav-btn {{
            border-color: #e2e8f0;
            color: #718096;
            background: #f8fafc;
        }}
        .filter-btn.clear-fav-btn:hover {{
            background: #fee2e2;
            color: #ef4444;
            border-color: #fca5a5;
        }}

        /* Responsive Grid */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(0,0,0,0.06);
            cursor: pointer;
            position: relative;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }}
        .card-fav-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
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
            background-color: #eef2ed;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        /* Skeleton Shimmer Loading State */
        .img-container::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(90deg, #eef2ed 0%, #f7faf6 50%, #eef2ed 100%);
            background-size: 200% 100%;
            animation: imgShimmer 1.6s infinite linear;
            z-index: 1;
            opacity: 1;
            transition: opacity 0.3s ease;
        }}
        .img-container.loaded::before {{
            opacity: 0;
            pointer-events: none;
        }}
        @keyframes imgShimmer {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        .img-placeholder {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .img-placeholder svg {{
            width: 36px;
            height: 36px;
            fill: #b5c7b7;
            opacity: 0.65;
            animation: imgPulse 1.4s ease-in-out infinite alternate;
        }}
        .img-container.loaded .img-placeholder {{
            opacity: 0;
        }}
        @keyframes imgPulse {{
            0% {{ transform: scale(0.92); opacity: 0.45; }}
            100% {{ transform: scale(1.06); opacity: 0.8; }}
        }}
        .img-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            position: relative;
            z-index: 3;
            opacity: 0;
            transition: opacity 0.35s ease, transform 0.3s ease;
        }}
        .img-container img.loaded {{
            opacity: 1;
        }}
        .card:hover .img-container img.loaded {{
            transform: scale(1.05);
        }}
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
        .name-zh, .name-primary {{
            font-size: 1.15rem;
            font-weight: bold;
            color: var(--text-main);
            margin-bottom: 4px;
            line-height: 1.25;
        }}
        .name-en, .name-sub1 {{
            font-size: 0.92rem;
            color: var(--text-sub);
            margin-bottom: 2px;
            line-height: 1.25;
        }}
        .name-ja, .name-sub2 {{
            font-size: 0.85rem;
            color: #888888;
            margin-bottom: 6px;
            line-height: 1.25;
        }}
        .dim {{
            font-size: 0.82rem;
            color: #888;
            margin-top: auto;
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

        
        @media (max-width: 360px) {{
            .filter-btn .filter-label {{
                display: none;
            }}
            .filter-btn {{
                padding: 5px 8px;
                font-size: 0.78rem;
            }}
        }}

        /* Enhanced Lightbox Modal */
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            width: 100%; height: 100%;
            background: rgba(10, 12, 16, 0.94);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            user-select: none;
            padding: 10px;
            box-sizing: border-box;
            overflow: hidden;
        }}
        .modal.active {{ display: flex; }}

        .modal-close {{
            position: absolute;
            top: 14px;
            right: 22px;
            color: #fff;
            font-size: 2.2rem;
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
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.16);
            border: 2px solid rgba(255, 255, 255, 0.45);
            color: #ffffff;
            font-size: 1.8rem;
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
            max-width: 92vw;
            max-height: 98vh;
            z-index: 1000;
            padding: 4px 60px;
            box-sizing: border-box;
        }}
        .lightbox-img-wrapper {{
            display: flex;
            align-items: center;
            justify-content: center;
            max-width: 90vw;
            max-height: calc(100vh - 170px);
        }}
        .lightbox-img-wrapper img {{
            max-width: 100%;
            max-height: calc(100vh - 170px);
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }}
        .lightbox-info {{
            margin-top: 8px;
            text-align: center;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
        }}
        .modal-caption {{
            font-size: 1.08rem;
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
            padding: 5px 14px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
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
            position: relative;
            margin-top: 8px;
            margin-bottom: 2px;
            z-index: 1002;
            background: rgba(20, 24, 30, 0.75);
            padding: 4px 10px;
            border-radius: 26px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            max-width: 90vw;
            overflow-x: auto;
            flex-shrink: 0;
        }}
        .thumb-strip {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .thumb-item {{
            width: 42px;
            height: 42px;
            border-radius: 6px;
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
            transform: scale(1.14);
            box-shadow: 0 0 12px rgba(42, 157, 143, 0.9);
            z-index: 2;
        }}
        .thumb-strip-arrow {{
            color: #888;
            font-size: 0.8rem;
            padding: 0 3px;
            user-select: none;
        }}

                @media (max-width: 640px) {{
            .main-wrapper {{
                padding: 12px 10px;
                width: 100%;
                box-sizing: border-box;
                overflow-x: hidden;
            }}
            header {{
                margin-bottom: 14px;
                width: 100%;
                box-sizing: border-box;
            }}
            h1 {{
                font-size: 1.35rem;
                margin-bottom: 12px;
            }}
            .controls {{
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
                margin-bottom: 8px;
                width: 100%;
                max-width: 100%;
                min-width: 0;
                box-sizing: border-box;
            }}
            .search-box {{
                width: 100%;
                max-width: 100%;
                box-sizing: border-box;
                padding: 9px 16px;
                font-size: 0.92rem;
            }}
            .filter-buttons-scroll {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                align-items: center;
                gap: 6px 8px;
                overflow-x: visible;
                padding: 2px 0 6px 0;
                width: 100%;
                max-width: 100%;
                min-width: 0;
                box-sizing: border-box;
            }}
            .filter-btn-break {{
                display: block;
                flex-basis: 100%;
                width: 100%;
                height: 0;
                margin: 0;
                padding: 0;
            }}
            .filter-btn {{
                height: 34px;
                padding: 0 11px;
                font-size: 0.82rem;
                white-space: nowrap;
                flex-shrink: 0;
                gap: 4px;
                border-radius: 17px;
                box-sizing: border-box;
                line-height: 1;
            }}
            .filter-btn .filter-icon {{
                font-size: 0.88rem;
                line-height: 1;
                display: inline-flex;
                align-items: center;
                justify-content: center;
            }}
            .showing-stats {{
                font-size: 0.82rem;
                margin-bottom: 14px;
            }}
            .grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 10px;
                width: 100%;
                max-width: 100%;
                box-sizing: border-box;
            }}
            .card {{
                border-radius: 10px;
                min-width: 0;
                box-sizing: border-box;
            }}
            .img-container {{
                height: 125px;
            }}
            .info {{
                padding: 8px 10px;
            }}
            .info-texts {{
                min-width: 0;
                overflow: hidden;
            }}
            .name-zh, .name-primary {{
                font-size: 0.92rem;
                margin-bottom: 2px;
                line-height: 1.2;
                word-break: break-word;
                overflow-wrap: break-word;
            }}
            .name-en, .name-sub1 {{
                font-size: 0.78rem;
                margin-bottom: 1px;
                line-height: 1.2;
                word-break: break-word;
                overflow-wrap: break-word;
            }}
            .name-ja, .name-sub2 {{
                font-size: 0.72rem;
                margin-bottom: 4px;
                line-height: 1.2;
                word-break: break-word;
                overflow-wrap: break-word;
            }}
            .dim {{
                font-size: 0.72rem;
            }}
            .card-fav-btn {{
                top: 6px;
                right: 6px;
                width: 30px;
                height: 30px;
            }}
            .card-fav-btn svg {{
                width: 15px;
                height: 15px;
            }}
            .rug-grid-box {{
                padding: 2px;
            }}
            .rug-grid-box svg {{
                width: 36px !important;
                height: 36px !important;
            }}
            .nav-container {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px 6px;
                gap: 6px 0;
                width: 100%;
                box-sizing: border-box;
            }}
            .nav-brand {{
                order: 1;
                font-size: 1.12rem;
                flex: 1;
            }}
            .lang-selector-wrap {{
                order: 2;
                margin-left: auto;
                padding: 2px 6px 2px 8px;
                flex-shrink: 0;
            }}
            .lang-select {{
                font-size: 0.8rem;
                padding: 2px;
            }}
            .nav-links {{
                order: 3;
                width: 100%;
                max-width: 100%;
                min-width: 0;
                margin-left: 0;
                display: flex;
                flex-wrap: nowrap;
                justify-content: flex-start;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                padding: 4px 0 2px;
                scrollbar-width: none;
                box-sizing: border-box;
            }}
            .nav-links::-webkit-scrollbar {{
                display: none;
            }}
            .nav-link {{
                padding: 5px 11px;
                font-size: 0.82rem;
                white-space: nowrap;
                flex-shrink: 0;
            }}
            /* Lightbox portrait mobile: keep thumbnails and information, fits comfortably */
            .lightbox-main {{
                padding: 4px 6px;
                width: 100%;
                max-width: 100%;
                max-height: 100vh;
                box-sizing: border-box;
            }}
            .lightbox-img-wrapper {{
                width: 100%;
                max-width: 100%;
                max-height: calc(100vh - 190px - env(safe-area-inset-bottom, 0px));
            }}
            .lightbox-img-wrapper img {{
                max-width: 100%;
                max-height: calc(100vh - 190px - env(safe-area-inset-bottom, 0px));
                width: auto;
                height: auto;
                object-fit: contain;
            }}
            .nav-zone {{
                width: 44px;
            }}
            .nav-btn {{
                width: 36px;
                height: 36px;
                font-size: 1.2rem;
                background: rgba(20, 20, 20, 0.45);
            }}
            .thumb-strip-wrapper {{
                margin-top: 6px;
                margin-bottom: calc(4px + env(safe-area-inset-bottom, 0px));
                max-width: 96%;
                padding: 3px 8px;
                box-sizing: border-box;
            }}
            .thumb-item {{
                width: 36px;
                height: 36px;
            }}
            .lightbox-info {{
                margin-top: 6px;
                gap: 4px;
            }}
            .modal-caption {{
                font-size: 0.95rem;
            }}
            .caption-sub {{
                display: inline;
            }}
            .lightbox-detail-info {{
                display: block;
            }}
            .lightbox-fav-btn {{
                padding: 5px 12px;
                font-size: 0.84rem;
            }}
            .modal-close {{
                top: 8px;
                right: 12px;
                font-size: 1.8rem;
            }}
            .img-placeholder svg {{
                width: 28px;
                height: 28px;
            }}
        }}

        
        /* Landscape / Short Screen Mode: Remove thumbnails, compact bottom bar, MAXIMIZE image! */
        @media (max-height: 560px) {{
            .thumb-strip-wrapper {{
                display: none !important;
            }}
            .lightbox-detail-info {{
                display: none !important;
            }}
            .caption-sub {{
                display: none !important;
            }}
            .lightbox-main {{
                padding: 2px 4px;
                width: 100%;
                max-width: 100%;
                height: 100%;
                max-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: space-between;
                box-sizing: border-box;
            }}
            .lightbox-img-wrapper {{
                flex: 1;
                width: 100%;
                max-width: 100%;
                max-height: calc(100vh - 50px - env(safe-area-inset-bottom, 0px));
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 0;
            }}
            .lightbox-img-wrapper img {{
                max-width: 100%;
                max-height: calc(100vh - 50px - env(safe-area-inset-bottom, 0px));
                width: auto;
                height: auto;
                object-fit: contain;
                border-radius: 6px;
            }}
            .lightbox-info {{
                margin-top: auto;
                margin-bottom: calc(4px + env(safe-area-inset-bottom, 0px));
                background: rgba(20, 24, 30, 0.88);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                padding: 3px 12px;
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                width: auto;
                max-width: 90%;
                height: 38px;
                box-sizing: border-box;
                flex-shrink: 0;
                z-index: 1002;
            }}
            .modal-caption {{
                font-size: 0.86rem;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-align: left;
                flex: 1;
                min-width: 0;
                line-height: 1.2;
            }}
            .lightbox-actions {{
                flex-shrink: 0;
                gap: 8px;
            }}
            .lightbox-fav-btn {{
                padding: 3px 8px;
                font-size: 0.76rem;
                border-radius: 14px;
                gap: 4px;
            }}
            .lightbox-counter {{
                font-size: 0.76rem;
                white-space: nowrap;
                color: #bbb;
            }}
            .modal-close {{
                top: 6px;
                right: 10px;
                font-size: 1.6rem;
            }}
            .nav-zone {{
                width: 44px;
            }}
            .nav-btn {{
                width: 34px;
                height: 34px;
                font-size: 1.1rem;
                background: rgba(20, 20, 20, 0.45);
            }}
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
    <script>
        function getInitialLanguage() {{
            try {{
                var saved = localStorage.getItem('acnh_lang');
                if (saved && (saved === 'zh-TW' || saved === 'en-US' || saved === 'ja-JP')) {{
                    return saved;
                }}
            }} catch(e) {{}}
            
            var langs = navigator.languages || [navigator.language || navigator.userLanguage || ''];
            for (var i = 0; i < langs.length; i++) {{
                var l = (langs[i] || '').toLowerCase();
                if (l.indexOf('zh') === 0) return 'zh-TW';
                if (l.indexOf('ja') === 0) return 'ja-JP';
            }}
            return 'en-US';
        }}
        var currentLang = getInitialLanguage();
        document.documentElement.lang = currentLang;

        // Register Service Worker for persistent Cache Storage & offline support
        if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {{
            window.addEventListener('load', function() {{
                navigator.serviceWorker.register('sw.js', {{ scope: './' }}).catch(function(err) {{
                    console.warn('SW registration skipped:', err);
                }});
            }});
        }}
    </script>
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="site-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-brand" id="navBrand">動森室內圖庫</a>
            <div class="nav-links">
                <a href="index.html" class="nav-link" id="navHome">首頁導覽</a>
                <a href="wallpapers.html" class="nav-link {nav_wall_active}" id="navWallpapers">壁紙 ({stats_counts.get('wallpapers', 312)})</a>
                <a href="floors.html" class="nav-link {nav_floor_active}" id="navFloors">地板 ({stats_counts.get('floors', 215)})</a>
                <a href="rugs.html" class="nav-link {nav_rug_active}" id="navRugs">地毯 ({stats_counts.get('rugs', 210)})</a>
            </div>
            <div class="lang-selector-wrap">
                <span class="lang-globe">🌐</span>
                <select id="langSelect" class="lang-select" onchange="changeLanguage(this.value)" aria-label="Language Selector">
                    <option value="zh-TW">繁體中文</option>
                    <option value="ja-JP">日本語</option>
                    <option value="en-US">English</option>
                </select>
            </div>
        </div>
    </nav>

    <div class="main-wrapper">
        <header>
            <h1 id="headerTitle">集合啦！動物森友會 - {page_title}</h1>
            <div class="controls">
                <input type="text" id="search" class="search-box" placeholder="搜尋名稱 (中/日/英)..." oninput="filterCards()">
                <div class="filter-buttons-scroll">
                    {filter_buttons_html}
                </div>
            </div>
            <div id="showingStats" class="showing-stats"></div>
        </header>

        <div class="empty-state" id="emptyState" style="display: none;">
            <h3 id="emptyTitle">找不到符合條件的項目</h3>
            <p id="emptyDesc">請嘗試調整搜尋關鍵字或切換分類篩選。</p>
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
        
        <!-- Center Image, Info & Thumbnails -->
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
            <!-- Bottom Thumbnail Strip / Pager -->
            <div class="thumb-strip-wrapper" onclick="event.stopPropagation()">
                <div class="thumb-strip" id="thumbStrip"></div>
            </div>
        </div>
    </div>

    <!-- Custom Style Confirm Dialog -->
    <div class="confirm-overlay" id="confirmModal" onclick="closeConfirmModal(event)">
        <div class="confirm-box" onclick="event.stopPropagation()">
            <div class="confirm-icon">🗑️</div>
            <div class="confirm-title">清空我的最愛</div>
            <div class="confirm-desc" id="confirmDesc">
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
        <p id="footerSrc">資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)</p>
        <p id="footerNote" style="margin-top: 6px; font-size: 0.82rem; color: #88998a;">非官方社群圖庫工具，僅供個人鑑賞與交流用途。</p>
    </footer>

    <script>
        const galleryData = {gallery_data_json};
        const STORAGE_KEY = '{storage_key}';
        const STATS = {{
            total: {len(sorted_items)},
            has_shot: {has_screenshot_count if page_type != 'rugs' else 0},
            no_shot: {no_screenshot_count if page_type != 'rugs' else 0},
            count_L: {count_L if page_type == 'rugs' else 0},
            count_M: {count_M if page_type == 'rugs' else 0},
            count_S: {count_S if page_type == 'rugs' else 0},
            wall_total: {stats_counts.get('wallpapers', 312)},
            floor_total: {stats_counts.get('floors', 215)},
            rug_total: {stats_counts.get('rugs', 210)},
            page_type: '{page_type}'
        }};

        const I18N_DATA = {{
            'zh-TW': {{
                brand: '動森室內圖庫',
                nav_home: '首頁導覽',
                nav_wallpapers: '壁紙',
                nav_floors: '地板',
                nav_rugs: '地毯',
                preloader_title: '集合啦！動物森友會',
                preloader_sub_wallpapers: '壁紙圖庫・正在讀取全輯高清圖片',
                preloader_sub_floors: '地板圖庫・正在讀取全輯高清圖片',
                preloader_sub_rugs: '地毯圖庫・正在讀取全輯高清圖片',
                preloader_loading: '準備讀取中...',
                preloader_counter: '已讀取 {{loaded}} / {{total}} 張',
                preloader_done: '已讀取 {{total}} / {{total}} 張（完成！）',
                preloader_skip: '跳過等待直接瀏覽 ➔',
                page_title_wallpapers: '壁紙全輯圖庫',
                page_title_floors: '地板全輯圖庫',
                page_title_rugs: '地毯全輯圖庫',
                filter_all_label: '全部',
                filter_shot_label: '實景',
                filter_icon_label: '圖示',
                filter_rug_L_label: 'L',
                filter_rug_M_label: 'M',
                filter_rug_S_label: 'S',
                filter_fav_label: '最愛',
                clear_fav_label: '清空',
                search_placeholder: '搜尋名稱 (中/日/英)...',
                showing_stats: '顯示中: <strong>{{match}}</strong> / {{total}} 款',
                empty_title: '找不到符合條件的項目',
                empty_desc: '請嘗試調整搜尋關鍵字或切換分類篩選。',
                fav_add: '加入我的最愛',
                fav_remove: '取消收藏',
                lightbox_fav_add: '收藏',
                lightbox_fav_active: '已收藏',
                lightbox_prev: '上一張 (← 方向鍵)',
                lightbox_next: '下一張 (→ 方向鍵)',
                lightbox_close: '關閉 (Esc)',
                res_label: '解析度: {{w}} &times; {{h}} px',
                rug_footprint: '佔地尺寸: <strong>{{grid}}</strong>（{{label}}）',
                rug_grid_hint: '房間 5×5 基準網格',
                confirm_title: '清空我的最愛',
                confirm_desc: '確定要清空已收藏的 <strong id="confirmFavCount">{{count}}</strong> 款項目嗎？<br>清空後將無法復原。',
                confirm_cancel: '取消',
                confirm_ok: '確認清空',
                footer_src: '資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)',
                footer_note: '非官方社群圖庫工具，僅供個人鑑賞與交流用途。'
            }},
            'en-US': {{
                brand: 'ACNH Interior Gallery',
                nav_home: 'Home',
                nav_wallpapers: 'Wallpapers',
                nav_floors: 'Flooring',
                nav_rugs: 'Rugs',
                preloader_title: 'Animal Crossing: New Horizons',
                preloader_sub_wallpapers: 'Wallpapers・Loading HD Images...',
                preloader_sub_floors: 'Flooring・Loading HD Images...',
                preloader_sub_rugs: 'Rugs・Loading HD Images...',
                preloader_loading: 'Preparing...',
                preloader_counter: 'Loaded {{loaded}} / {{total}} images',
                preloader_done: 'Loaded {{total}} / {{total}} images (Completed!)',
                preloader_skip: 'Skip & Browse Directly ➔',
                page_title_wallpapers: 'Wallpapers Gallery',
                page_title_floors: 'Flooring Gallery',
                page_title_rugs: 'Rugs Gallery',
                filter_all_label: 'All',
                filter_shot_label: 'Photos',
                filter_icon_label: 'Icons',
                filter_rug_L_label: 'L',
                filter_rug_M_label: 'M',
                filter_rug_S_label: 'S',
                filter_fav_label: 'Fav',
                clear_fav_label: 'Clear',
                search_placeholder: 'Search name (EN / ZH / JA)...',
                showing_stats: 'Showing: <strong>{{match}}</strong> / {{total}} items',
                empty_title: 'No matching items found',
                empty_desc: 'Try adjusting your search query or switching filters.',
                fav_add: 'Add to favorites',
                fav_remove: 'Remove from favorites',
                lightbox_fav_add: 'Favorite',
                lightbox_fav_active: 'Favorited',
                lightbox_prev: 'Previous (← Arrow)',
                lightbox_next: 'Next (→ Arrow)',
                lightbox_close: 'Close (Esc)',
                res_label: 'Resolution: {{w}} &times; {{h}} px',
                rug_footprint: 'Footprint: <strong>{{grid}}</strong> ({{label}})',
                rug_grid_hint: 'Room 5×5 Reference Grid',
                confirm_title: 'Clear Favorites',
                confirm_desc: 'Are you sure you want to clear <strong id="confirmFavCount">{{count}}</strong> favorited item(s)?<br>This action cannot be undone.',
                confirm_cancel: 'Cancel',
                confirm_ok: 'Clear All',
                footer_src: 'Data & images source: <a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> & Nintendo Animal Crossing: New Horizons',
                footer_note: 'Unofficial fan gallery tool, for personal appreciation and reference only.'
            }},
            'ja-JP': {{
                brand: 'あつ森インテリア図鑑',
                nav_home: 'ホーム',
                nav_wallpapers: 'かべがみ',
                nav_floors: 'ゆかいた',
                nav_rugs: 'ラグ',
                preloader_title: 'あつまれ どうぶつの森',
                preloader_sub_wallpapers: 'かべがみ図鑑・HD画像を読み込み中...',
                preloader_sub_floors: 'ゆかいた図鑑・HD画像を読み込み中...',
                preloader_sub_rugs: 'ラグ図鑑・HD画像を読み込み中...',
                preloader_loading: '読み込み準備中...',
                preloader_counter: '{{loaded}} / {{total}} 枚を読み込み済み',
                preloader_done: '全 {{total}} 枚を読み込み完了！',
                preloader_skip: 'スキップして閲覧 ➔',
                page_title_wallpapers: 'かべがみ図鑑 全集',
                page_title_floors: 'ゆかいた図鑑 全集',
                page_title_rugs: 'ラグ図鑑 全集',
                filter_all_label: 'すべて',
                filter_shot_label: '写真',
                filter_icon_label: 'アイコン',
                filter_rug_L_label: 'L',
                filter_rug_M_label: 'M',
                filter_rug_S_label: 'S',
                filter_fav_label: 'お気に入り',
                clear_fav_label: '消去',
                search_placeholder: '名前で検索 (日 / 英 / 中)...',
                showing_stats: '表示中: <strong>{{match}}</strong> / {{total}} 種',
                empty_title: '該当する項目が見つかりません',
                empty_desc: '検索キーワードやフィルターを変更してください。',
                fav_add: 'お気に入りに追加',
                fav_remove: 'お気に入りから削除',
                lightbox_fav_add: 'お気に入り',
                lightbox_fav_active: '登録済み',
                lightbox_prev: '前へ (← キー)',
                lightbox_next: '次へ (→ キー)',
                lightbox_close: '閉じる (Esc)',
                res_label: '解像度: {{w}} &times; {{h}} px',
                rug_footprint: 'サイズ: <strong>{{grid}}</strong>（{{label}}）',
                rug_grid_hint: '部屋 5×5 基準グリッド',
                confirm_title: 'お気に入りを全消去',
                confirm_desc: '登録済みの <strong id="confirmFavCount">{{count}}</strong> 件のお気に入りをすべて削除しますか？<br>この操作は元に戻せません。',
                confirm_cancel: 'キャンセル',
                confirm_ok: '削除する',
                footer_src: 'データ・画像出典：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> および 任天堂『あつまれ どうぶつの森』',
                footer_note: '非公式ファンサイトです。個人の鑑賞および交流を目的としています。'
            }}
        }};

        let favorites = new Set();
        let currentFilter = 'all';
        let filteredIndices = galleryData.map((_, i) => i);
        let currentPos = 0; // index in filteredIndices

        function getLocalizedRugSizeLabel(cat, lang) {{
            if (lang === 'en-US') {{
                if (cat === 'L') return 'Large (L)';
                if (cat === 'M') return 'Medium (M)';
                if (cat === 'S') return 'Small (S)';
                return cat || '';
            }}
            if (lang === 'ja-JP') {{
                if (cat === 'L') return 'Lサイズ';
                if (cat === 'M') return 'Mサイズ';
                if (cat === 'S') return 'Sサイズ';
                return cat || '';
            }}
            if (cat === 'L') return '大型 (L)';
            if (cat === 'M') return '中型 (M)';
            if (cat === 'S') return '小型 (S)';
            return cat || '';
        }}

        function changeLanguage(lang) {{
            if (!['zh-TW', 'en-US', 'ja-JP'].includes(lang)) return;
            currentLang = lang;
            try {{
                localStorage.setItem('acnh_lang', lang);
            }} catch(e) {{}}
            document.documentElement.lang = lang;

            var sel = document.getElementById('langSelect');
            if (sel && sel.value !== lang) sel.value = lang;

            applyLanguage(lang);
        }}

        function applyCardLanguage(lang) {{
            const d = I18N_DATA[lang] || I18N_DATA['zh-TW'];
            for (let i = 0; i < galleryData.length; i++) {{
                const it = galleryData[i];
                const titleEl = document.getElementById('title-' + i);
                const sub1El = document.getElementById('sub1-' + i);
                const sub2El = document.getElementById('sub2-' + i);
                const dimEl = document.getElementById('dim-' + i);
                const favBtn = document.getElementById('fav-btn-' + i);
                const isFav = favorites.has(it.name_en);

                if (lang === 'zh-TW') {{
                    if (titleEl) titleEl.textContent = it.name_zh;
                    if (sub1El) sub1El.textContent = it.name_ja;
                    if (sub2El) sub2El.textContent = it.name_en;
                }} else if (lang === 'en-US') {{
                    if (titleEl) titleEl.textContent = it.name_en;
                    if (sub1El) sub1El.textContent = it.name_zh;
                    if (sub2El) sub2El.textContent = it.name_ja;
                }} else if (lang === 'ja-JP') {{
                    if (titleEl) titleEl.textContent = it.name_ja;
                    if (sub1El) sub1El.textContent = it.name_en;
                    if (sub2El) sub2El.textContent = it.name_zh;
                }}

                if (favBtn) {{
                    favBtn.title = isFav ? d.fav_remove : d.fav_add;
                }}

                if (dimEl && it.grid_size) {{
                    const szLbl = getLocalizedRugSizeLabel(it.size_category, lang);
                    dimEl.innerHTML = d.rug_footprint.replace('{{grid}}', it.grid_size).replace('{{label}}', szLbl);
                }}
            }}
        }}

        function applyLanguage(lang) {{
            if (!I18N_DATA[lang]) lang = 'zh-TW';
            const d = I18N_DATA[lang];

            const pageKey = 'page_title_' + STATS.page_type;
            const catTitle = d[pageKey] || '';

            if (lang === 'en-US') {{
                document.title = catTitle + ' (' + STATS.total + ' items) - Animal Crossing: New Horizons';
                const h1 = document.getElementById('headerTitle');
                if (h1) h1.textContent = 'Animal Crossing: New Horizons - ' + catTitle + ' (' + STATS.total + ')';
            }} else if (lang === 'ja-JP') {{
                document.title = catTitle + '（' + STATS.total + '種）- あつまれ どうぶつの森';
                const h1 = document.getElementById('headerTitle');
                if (h1) h1.textContent = 'あつまれ どうぶつの森 - ' + catTitle + '（' + STATS.total + '種）';
            }} else {{
                document.title = '集合啦！動物森友會 - ' + catTitle + ' (' + STATS.total + '款)';
                const h1 = document.getElementById('headerTitle');
                if (h1) h1.textContent = '集合啦！動物森友會 - ' + catTitle + ' (' + STATS.total + '款)';
            }}

            const navBrand = document.getElementById('navBrand');
            if (navBrand) navBrand.textContent = d.brand;
            const navHome = document.getElementById('navHome');
            if (navHome) navHome.textContent = d.nav_home;
            const navWall = document.getElementById('navWallpapers');
            if (navWall) navWall.textContent = d.nav_wallpapers + ' (' + STATS.wall_total + ')';
            const navFloor = document.getElementById('navFloors');
            if (navFloor) navFloor.textContent = d.nav_floors + ' (' + STATS.floor_total + ')';
            const navRug = document.getElementById('navRugs');
            if (navRug) navRug.textContent = d.nav_rugs + ' (' + STATS.rug_total + ')';

            const searchInput = document.getElementById('search');
            if (searchInput) searchInput.placeholder = d.search_placeholder;

            const btnAll = document.getElementById('filterBtnAll');
            if (btnAll) btnAll.innerHTML = `<span class="filter-icon">✨</span> <span class="filter-label">${{d.filter_all_label}}</span> <span class="filter-count">(${{STATS.total}})</span>`;

            if (STATS.page_type === 'rugs') {{
                const btnL = document.getElementById('filterBtnL');
                if (btnL) btnL.innerHTML = `<span class="filter-label">${{d.filter_rug_L_label}}</span> <span class="filter-count">(${{STATS.count_L}})</span>`;
                const btnM = document.getElementById('filterBtnM');
                if (btnM) btnM.innerHTML = `<span class="filter-label">${{d.filter_rug_M_label}}</span> <span class="filter-count">(${{STATS.count_M}})</span>`;
                const btnS = document.getElementById('filterBtnS');
                if (btnS) btnS.innerHTML = `<span class="filter-label">${{d.filter_rug_S_label}}</span> <span class="filter-count">(${{STATS.count_S}})</span>`;
            }} else {{
                const btnShot = document.getElementById('filterBtnShot');
                if (btnShot) btnShot.innerHTML = `<span class="filter-icon">📸</span> <span class="filter-label">${{d.filter_shot_label}}</span> <span class="filter-count">(${{STATS.has_shot}})</span>`;
                const btnIcon = document.getElementById('filterBtnIcon');
                if (btnIcon) btnIcon.innerHTML = `<span class="filter-icon">🎨</span> <span class="filter-label">${{d.filter_icon_label}}</span> <span class="filter-count">(${{STATS.no_shot}})</span>`;
            }}

            const favFilterBtn = document.getElementById('favFilterBtn');
            if (favFilterBtn) favFilterBtn.innerHTML = `<span class="filter-icon">❤️</span> <span class="filter-label">${{d.filter_fav_label}}</span> <span class="filter-count">(<span id="favCount">${{favorites.size}}</span>)</span>`;

            const clearFavBtn = document.getElementById('clearFavBtn');
            if (clearFavBtn) clearFavBtn.innerHTML = `<span class="filter-icon">🗑️</span> <span class="filter-label">${{d.clear_fav_label}}</span>`;

            const emptyTitle = document.getElementById('emptyTitle');
            if (emptyTitle) emptyTitle.textContent = d.empty_title;
            const emptyDesc = document.getElementById('emptyDesc');
            if (emptyDesc) emptyDesc.textContent = d.empty_desc;


            const prevBtn = document.getElementById('prevBtn');
            if (prevBtn) prevBtn.title = d.lightbox_prev;
            const nextBtn = document.getElementById('nextBtn');
            if (nextBtn) nextBtn.title = d.lightbox_next;
            const closeBtn = document.querySelector('.modal-close');
            if (closeBtn) closeBtn.title = d.lightbox_close;

            const confirmTitle = document.querySelector('.confirm-title');
            if (confirmTitle) confirmTitle.textContent = d.confirm_title;
            const confirmDesc = document.getElementById('confirmDesc');
            if (confirmDesc) confirmDesc.innerHTML = d.confirm_desc.replace('{{count}}', favorites.size);
            const confirmCancel = document.querySelector('.confirm-btn-cancel');
            if (confirmCancel) confirmCancel.textContent = d.confirm_cancel;
            const confirmDanger = document.querySelector('.confirm-btn-danger');
            if (confirmDanger) confirmDanger.textContent = d.confirm_ok;

            const footerSrc = document.getElementById('footerSrc');
            if (footerSrc) footerSrc.innerHTML = d.footer_src;
            const footerNote = document.getElementById('footerNote');
            if (footerNote) footerNote.textContent = d.footer_note;

            applyCardLanguage(lang);
            filterCards();

            const modal = document.getElementById('lightboxModal');
            if (modal && modal.classList.contains('active')) {{
                updateLightbox();
            }}
        }}

        // Instant revelation for already-cached or quickly loaded images
        function markCompleteImages() {{
            document.querySelectorAll('.img-container img').forEach(function(img) {{
                if (img.complete && img.naturalWidth > 0) {{
                    img.classList.add('loaded');
                    if (img.parentElement) img.parentElement.classList.add('loaded');
                }}
            }});
        }}
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', markCompleteImages);
        }} else {{
            markCompleteImages();
        }}

        // Gentle background prefetcher (runs during browser idle time, max 3 concurrent)
        (function initIdlePrefetcher() {{
            var index = 0;
            var concurrency = 3;
            var active = 0;

            function processQueue() {{
                while (active < concurrency && index < galleryData.length) {{
                    var item = galleryData[index++];
                    if (!item || !item.local_rel_path) continue;
                    active++;
                    var img = new Image();
                    img.onload = img.onerror = function() {{
                        active--;
                        if ('requestIdleCallback' in window) {{
                            window.requestIdleCallback(processQueue, {{ timeout: 2000 }});
                        }} else {{
                            setTimeout(processQueue, 150);
                        }}
                    }};
                    img.src = item.local_rel_path;
                }}
            }}

            setTimeout(function() {{
                if ('requestIdleCallback' in window) {{
                    window.requestIdleCallback(processQueue, {{ timeout: 3000 }});
                }} else {{
                    setTimeout(processQueue, 300);
                }}
            }}, 2500);
        }})();

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
            const d = I18N_DATA[currentLang] || I18N_DATA['zh-TW'];
            const desc = document.getElementById('confirmDesc');
            if (desc) desc.innerHTML = d.confirm_desc.replace('{{count}}', favorites.size);

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

            const d = I18N_DATA[currentLang] || I18N_DATA['zh-TW'];

            galleryData.forEach((item, idx) => {{
                const btn = document.getElementById(`fav-btn-${{idx}}`);
                if (btn) {{
                    const isFav = favorites.has(item.name_en);
                    btn.classList.toggle('active', isFav);
                    btn.title = isFav ? d.fav_remove : d.fav_add;
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
            const d = I18N_DATA[currentLang] || I18N_DATA['zh-TW'];

            btn.classList.toggle('active', isFav);
            if (icon) {{
                icon.innerHTML = isFav 
                    ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
                    : '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
            }}
            if (text) {{
                text.textContent = isFav ? d.lightbox_fav_active : d.lightbox_fav_add;
            }}
            btn.title = isFav ? d.fav_remove : d.fav_add;
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

            const showingStats = document.getElementById('showingStats');
            if (showingStats) {{
                const d = I18N_DATA[currentLang] || I18N_DATA['zh-TW'];
                showingStats.innerHTML = d.showing_stats.replace('{{match}}', filteredIndices.length).replace('{{total}}', galleryData.length);
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
            document.body.style.overflow = 'hidden';
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
            const d = I18N_DATA[currentLang] || I18N_DATA['zh-TW'];

            const img = document.getElementById('lightboxImg');
            img.src = item.local_rel_path;
            img.alt = (currentLang === 'en-US' ? item.name_en : (currentLang === 'ja-JP' ? item.name_ja : item.name_zh));

            let detailInfo = '';
            if (item.grid_size) {{
                const szLbl = getLocalizedRugSizeLabel(item.size_category, currentLang);
                detailInfo = `
                    <div class="lightbox-detail-info" style="display:flex; align-items:center; justify-content:center; gap:10px; margin-top:4px;">
                        ${{getRugGridSvg(item.grid_size, 38)}}
                        <div style="text-align:left; font-size:0.88rem; color:#fff;">
                            <div>${{d.rug_footprint.replace('{{grid}}', item.grid_size).replace('{{label}}', szLbl)}}</div>
                            <div style="font-size:0.75rem; color:#bbb; margin-top:1px;">${{d.rug_grid_hint}}</div>
                        </div>
                    </div>`;
            }} else {{
                detailInfo = `<div class="lightbox-detail-info" style="font-size: 0.82rem; color: #aaa; margin-top: 2px;">${{d.res_label.replace('{{w}}', item.width).replace('{{h}}', item.height)}}</div>`;
            }}

            let captionText = '';
            if (currentLang === 'en-US') {{
                captionText = `<span class="caption-primary"><strong>${{item.name_en}}</strong></span> <span class="caption-sub">/ ${{item.name_ja}} (${{item.name_zh}})</span>`;
            }} else if (currentLang === 'ja-JP') {{
                captionText = `<span class="caption-primary"><strong>${{item.name_ja}}</strong></span> <span class="caption-sub">/ ${{item.name_en}} (${{item.name_zh}})</span>`;
            }} else {{
                captionText = `<span class="caption-primary"><strong>${{item.name_zh}}</strong></span> <span class="caption-sub">/ ${{item.name_ja}} (${{item.name_en}})</span>`;
            }}

            document.getElementById('lightboxCaption').innerHTML = captionText + detailInfo;
            document.getElementById('lightboxCounter').textContent = `${{currentPos + 1}} / ${{filteredIndices.length}}`;

            updateLightboxFavBtn();
            renderThumbnailStrip();

            // Smart predictive HD image preloading (next 3, prev 2)
            const offsets = [1, -1, 2, -2, 3];
            offsets.forEach(offset => {{
                const targetPos = currentPos + offset;
                if (targetPos >= 0 && targetPos < filteredIndices.length) {{
                    const itm = galleryData[filteredIndices[targetPos]];
                    if (itm && itm.local_rel_path) {{
                        const preImg = new Image();
                        preImg.src = itm.local_rel_path;
                    }}
                }}
            }});
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
                
                const dispTitle = (currentLang === 'en-US' ? `${{it.name_en}} (${{it.name_ja}})` : (currentLang === 'ja-JP' ? `${{it.name_ja}} (${{it.name_en}})` : `${{it.name_zh}} (${{it.name_en}})`));
                div.title = dispTitle;
                div.onclick = (e) => {{
                    e.stopPropagation();
                    currentPos = pos;
                    updateLightbox();
                }};

                const thumbImg = document.createElement('img');
                thumbImg.src = it.local_rel_path;
                thumbImg.alt = dispTitle;
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

        function closeLightbox(event) {{
            if (event && event.target && event.target.id !== 'lightboxModal' && !event.target.classList.contains('modal-close')) {{
                return;
            }}
            document.getElementById('lightboxModal').classList.remove('active');
            document.body.style.overflow = '';
        }}

        // Mobile Touch Swipe Navigation & Pull-to-close
        (function setupTouchGestures() {{
            var modal = document.getElementById('lightboxModal');
            if (!modal) return;
            var startX = 0;
            var startY = 0;
            var endX = 0;
            var endY = 0;

            modal.addEventListener('touchstart', function(e) {{
                if (e.touches.length === 1) {{
                    startX = e.touches[0].clientX;
                    startY = e.touches[0].clientY;
                    endX = startX;
                    endY = startY;
                }}
            }}, {{ passive: true }});

            modal.addEventListener('touchmove', function(e) {{
                if (e.touches.length === 1) {{
                    endX = e.touches[0].clientX;
                    endY = e.touches[0].clientY;
                }}
            }}, {{ passive: true }});

            modal.addEventListener('touchend', function(e) {{
                var diffX = endX - startX;
                var diffY = endY - startY;
                var absX = Math.abs(diffX);
                var absY = Math.abs(diffY);

                if (absX > 40 && absX > absY * 1.4) {{
                    if (diffX < 0) {{
                        navigateLightbox(1);
                    }} else {{
                        navigateLightbox(-1);
                    }}
                }} else if (diffY > 80 && absY > absX * 1.5) {{
                    closeLightbox();
                }}
            }}, {{ passive: true }});
        }})();

        // Keyboard Shortcuts
        document.addEventListener('keydown', (e) => {{
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

        // Clean up any Service Worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.getRegistrations().then(function(regs) {{
                for (var r of regs) r.unregister();
            }});
        }}

        // Initialize language and favorites
        loadFavorites();
        var sel = document.getElementById('langSelect');
        if (sel) sel.value = currentLang;
        applyLanguage(currentLang);
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
    wall_count = stats_counts.get('wallpapers', 312)
    floor_count = stats_counts.get('floors', 215)
    rug_count = stats_counts.get('rugs', 210)

    index_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>集合啦！動物森友會 - 室內裝潢圖庫全輯 (壁紙 / 地板 / 地毯)</title>
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
        html, body {{
            overflow-x: hidden;
            width: 100%;
            max-width: 100vw;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", "Hiragino Sans", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
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
            gap: 16px;
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
            flex-shrink: 0;
            order: 1;
        }}
        .nav-links {{
            display: flex;
            gap: 8px;
            align-items: center;
            margin-left: auto;
            order: 2;
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

        /* Language Switcher */
        .lang-selector-wrap {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #eef3ef;
            padding: 3px 8px 3px 12px;
            border-radius: 20px;
            border: 1px solid rgba(43, 92, 95, 0.22);
            transition: all 0.2s ease;
            flex-shrink: 0;
            margin-left: 6px;
            order: 3;
        }}
        .lang-selector-wrap:hover {{
            background: #e5ede7;
            border-color: var(--primary);
        }}
        .lang-globe {{
            font-size: 0.95rem;
            line-height: 1;
            user-select: none;
        }}
        .lang-select {{
            background: transparent;
            border: none;
            outline: none;
            color: var(--primary);
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            padding: 4px 4px 4px 0;
            font-family: inherit;
        }}
        .lang-select option {{
            background: #ffffff;
            color: #333333;
        }}

        /* Hero Banner */
        .hero {{
            text-align: center;
            padding: 50px 24px 30px;
            max-width: 900px;
            margin: 0 auto;
        }}
        .hero-badge {{
            display: inline-block;
            background: #e1ede8;
            color: var(--primary);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }}
        .hero h1 {{
            font-size: 2.5rem;
            color: var(--primary);
            line-height: 1.3;
            margin-bottom: 16px;
            letter-spacing: 0.5px;
        }}
        .hero p {{
            font-size: 1.05rem;
            color: var(--text-sub);
            line-height: 1.7;
        }}

        /* Portals Grid */
        .portal-grid {{
            max-width: 1200px;
            margin: 20px auto 50px;
            padding: 0 24px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 28px;
        }}
        .portal-card {{
            background: #ffffff;
            border-radius: 24px;
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
            margin-bottom: 32px;
            font-weight: bold;
        }}
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 28px;
        }}
        .feature-item {{
            text-align: center;
            padding: 16px;
        }}
        .feature-icon {{
            font-size: 2.2rem;
            margin-bottom: 12px;
        }}
        .feature-name {{
            font-size: 1.15rem;
            font-weight: bold;
            color: var(--primary);
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
            padding: 28px;
            text-align: center;
            font-size: 0.9rem;
            color: var(--text-sub);
            line-height: 1.6;
            margin-top: auto;
        }}
        .site-footer a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }}
        .site-footer a:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 640px) {{
            .nav-container {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
                padding: 10px 14px 6px;
                gap: 6px 0;
                width: 100%;
                box-sizing: border-box;
            }}
            .nav-brand {{
                order: 1;
                font-size: 1.12rem;
                flex: 1;
            }}
            .lang-selector-wrap {{
                order: 2;
                margin-left: auto;
                padding: 2px 6px 2px 8px;
                flex-shrink: 0;
            }}
            .lang-select {{
                font-size: 0.8rem;
                padding: 2px;
            }}
            .nav-links {{
                order: 3;
                width: 100%;
                max-width: 100%;
                min-width: 0;
                margin-left: 0;
                display: flex;
                flex-wrap: nowrap;
                justify-content: flex-start;
                align-items: center;
                gap: 6px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                padding: 4px 0 2px;
                scrollbar-width: none;
                box-sizing: border-box;
            }}
            .nav-links::-webkit-scrollbar {{
                display: none;
            }}
            .nav-link {{
                padding: 5px 11px;
                font-size: 0.82rem;
                white-space: nowrap;
                flex-shrink: 0;
            }}
            .hero {{
                padding: 30px 16px 20px;
            }}
            .hero-badge {{
                font-size: 0.82rem;
                padding: 4px 12px;
                margin-bottom: 12px;
            }}
            .hero h1 {{
                font-size: 1.75rem;
                margin-bottom: 12px;
            }}
            .hero p {{
                font-size: 0.92rem;
                line-height: 1.6;
            }}
            .portal-grid {{
                padding: 0 14px;
                grid-template-columns: 1fr;
                gap: 18px;
                margin-bottom: 36px;
            }}
            .card-body {{
                padding: 20px 18px;
            }}
            .card-title {{
                font-size: 1.35rem;
            }}
            .card-desc {{
                font-size: 0.88rem;
                margin-bottom: 18px;
            }}
            .card-specs {{
                gap: 8px;
                margin-bottom: 18px;
            }}
            .spec-tag {{
                font-size: 0.76rem;
                padding: 3px 8px;
            }}
            .enter-btn {{
                padding: 10px 16px;
                font-size: 0.92rem;
            }}
            .features {{
                margin: 0 14px 40px;
                padding: 24px 16px;
                border-radius: 20px;
            }}
            .features-title {{
                font-size: 1.35rem;
                margin-bottom: 22px;
            }}
            .features-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .feature-item {{
                padding: 8px 4px;
            }}
            .feature-icon {{
                font-size: 1.8rem;
                margin-bottom: 8px;
            }}
            .feature-name {{
                font-size: 1.05rem;
                margin-bottom: 6px;
            }}
            .feature-desc {{
                font-size: 0.86rem;
            }}
            .site-footer {{
                padding: 20px 14px;
                font-size: 0.82rem;
            }}
        }}
    </style>
    <script>
        function getInitialLanguage() {{
            try {{
                var saved = localStorage.getItem('acnh_lang');
                if (saved && (saved === 'zh-TW' || saved === 'en-US' || saved === 'ja-JP')) {{
                    return saved;
                }}
            }} catch(e) {{}}
            
            var langs = navigator.languages || [navigator.language || navigator.userLanguage || ''];
            for (var i = 0; i < langs.length; i++) {{
                var l = (langs[i] || '').toLowerCase();
                if (l.indexOf('zh') === 0) return 'zh-TW';
                if (l.indexOf('ja') === 0) return 'ja-JP';
            }}
            return 'en-US';
        }}
        var currentLang = getInitialLanguage();
        document.documentElement.lang = currentLang;

        // Register Service Worker for persistent Cache Storage & offline support
        if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {{
            window.addEventListener('load', function() {{
                navigator.serviceWorker.register('sw.js', {{ scope: './' }}).catch(function(err) {{
                    console.warn('SW registration skipped:', err);
                }});
            }});
        }}
    </script>
</head>
<body>
    <!-- Top Navigation Bar -->
    <nav class="site-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-brand" id="navBrand">動森室內圖庫</a>
            <div class="nav-links">
                <a href="index.html" class="nav-link active" id="navHome">首頁導覽</a>
                <a href="wallpapers.html" class="nav-link" id="navWallpapers">壁紙 ({wall_count})</a>
                <a href="floors.html" class="nav-link" id="navFloors">地板 ({floor_count})</a>
                <a href="rugs.html" class="nav-link" id="navRugs">地毯 ({rug_count})</a>
            </div>
            <div class="lang-selector-wrap">
                <span class="lang-globe">🌐</span>
                <select id="langSelect" class="lang-select" onchange="changeLanguage(this.value)" aria-label="Language Selector">
                    <option value="zh-TW">繁體中文</option>
                    <option value="ja-JP">日本語</option>
                    <option value="en-US">English</option>
                </select>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero">
        <div class="hero-badge" id="heroBadge">Animal Crossing: New Horizons</div>
        <h1 id="heroTitle">集合啦！動物森友會<br>室內裝潢圖庫全輯</h1>
        <p id="heroDesc">收錄全系列壁紙、地板與地毯的 1280x720 高清遊戲實景截圖與官方圖示。<br>支援實景大圖優先排序、即時搜尋、鍵盤方向鍵導航與離線個人最愛收藏。</p>
    </div>

    <!-- Portal Cards -->
    <div class="portal-grid">
        <!-- Wallpapers Card -->
        <a href="wallpapers.html" class="portal-card wallpapers">
            <div class="card-body">
                <div class="card-title">
                    <span id="wallCardTitle">壁紙圖庫</span>
                    <span class="card-count" id="wallCardCount">{wall_count} 款</span>
                </div>
                <div class="card-desc" id="wallCardDesc">
                    涵蓋常規商店、駱嵐不可思議壁紙、非賣品活動獎勵與三麗鷗聯名款。260 款室內 1280x720 實拍大圖與 52 款官方高畫質備選圖示。
                </div>
                <div class="card-specs" id="wallSpecs">
                    <span class="spec-tag">📸 260 款實景大圖</span>
                    <span class="spec-tag">✨ 實景優先 + 名稱排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn" id="wallCardBtn">
                    進入壁紙圖庫 ➔
                </div>
            </div>
        </a>

        <!-- Floors Card -->
        <a href="floors.html" class="portal-card floors">
            <div class="card-body">
                <div class="card-title">
                    <span id="floorCardTitle">地板圖庫</span>
                    <span class="card-count" id="floorCardCount">{floor_count} 款</span>
                </div>
                <div class="card-desc" id="floorCardDesc">
                    收錄實木拼花、復古磁磚、戶外自然場景、動態地磚與特殊材質地板。187 款室內鋪設 1280x720 實拍照與 28 款官方圖示。
                </div>
                <div class="card-specs" id="floorSpecs">
                    <span class="spec-tag">📸 187 款實景大圖</span>
                    <span class="spec-tag">✨ 實景優先 + 名稱排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn" id="floorCardBtn">
                    進入地板圖庫 ➔
                </div>
            </div>
        </a>

        <!-- Rugs Card -->
        <a href="rugs.html" class="portal-card rugs">
            <div class="card-body">
                <div class="card-title">
                    <span id="rugCardTitle">地毯圖庫</span>
                    <span class="card-count" id="rugCardCount">{rug_count} 款</span>
                </div>
                <div class="card-desc" id="rugCardDesc">
                    全系列大、中、小型與趣味特殊造型地毯，包括駱嵐限定地毯、蔬果造型地毯與季節限定圖騰。完整標註遊戲內 1×1 ~ 5×5 佔地尺寸與 S/M/L 篩選分類。
                </div>
                <div class="card-specs" id="rugSpecs">
                    <span class="spec-tag">📐 S / M / L 尺寸篩選</span>
                    <span class="spec-tag">✨ 尺寸大到小 + 字母排序</span>
                    <span class="spec-tag">♥ 我的最愛</span>
                </div>
                <div class="enter-btn" id="rugCardBtn">
                    進入地毯圖庫 ➔
                </div>
            </div>
        </a>
    </div>

    <!-- Highlights Section -->
    <div class="features">
        <h2 class="features-title" id="featuresTitle">✨ 核心功能特色</h2>
        <div class="features-grid">
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <div class="feature-name" id="feat1Title">三語即時搜尋</div>
                <div class="feature-desc" id="feat1Desc">支援繁體中文（台灣繁中）、英文以及日文原文即時過濾查找。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔤</div>
                <div class="feature-name" id="feat2Title">英文字母 A-Z 排序</div>
                <div class="feature-desc" id="feat2Desc">依照英文名稱字母順序整齊編排，方便精確定位與參照社群資料。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">♥</div>
                <div class="feature-name" id="feat3Title">離線個人收藏</div>
                <div class="feature-desc" id="feat3Desc">點擊愛心即可標記喜歡的壁紙與地板，資料保存在瀏覽器本地。</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🖼️</div>
                <div class="feature-name" id="feat4Title">沉浸式全螢幕檢視</div>
                <div class="feature-desc" id="feat4Desc">支援點擊看大圖、鍵盤左右鍵快速切圖、原圖細節清晰可見。</div>
            </div>
        </div>
    </div>

    <!-- Site Footer with Image Sources -->
    <footer class="site-footer">
        <p id="footerSrc">資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)</p>
        <p id="footerNote" style="margin-top: 6px; font-size: 0.82rem; color: #88998a;">非官方社群圖庫工具，僅供個人鑑賞與交流用途。</p>
    </footer>

    <script>
        const COUNTS = {{
            wall: {wall_count},
            floor: {floor_count},
            rug: {rug_count}
        }};

        const INDEX_I18N_DATA = {{
            'zh-TW': {{
                brand: '動森室內圖庫',
                nav_home: '首頁導覽',
                nav_wallpapers: '壁紙 (' + COUNTS.wall + ')',
                nav_floors: '地板 (' + COUNTS.floor + ')',
                nav_rugs: '地毯 (' + COUNTS.rug + ')',
                hero_badge: 'Animal Crossing: New Horizons',
                hero_title: '集合啦！動物森友會<br>室內裝潢圖庫全輯',
                hero_desc: '收錄全系列壁紙、地板與地毯的 1280x720 高清遊戲實景截圖與官方圖示。<br>支援實景大圖優先排序、即時搜尋、鍵盤方向鍵導航與離線個人最愛收藏。',
                wall_title: '壁紙圖庫',
                wall_count: COUNTS.wall + ' 款',
                wall_desc: '涵蓋常規商店、駱嵐不可思議壁紙、非賣品活動獎勵與三麗鷗聯名款。260 款室內 1280x720 實拍大圖與 52 款官方高畫質備選圖示。',
                wall_specs: ['📸 260 款實景大圖', '✨ 實景優先 + 名稱排序', '♥ 我的最愛'],
                wall_btn: '進入壁紙圖庫 ➔',
                floor_title: '地板圖庫',
                floor_count: COUNTS.floor + ' 款',
                floor_desc: '收錄實木拼花、復古磁磚、戶外自然場景、動態地磚與特殊材質地板。187 款室內鋪設 1280x720 實拍照與 28 款官方圖示。',
                floor_specs: ['📸 187 款實景大圖', '✨ 實景優先 + 名稱排序', '♥ 我的最愛'],
                floor_btn: '進入地板圖庫 ➔',
                rug_title: '地毯圖庫',
                rug_count: COUNTS.rug + ' 款',
                rug_desc: '全系列大、中、小型與趣味特殊造型地毯，包括駱嵐限定地毯、蔬果造型地毯與季節限定圖騰。完整標註遊戲內 1×1 ~ 5×5 佔地尺寸與 S/M/L 篩選分類。',
                rug_specs: ['📐 S / M / L 尺寸篩選', '✨ 尺寸大到小 + 字母排序', '♥ 我的最愛'],
                rug_btn: '進入地毯圖庫 ➔',
                features_title: '✨ 核心功能特色',
                feat1_title: '三語即時搜尋',
                feat1_desc: '支援繁體中文（台灣繁中）、英文以及日文原文即時過濾查找。',
                feat2_title: '英文字母 A-Z 排序',
                feat2_desc: '依照英文名稱字母順序整齊編排，方便精確定位與參照社群資料。',
                feat3_title: '離線個人收藏',
                feat3_desc: '點擊愛心即可標記喜歡的壁紙與地板，資料保存在瀏覽器本地。',
                feat4_title: '沉浸式全螢幕檢視',
                feat4_desc: '支援點擊看大圖、鍵盤左右鍵快速切圖、原圖細節清晰可見。',
                footer_src: '資料與圖片來源：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> 及 Nintendo《集合啦！動物森友會》(Animal Crossing: New Horizons)',
                footer_note: '非官方社群圖庫工具，僅供個人鑑賞與交流用途。'
            }},
            'en-US': {{
                brand: 'ACNH Interior Gallery',
                nav_home: 'Home',
                nav_wallpapers: 'Wallpapers (' + COUNTS.wall + ')',
                nav_floors: 'Flooring (' + COUNTS.floor + ')',
                nav_rugs: 'Rugs (' + COUNTS.rug + ')',
                hero_badge: 'Animal Crossing: New Horizons',
                hero_title: 'Animal Crossing: New Horizons<br>Complete Interior Gallery',
                hero_desc: 'Complete collection of wallpapers, flooring, and rugs with 1280x720 HD in-game screenshots and official icons.<br>Features screenshot-first sorting, real-time multilingual search, arrow key navigation, and offline favorites.',
                wall_title: 'Wallpapers',
                wall_count: COUNTS.wall + ' items',
                wall_desc: "Includes Nook's Cranny, Saharah mysterious wallpapers, seasonal event rewards, and Sanrio items. 260 HD in-game screenshots and 52 official icons.",
                wall_specs: ['📸 260 HD Screenshots', '✨ Screenshot-First Sort', '♥ Favorites'],
                wall_btn: 'Browse Wallpapers ➔',
                floor_title: 'Flooring',
                floor_count: COUNTS.floor + ' items',
                floor_desc: 'Parquet, vintage tiles, outdoor natural grounds, animated floors, and special textures. 187 HD in-game room photos and 28 official icons.',
                floor_specs: ['📸 187 HD Screenshots', '✨ Screenshot-First Sort', '♥ Favorites'],
                floor_btn: 'Browse Flooring ➔',
                rug_title: 'Rugs',
                rug_count: COUNTS.rug + ' items',
                rug_desc: 'Large, Medium, Small, and uniquely shaped rugs, including Saharah exclusives and seasonal designs. Annotated with 1×1 to 5×5 footprints and S/M/L filters.',
                rug_specs: ['📐 S / M / L Size Filter', '✨ Size + Name Sort', '♥ Favorites'],
                rug_btn: 'Browse Rugs ➔',
                features_title: '✨ Key Features',
                feat1_title: 'Trilingual Search',
                feat1_desc: 'Instant search across Traditional Chinese, English, and Japanese.',
                feat2_title: 'Alphabetical A-Z Order',
                feat2_desc: 'Arranged alphabetically by English name for easy lookup and community cross-referencing.',
                feat3_title: 'Local Favorites',
                feat3_desc: 'Bookmark your favorite items with a click, saved directly in your browser.',
                feat4_title: 'Fullscreen Lightbox',
                feat4_desc: 'Full HD preview with keyboard arrow navigation and thumbnail filmstrip.',
                footer_src: 'Data & images source: <a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> & Nintendo Animal Crossing: New Horizons',
                footer_note: 'Unofficial fan gallery tool, for personal appreciation and reference only.'
            }},
            'ja-JP': {{
                brand: 'あつ森インテリア図鑑',
                nav_home: 'ホーム',
                nav_wallpapers: 'かべがみ (' + COUNTS.wall + ')',
                nav_floors: 'ゆかいた (' + COUNTS.floor + ')',
                nav_rugs: 'ラグ (' + COUNTS.rug + ')',
                hero_badge: 'あつまれ どうぶつの森',
                hero_title: 'あつまれ どうぶつの森<br>インテリア図鑑 全集',
                hero_desc: 'すべてのかべがみ、ゆかいた、ラグを収録。1280x720のHD実機スクリーンショットと公式アイコン。<br>実機写真優先ソート、リアルタイム多言語検索、矢印キー操作、お気に入り保存に対応。',
                wall_title: 'かべがみ図鑑',
                wall_count: COUNTS.wall + ' 種',
                wall_desc: 'タヌキ商店、ローランのふしぎなかべがみ、イベント報酬、サンリオコラボまで網羅。260枚のHD実機写真と52枚の公式アイコン。',
                wall_specs: ['📸 260枚の実機写真', '✨ 実機写真優先ソート', '♥ お気に入り'],
                wall_btn: 'かべがみを見る ➔',
                floor_title: 'ゆかいた図鑑',
                floor_count: COUNTS.floor + ' 種',
                floor_desc: '木目調、タイル、屋外の自然な地面、動く床など多彩な床材。187枚のHD部屋写真と28枚の公式アイコン。',
                floor_specs: ['📸 187枚の実機写真', '✨ 実機写真優先ソート', '♥ お気に入り'],
                floor_btn: 'ゆかいたを見る ➔',
                rug_title: 'ラグ図鑑',
                rug_count: COUNTS.rug + ' 種',
                rug_desc: '大・中・小および特殊形状のラグを網羅。ローラン限定品や季節限定デザインを含む。1×1〜5×5の実寸サイズとS/M/L絞り込み対応。',
                rug_specs: ['📐 S/M/L サイズ絞り込み', '✨ サイズ順＋名前順', '♥ お気に入り'],
                rug_btn: 'ラグを見る ➔',
                features_title: '✨ 主な機能と特徴',
                feat1_title: '3言語リアルタイム検索',
                feat1_desc: '日本語・英語・繁体字中国語でのリアルタイム絞り込みに対応。',
                feat2_title: 'アルファベット順ソート',
                feat2_desc: '英語名称のアルファベット順に整理され、コミュニティ情報の参照に便利。',
                feat3_title: 'お気に入り機能',
                feat3_desc: 'ハートアイコンをクリックしてお気に入り登録。ブラウザに自動保存されます。',
                feat4_title: '全画面ビューアー',
                feat4_desc: '矢印キーでの高速切り替え、サムネイル一覧付きの高画質プレビュー。',
                footer_src: 'データ・画像出典：<a href="https://nookipedia.com/" target="_blank" rel="noopener">Nookipedia (Animal Crossing Wiki)</a> および 任天堂『あつまれ どうぶつの森』',
                footer_note: '非公式ファンサイトです。個人の鑑賞および交流を目的としています。'
            }}
        }};

        function changeLanguage(lang) {{
            if (!['zh-TW', 'en-US', 'ja-JP'].includes(lang)) return;
            currentLang = lang;
            try {{
                localStorage.setItem('acnh_lang', lang);
            }} catch(e) {{}}
            document.documentElement.lang = lang;

            var sel = document.getElementById('langSelect');
            if (sel && sel.value !== lang) sel.value = lang;

            applyLanguage(lang);
        }}

        function applyLanguage(lang) {{
            if (!INDEX_I18N_DATA[lang]) lang = 'zh-TW';
            const d = INDEX_I18N_DATA[lang];

            if (lang === 'en-US') {{
                document.title = 'Animal Crossing: New Horizons - Complete Interior Gallery (Wallpapers / Flooring / Rugs)';
            }} else if (lang === 'ja-JP') {{
                document.title = 'あつまれ どうぶつの森 - インテリア図鑑 全集 (かべがみ / ゆかいた / ラグ)';
            }} else {{
                document.title = '集合啦！動物森友會 - 室內裝潢圖庫全輯 (壁紙 / 地板 / 地毯)';
            }}

            const navBrand = document.getElementById('navBrand');
            if (navBrand) navBrand.textContent = d.brand;
            const navHome = document.getElementById('navHome');
            if (navHome) navHome.textContent = d.nav_home;
            const navWall = document.getElementById('navWallpapers');
            if (navWall) navWall.textContent = d.nav_wallpapers;
            const navFloor = document.getElementById('navFloors');
            if (navFloor) navFloor.textContent = d.nav_floors;
            const navRug = document.getElementById('navRugs');
            if (navRug) navRug.textContent = d.nav_rugs;

            const heroBadge = document.getElementById('heroBadge');
            if (heroBadge) heroBadge.textContent = d.hero_badge;
            const heroTitle = document.getElementById('heroTitle');
            if (heroTitle) heroTitle.innerHTML = d.hero_title;
            const heroDesc = document.getElementById('heroDesc');
            if (heroDesc) heroDesc.innerHTML = d.hero_desc;

            // Cards
            document.getElementById('wallCardTitle').textContent = d.wall_title;
            document.getElementById('wallCardCount').textContent = d.wall_count;
            document.getElementById('wallCardDesc').textContent = d.wall_desc;
            document.getElementById('wallCardBtn').textContent = d.wall_btn;
            document.getElementById('wallSpecs').innerHTML = d.wall_specs.map(s => `<span class="spec-tag">${{s}}</span>`).join('');

            document.getElementById('floorCardTitle').textContent = d.floor_title;
            document.getElementById('floorCardCount').textContent = d.floor_count;
            document.getElementById('floorCardDesc').textContent = d.floor_desc;
            document.getElementById('floorCardBtn').textContent = d.floor_btn;
            document.getElementById('floorSpecs').innerHTML = d.floor_specs.map(s => `<span class="spec-tag">${{s}}</span>`).join('');

            document.getElementById('rugCardTitle').textContent = d.rug_title;
            document.getElementById('rugCardCount').textContent = d.rug_count;
            document.getElementById('rugCardDesc').textContent = d.rug_desc;
            document.getElementById('rugCardBtn').textContent = d.rug_btn;
            document.getElementById('rugSpecs').innerHTML = d.rug_specs.map(s => `<span class="spec-tag">${{s}}</span>`).join('');

            // Features
            document.getElementById('featuresTitle').textContent = d.features_title;
            document.getElementById('feat1Title').textContent = d.feat1_title;
            document.getElementById('feat1Desc').textContent = d.feat1_desc;
            document.getElementById('feat2Title').textContent = d.feat2_title;
            document.getElementById('feat2Desc').textContent = d.feat2_desc;
            document.getElementById('feat3Title').textContent = d.feat3_title;
            document.getElementById('feat3Desc').textContent = d.feat3_desc;
            document.getElementById('feat4Title').textContent = d.feat4_title;
            document.getElementById('feat4Desc').textContent = d.feat4_desc;

            // Footer
            document.getElementById('footerSrc').innerHTML = d.footer_src;
            document.getElementById('footerNote').textContent = d.footer_note;
        }}

        // Clean up any Service Worker
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.getRegistrations().then(function(regs) {{
                for (var r of regs) r.unregister();
            }});
        }}

        // Initialize language
        var sel = document.getElementById('langSelect');
        if (sel) sel.value = currentLang;
        applyLanguage(currentLang);
    </script>
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

    stats_counts = {
        "wallpapers": len(wallpapers),
        "floors": len(floors),
        "rugs": len(rugs),
    }

    generate_gallery_page(
        items_data=wallpapers,
        page_type="wallpapers",
        page_title="壁紙圖庫全輯",
        page_icon="🖼️",
        storage_key="acnh_wallpaper_favorites_v1",
        out_filename="wallpapers.html",
        stats_counts=stats_counts,
    )

    generate_gallery_page(
        items_data=floors,
        page_type="floors",
        page_title="地板圖庫全輯",
        page_icon="🪵",
        storage_key="acnh_floor_favorites_v1",
        out_filename="floors.html",
        stats_counts=stats_counts,
    )

    generate_gallery_page(
        items_data=rugs,
        page_type="rugs",
        page_title="地毯圖庫全輯",
        page_icon="🧶",
        storage_key="acnh_rug_favorites_v1",
        out_filename="rugs.html",
        stats_counts=stats_counts,
    )

    generate_index_page(stats_counts)
    generate_sw_file(PAGES_DIR)
    print("All pages generated successfully!")

def generate_sw_file(pages_dir):
    sw_path = os.path.join(pages_dir, "sw.js")
    sw_code = """// ACNH Interior Gallery Service Worker (Cache Storage)
const CACHE_NAME = 'acnh-gallery-v2';
const STATIC_ASSETS = [
    './index.html',
    './wallpapers.html',
    './floors.html',
    './rugs.html'
];

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('Initial static asset cache partial fail:', err);
            });
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);

    // Image assets: Cache-First strategy (Instant 0ms retrieval, cache on miss)
    if (req.destination === 'image' || url.pathname.match(/\\.(webp|jpg|jpeg|png|gif|svg)$/i) || url.pathname.includes('/images/')) {
        event.respondWith(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.match(req).then((cachedResponse) => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return fetch(req).then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(req, networkResponse.clone());
                        }
                        return networkResponse;
                    }).catch(() => {
                        return cachedResponse || Response.error();
                    });
                });
            })
        );
        return;
    }

    // HTML / JS / Other: Stale-While-Revalidate / Network-First
    event.respondWith(
        fetch(req).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
                const responseClone = networkResponse.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(req, responseClone);
                });
            }
            return networkResponse;
        }).catch(() => {
            return caches.match(req);
        })
    );
});
"""
    with open(sw_path, "w", encoding="utf-8") as f:
        f.write(sw_code)
    print(f"Generated {sw_path}")

if __name__ == "__main__":
    build_all()
