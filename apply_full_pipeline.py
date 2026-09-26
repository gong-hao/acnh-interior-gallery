import json
import csv
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

COLOR_RANK = {
    'white': 1, 'ivory': 1, 'cream': 1,
    'beige': 2, 'natural': 2, 'brown': 2, 'tan': 2, 'chocolate': 2,
    'gray': 3, 'grey': 3, 'slate': 3,
    'black': 4, 'dark': 4,
    'yellow': 5, 'orange': 5,
    'pink': 6, 'peach': 6, 'red': 6,
    'green': 7, 'olive': 7, 'mint': 7,
    'aqua': 8, 'cyan': 8, 'blue': 8, 'navy': 8,
    'purple': 9, 'violet': 9,
    'colorful': 10, 'rainbow': 10
}

def get_color_rank(c1, c2, name_en='', name_zh=''):
    c1_l = (c1 or '').lower().strip()
    c2_l = (c2 or '').lower().strip()
    nl = name_en.lower()
    
    kw_map = [
        (['white', '白'], 1),
        (['beige', 'brown', 'chocolate', 'natural-wood', 'light-wood', 'dark-wood', '棕', '茶', '咖', '木', '褐', '米'], 2),
        (['gray', 'grey', '灰'], 3),
        (['black', '黑'], 4),
        (['yellow', 'orange', '黃', '橘', '橙'], 5),
        (['pink', 'red', 'peach', '粉', '紅', '桃'], 6),
        (['green', 'olive', 'mint', '綠', '薄荷', '青'], 7),
        (['blue', 'aqua', 'cyan', 'navy', '藍', '水'], 8),
        (['purple', 'violet', '紫'], 9),
        (['colorful', 'rainbow', '巧拼', '彩'], 10),
    ]
    for words, rank in kw_map:
        if any(w in nl or w in name_zh for w in words):
            return rank
            
    r1 = COLOR_RANK.get(c1_l, 99)
    r2 = COLOR_RANK.get(c2_l, 99)
    return min(r1, r2)

# =========================================================================
# WALLPAPERS PIPELINE
# =========================================================================

def get_wallpaper_series_key(item):
    tag = item.get('tag', '')
    nl = item.get('name_en', '').lower().strip()
    fn_base = item.get('filename_base', '')
    
    # 1. Fruit series: all 5 fruit walls together
    if tag == 'Fruit Walls' or nl in ['apple wall', 'cherry wall', 'orange wall', 'peach wall', 'pear wall']:
        return 'Series_Fruit_Walls'
        
    # 2. Japanese Sliding Screens (Shoji, Fusuma, Screen)
    if nl in ['screen wall', 'gold-screen wall', 'shoji screen', 'modern shoji-screen wall']:
        return 'Series_Japanese_Screen_Walls'
        
    # 3. Sanrio
    if 'sanrio' in tag.lower() or any(w in nl for w in ['cinnamoroll', 'hello kitty', 'kerokerokeroppi', 'kiki & lala', 'my melody', 'pompompurin']):
        return 'Series_Sanrio_wallpapers'
        
    # 4. Mario
    if 'mario' in tag.lower() or 'mushroom mural' in nl:
        return 'Series_Mario_wallpapers'
        
    # 5. Zelda
    if 'zelda' in tag.lower() or 'korok forest' in nl:
        return 'Series_Zelda_wallpapers'
        
    # 6. Splatoon
    if 'splatoon' in tag.lower() or 'eeltail alley' in nl:
        return 'Series_Splatoon_wallpapers'
        
    # 7. LEGO
    if 'lego' in tag.lower():
        return 'Series_LEGO_wallpapers'
        
    # 8. Wedding
    if nl in ['white wedding wall', 'brown wedding wall', 'green wedding wall']:
        return 'Series_Wedding_Cloth_Walls'

    # 9. Chocolate
    if tag == 'Chocolate' or nl in ['white-chocolate wall', 'dark-chocolate wall', 'strawberry-chocolate wall']:
        return 'Series_Chocolate_wallpapers'

    # 10. Locker rooms
    if 'locker-room' in nl:
        return 'Series_Locker_Room_wallpapers'

    # 11. Shelving
    if 'shelving wall' in nl:
        return 'Series_Shelving_wallpapers'

    # 12. Moroccan
    if 'moroccan-style wall' in nl:
        return 'Series_Moroccan_wallpapers'

    # 13. European
    if 'european-style wall' in nl:
        return 'Series_European_wallpapers'

    # 14. Window panel walls
    if 'window-panel wall' in nl:
        return 'Series_Window_Panel_wallpapers'

    return fn_base if fn_base else item.get('name_en')

def classify_wallpaper(item):
    tag = item.get('tag', '')
    nl = item.get('name_en', '').lower().strip()
    vfx = item.get('vfx', 'No')
    src = item.get('source', '')
    
    # Rule 1: Nook's Cranny store walls are ALWAYS regular walls (is_special = 0)
    if 'cranny' in src.lower():
        is_special = False
    elif tag in [
        'Japanese Style', 'Tea Room Walls', 'Fruit Walls', 'Wood Walls', 'Brick',
        'Stone Walls', 'Iron Walls', 'Tin Walls', 'Metro Walls', 'Tile Walls',
        'Two-Tone Tile Walls', 'Honeycomb', 'Stucco Walls', 'Simple Walls',
        'Cloth Walls', 'Stripe Walls', 'Dot', 'Cute Walls', 'Dollhouse Walls',
        'Toy Walls', 'Puzzle Walls', 'Pegboard Walls', 'Flower Walls',
        'Flower Pop Walls', 'Rose Walls', 'Heart Walls', 'Camouflage', 'Panel Mold Walls'
    ] and 'saharah' not in src.lower():
        is_special = False
    elif 'saharah' in src.lower() or vfx == 'Yes' or any(w in tag for w in ['Special', 'Zelda', 'Splatoon', 'Mario', 'Sanrio', 'LEGO', 'WallFacility', 'Neta']):
        is_special = True
    else:
        is_special = False
        
    if not is_special:
        # Regular wall clusters (0 - 85)
        if any(w in tag for w in ['Wood', 'Herringbone', 'Plank']) or 'wood' in nl or 'basic wall' in nl or 'window-panel' in nl:
            cluster = 10
        elif any(w in tag for w in ['Brick', 'Stone', 'Iron', 'Tin', 'Metro', 'Arched-window']):
            cluster = 20
        elif 'Tile' in tag or 'Honeycomb' in tag:
            cluster = 30
        elif any(w in tag for w in ['Stucco', 'Simple', 'Cloth', 'Stripe', 'Dot']):
            cluster = 40
        elif any(w in tag for w in ['Japanese', 'Tea Room']) or any(w in nl for w in ['fusuma', 'shoji', 'tatami', 'bamboo', 'screen wall']):
            cluster = 50
        elif 'Asia' in tag or 'imperial' in nl or 'dynasty' in nl:
            cluster = 60
        elif any(w in tag for w in ['Art Deco', 'Crown', 'Manor', 'Hall', 'Morocco', 'Country', 'Diner', 'Panel Mold', 'Library']):
            cluster = 70
        elif tag == 'Fruit Walls' or nl in ['apple wall', 'cherry wall', 'orange wall', 'peach wall', 'pear wall']:
            cluster = 80
        else:
            cluster = 85
        return (0, cluster)
    else:
        # Special wall clusters (100 - 190)
        # 190: Collaborations
        if any(w in tag.lower() for w in ['mario', 'sanrio', 'lego', 'zelda', 'splatoon']) or any(w in nl for w in ['mushroom mural', 'korok forest', 'eeltail alley', 'cinnamoroll', 'hello kitty', 'kerokerokeroppi', 'kiki & lala', 'my melody', 'pompompurin']):
            return (1, 190)
            
        # 180: Cosmic, Sci-Fi, Holiday, Wedding, Fantasy
        if any(w in nl for w in ['starry', 'pirate', 'jingle', 'wedding', 'prom']) or nl == 'sci-fi wall':
            return (1, 180)
            
        # 100: Sky & Weather & City Vistas
        if nl in ['sky wall', 'stormy-night wall', 'cityscape wall', 'skyscraper wall', 'fireworks-show wall', 'aurora wall']:
            return (1, 100)
            
        # 110: Water & Ocean
        if nl in ['sea view', 'ocean-horizon wall', 'tropical vista', 'underwater wall', 'mermaid wall'] or 'ocean' in nl:
            return (1, 110)
            
        # 120: Mountain & Vistas & Terrain
        if nl in ['summit wall', 'meadow vista', 'rice-paddy wall', 'desert vista', 'western vista', 'limestone-cave wall', 'magma-cavern wall', 'dig-site wall']:
            return (1, 120)
            
        # 140: Snow & Ice
        if nl in ['falling-snow wall', 'ski-slope wall', 'ice wall', 'iceberg wall']:
            return (1, 140)
            
        # 150: Outdoor Facilities, Sports, Construction, Yard, Fence
        if any(w in nl for w in ['stadium', 'ringside', 'backyard-fence', 'chain-link fence', 'outdoor-window', 'construction-site', 'graveyard', 'street-art', 'paintball', 'rock-climbing', 'garbage-heap', 'ramshackle']):
            return (1, 150)
            
        # 130: Nature & Forests & Gardens & Seasonal
        if any(w in nl for w in ['cherry-blossom', 'autumn', 'mangrove', 'tree-lined', 'misty-garden', 'mossy-garden', 'brick garden', 'glowing-moss', 'ruins wall', 'ivy wall']) or 'nature' in tag.lower():
            return (1, 130)
            
        # 170: Ancient, Cultural & Exotic Special
        if any(w in nl for w in ['ancient wall', 'exquisite wall', 'imperial wall', 'dojo wall', 'straw wall', 'european-style wall', 'moroccan-style wall', 'antique brick', 'mortar wall', 'chocolate', 'kisses']) or any(w in tag.lower() for w in ['asia', 'chocolate']):
            return (1, 170)

        # 160: Indoor Facilities, Commercial, Shops, Tech, Rooms
        return (1, 160)

def process_wallpapers():
    print("Processing Wallpapers...")
    items = json.load(open('wallpapers.json', encoding='utf-8'))
    for it in items:
        it['series_key'] = get_wallpaper_series_key(it)
        is_sp, cl = classify_wallpaper(it)
        it['is_special'] = 1 if is_sp else 0
        it['style_cluster'] = cl
        it['color_rank'] = get_color_rank(it.get('color_1'), it.get('color_2'), it.get('name_en', ''), it.get('name_zh', ''))

    # Group by series_key
    series_groups = defaultdict(list)
    for it in items:
        series_groups[it['series_key']].append(it)
        
    for skey, g_items in series_groups.items():
        min_sp = min(it['is_special'] for it in g_items)
        min_ver = min(it['version_rank'] for it in g_items)
        min_cl = min(it['style_cluster'] for it in g_items)
        min_nid = min(it['nookipedia_id'] for it in g_items)
        for it in g_items:
            it['series_is_special'] = min_sp
            it['series_version_rank'] = min_ver
            it['series_style_cluster'] = min_cl
            it['series_anchor_id'] = min_nid

    items.sort(key=lambda x: (
        x['series_is_special'],
        x['series_style_cluster'],
        x['series_version_rank'],
        x['series_anchor_id'],
        x['color_rank'],
        x.get('variant_id', 0),
        x['nookipedia_id']
    ))

    for idx, it in enumerate(items):
        it['default_sort_order'] = idx

    # Check contiguity
    for skey, g_items in series_groups.items():
        if len(g_items) > 1:
            indices = [it['default_sort_order'] for it in g_items]
            indices.sort()
            for i in range(len(indices)-1):
                if indices[i+1] - indices[i] != 1:
                    print(f"ERROR: Gap in series {skey}: {indices}")

    json.dump(items, open('wallpapers.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    save_csv('wallpapers.csv', items)
    print(f"Wallpapers processed successfully: {len(items)} items saved.")

# =========================================================================
# FLOORS PIPELINE
# =========================================================================

def get_floor_series_key(item):
    tag = item.get('tag', '')
    nl = item.get('name_en', '').lower().strip()
    fn_base = item.get('filename_base', '')
    
    # 1. Sanrio
    if 'sanrio' in tag.lower() or any(w in nl for w in ['cinnamoroll', 'hello kitty', 'kerokerokeroppi', 'kiki & lala', 'my melody', 'pompompurin']):
        return 'Series_Sanrio_floors'
        
    # 2. Mario
    if 'mario' in tag.lower() or nl == 'block flooring':
        return 'Series_Mario_floors'
        
    # 3. Zelda
    if 'zelda' in tag.lower() or 'korok' in nl:
        return 'Series_Zelda_floors'
        
    # 4. Splatoon
    if 'splatoon' in tag.lower() or 'tricolor turf war' in nl:
        return 'Series_Splatoon_floors'
        
    # 5. LEGO
    if 'lego' in tag.lower():
        return 'Series_LEGO_floors'
        
    # 6. Chocolate
    if tag == 'Chocolate' or 'chocolates flooring' in nl:
        return 'Series_Chocolate_floors'

    # 7. Tatami
    if 'tatami' in nl:
        return fn_base if fn_base else 'Series_Tatami_floors'

    return fn_base if fn_base else item.get('name_en')

def classify_floor(item):
    tag = item.get('tag', '')
    nl = item.get('name_en', '').lower().strip()
    vfx = item.get('vfx', 'No')
    src = item.get('source', '')
    
    # Rule 1: Nook's Cranny store floors are regular floors (is_special = 0)
    if 'cranny' in src.lower():
        is_special = False
    elif 'saharah' in src.lower() or vfx == 'Yes' or any(w in tag for w in ['Special', 'Zelda', 'Splatoon', 'Mario', 'Sanrio', 'LEGO', 'FloorFacility', 'Neta']):
        is_special = True
    else:
        is_special = False
        
    if not is_special:
        if any(w in tag for w in ['Wood', 'Parquet', 'Board', 'Plank']) or 'wood' in nl or 'parquet' in nl:
            cluster = 10
        elif any(w in tag for w in ['Tile', 'Brick', 'Stone', 'Iron', 'Block']):
            cluster = 20
        elif any(w in tag for w in ['Tatami', 'Rush', 'Bamboo']):
            cluster = 50
        elif any(w in tag for w in ['Carpet', 'Cloth', 'Rubber', 'Mat']):
            cluster = 40
        else:
            cluster = 60
        return (0, cluster)
    else:
        # Special floor clusters
        # 190: Collaborations
        if any(w in tag.lower() for w in ['mario', 'sanrio', 'lego', 'zelda', 'splatoon']):
            return (1, 190)
            
        # 180: Cosmic & Fantasy
        if any(w in nl for w in ['magic-circle', 'sci-fi', 'lunar surface', 'galaxy']):
            return (1, 180)
            
        # 110: Water & Ocean
        if any(w in nl for w in ['water flooring', 'underwater flooring', 'mermaid flooring', 'sandy-beach', 'starry-sands', 'oasis']):
            return (1, 110)
            
        # 120: Mountain & Terrain
        if any(w in nl for w in ['rocky-mountain', 'lava', 'western desert', "saharah's desert", 'swamp', 'dirt flooring', 'field flooring']):
            return (1, 120)
            
        # 140: Snow & Ice
        if any(w in nl for w in ['ski-slope', 'ice flooring', 'iceberg flooring']):
            return (1, 140)
            
        # 130: Nature & Forests & Seasonal
        if any(w in nl for w in ['cherry-blossom', 'fallen leaves', 'jungle', 'mossy-garden', 'wildflower', 'glowing-moss', 'broken stone-path', 'rope-net', 'forest flooring']):
            return (1, 130)
            
        # 150: Outdoor Roads & Sports
        if any(w in nl for w in ['racetrack', 'boxing-ring', 'sumo ring', 'sidewalk', 'crosswalk', 'highway', 'parking', 'scramble crosswalk', 'train-station', 'paintball', 'sandlot', 'hopscotch', 'ramshackle', 'gravel flooring']):
            return (1, 150)
            
        # 170: Luxury & Cultural & Exotic
        if any(w in nl for w in ['pyramid', 'imperial tile', 'palace tile', 'chocolates flooring', 'floral rush-mat', 'moroccan art-tile', 'old board', 'old stone-tile', 'natural flooring']):
            return (1, 170)
            
        # 160: Indoor Facilities & Commercial
        return (1, 160)

def process_floors():
    print("Processing Floors...")
    items = json.load(open('floors.json', encoding='utf-8'))
    for it in items:
        it['series_key'] = get_floor_series_key(it)
        is_sp, cl = classify_floor(it)
        it['is_special'] = 1 if is_sp else 0
        it['style_cluster'] = cl
        it['color_rank'] = get_color_rank(it.get('color_1'), it.get('color_2'), it.get('name_en', ''), it.get('name_zh', ''))

    # Group by series_key
    series_groups = defaultdict(list)
    for it in items:
        series_groups[it['series_key']].append(it)
        
    for skey, g_items in series_groups.items():
        min_sp = min(it['is_special'] for it in g_items)
        min_ver = min(it['version_rank'] for it in g_items)
        min_cl = min(it['style_cluster'] for it in g_items)
        min_nid = min(it['nookipedia_id'] for it in g_items)
        for it in g_items:
            it['series_is_special'] = min_sp
            it['series_version_rank'] = min_ver
            it['series_style_cluster'] = min_cl
            it['series_anchor_id'] = min_nid

    items.sort(key=lambda x: (
        x['series_is_special'],
        x['series_style_cluster'],
        x['series_version_rank'],
        x['series_anchor_id'],
        x['color_rank'],
        x.get('variant_id', 0),
        x['nookipedia_id']
    ))

    for idx, it in enumerate(items):
        it['default_sort_order'] = idx

    # Check contiguity
    for skey, g_items in series_groups.items():
        if len(g_items) > 1:
            indices = [it['default_sort_order'] for it in g_items]
            indices.sort()
            for i in range(len(indices)-1):
                if indices[i+1] - indices[i] != 1:
                    print(f"ERROR: Gap in series {skey}: {indices}")

    json.dump(items, open('floors.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    save_csv('floors.csv', items)
    print(f"Floors processed successfully: {len(items)} items saved.")

# =========================================================================
# RUGS PIPELINE
# =========================================================================

def get_rug_series_key(item):
    tag = item.get('tag', '')
    nl = item.get('name_en', '').lower().strip()
    fn_base = item.get('filename_base', '')
    
    # 1. Watermelon rugs 2.0
    if 'watermelon rug' in nl:
        return 'Series_Watermelon_Rugs_2.0'
        
    # 2. Fruit Rugs 1.0 (5 starter fruits)
    if tag == 'Fruit Rugs' or nl in ['apple rug', 'cherry rug', 'orange rug', 'peach rug', 'pear rug']:
        return 'Series_Fruit_Rugs_1.0'
        
    # 3. Sanrio
    if 'sanrio' in tag.lower() or any(w in nl for w in ['cinnamoroll', 'hello kitty', 'kerokerokeroppi', 'kiki & lala', 'my melody', 'pompompurin']):
        return 'Series_Sanrio_rugs'
        
    # 4. Mario
    if 'mario' in tag.lower() or any(w in nl for w in ['1-up', 'yoshi', '? block', 'mushroom rug']):
        return 'Series_Mario_rugs'
        
    # 5. Zelda
    if 'zelda' in tag.lower() or 'korok' in nl:
        return 'Series_Zelda_rugs'
        
    # 6. Splatoon
    if 'splatoon' in tag.lower() or 'squid' in nl:
        return 'Series_Splatoon_rugs'
        
    # 7. LEGO
    if 'lego' in tag.lower():
        return 'Series_LEGO_rugs'

    # 8. Bamboo rugs & mats
    if 'bamboo' in nl:
        if 'bath mat' in nl:
            return 'Series_Bamboo_Bath_Mat_rugs'
        elif 'bamboo rug' in nl:
            return 'Series_Bamboo_Rug_rugs'
        elif 'bamboo mat' in nl:
            return 'Series_Bamboo_Mat_rugs'

    return fn_base if fn_base else item.get('name_en')

def process_rugs():
    print("Processing Rugs...")
    items = json.load(open('rugs.json', encoding='utf-8'))
    for it in items:
        it['series_key'] = get_rug_series_key(it)
        it['color_rank'] = get_color_rank(it.get('color_1'), it.get('color_2'), it.get('name_en', ''), it.get('name_zh', ''))

    # Group by series_key
    series_groups = defaultdict(list)
    for it in items:
        series_groups[it['series_key']].append(it)
        
    for skey, g_items in series_groups.items():
        min_sp = min(it['is_special'] for it in g_items)
        min_ver = min(it['version_rank'] for it in g_items)
        min_cl = min(it['style_cluster'] for it in g_items)
        min_nid = min(it['nookipedia_id'] for it in g_items)
        for it in g_items:
            it['series_is_special'] = min_sp
            it['series_version_rank'] = min_ver
            it['series_style_cluster'] = min_cl
            it['series_anchor_id'] = min_nid

    items.sort(key=lambda x: (
        x['series_is_special'],
        x['series_style_cluster'],
        x['series_version_rank'],
        x['series_anchor_id'],
        x['color_rank'],
        x.get('variant_id', 0),
        x['nookipedia_id']
    ))

    for idx, it in enumerate(items):
        it['default_sort_order'] = idx

    # Check contiguity
    for skey, g_items in series_groups.items():
        if len(g_items) > 1:
            indices = [it['default_sort_order'] for it in g_items]
            indices.sort()
            for i in range(len(indices)-1):
                if indices[i+1] - indices[i] != 1:
                    print(f"ERROR: Gap in series {skey}: {indices}")

    json.dump(items, open('rugs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    save_csv('rugs.csv', items)
    print(f"Rugs processed successfully: {len(items)} items saved.")

def save_csv(filename, items):
    if not items:
        return
    fieldnames = list(items[0].keys())
    # Exclude internal non-csv keys if any
    for k in ['area', 'max_side', 'index']:
        if k in fieldnames:
            fieldnames.remove(k)
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for it in items:
            writer.writerow(it)

if __name__ == '__main__':
    process_wallpapers()
    process_floors()
    process_rugs()
    print("\n--- All 3 datasets updated successfully! ---")
