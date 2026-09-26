import json, sys

wallpapers = json.load(open('wallpapers.json', encoding='utf-8'))
floors = json.load(open('floors.json', encoding='utf-8'))
rugs = json.load(open('rugs.json', encoding='utf-8'))

print("==================================================")
print("1. Wallpapers marked is_special == 1 but sold in Nook's Cranny or Crafting")
print("==================================================")
for it in wallpapers:
    if it.get('is_special') == 1:
        src = it.get('source', '').lower()
        tag = it.get('tag', '')
        if "cranny" in src or tag == 'Japanese Style':
            print(f"[{it['default_sort_order']:3d}] {it['name_zh']} ({it['name_en']}) | tag: {tag} | src: {it['source']} | vfx: {it.get('vfx')}")

print("\n==================================================")
print("2. Check all Fruit items across wallpapers, floors, rugs")
print("==================================================")
for fname, data in [('Wallpapers', wallpapers), ('Floors', floors), ('Rugs', rugs)]:
    fruit_items = [it for it in data if 'fruit' in it.get('tag', '').lower() or any(k in it.get('name_zh', '') for k in ['蘋果', '櫻桃', '桃子', '梨子', '橘子', '西瓜'])]
    print(f"\n--- {fname} Fruit items ---")
    for it in sorted(fruit_items, key=lambda x: x.get('default_sort_order', 0)):
        print(f"[{it['default_sort_order']:3d}] {it['name_zh']} ({it['name_en']}) | tag: {it.get('tag')} | ver: {it.get('version_added')}")

print("\n==================================================")
print("3. Check Japanese / Asian / Zen items in wallpapers & floors")
print("==================================================")
for fname, data in [('Wallpapers', wallpapers), ('Floors', floors)]:
    jp_items = [it for it in data if any(k in it.get('tag', '').lower() for k in ['japanese', 'tea room', 'tatami', 'asia']) or any(k in it.get('name_zh', '') for k in ['日式', '拉門', '障子', '茶室', '榻榻米', '和風', '枯山水', '金箔', '竹簾'])]
    print(f"\n--- {fname} Japanese items ---")
    for it in sorted(jp_items, key=lambda x: x.get('default_sort_order', 0)):
        print(f"[{it['default_sort_order']:3d}] {it['name_zh']} ({it['name_en']}) | tag: {it.get('tag')} | is_sp: {it.get('is_special')} | src: {it.get('source')}")
