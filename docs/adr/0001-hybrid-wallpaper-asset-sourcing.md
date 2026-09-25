# 0001 Hybrid Wallpaper Asset Sourcing

## Context
ACNH features 312 unique wallpapers. Nookipedia maintains 259 high-resolution (1280x720) in-game room screenshots, but lacks screenshots for 53 wallpapers introduced in the 2.0 update and DLCs. Web and video searches showed no single comprehensive video catalog exists to programmatically extract the remaining 53 in-game room screenshots.

## Decision
Adopt a hybrid asset acquisition pipeline:
1. For the 259 base wallpapers, download the community-uploaded 1280x720 in-game room screenshots from Nookipedia.
2. For the 53 missing 2.0 wallpapers, fallback to official high-resolution inventory/storage item icons from Nookipedia/ACNH datamine assets.
3. Explicitly flag `has_in_game_screenshot: false` in metadata and generate a separate `missing_screenshots.csv` tracking list so missing room screenshots can be incrementally replaced when community photography becomes available.
4. Name all assets using `TraditionalChinese_English.ext` and provide both JSON/CSV metadata indexes and an offline HTML gallery.
