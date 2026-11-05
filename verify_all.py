# -*- coding: utf-8 -*-
import sys
import os

from research_engine import BUILTIN_INTELLIGENCE_FEEDS, LogisticsResearchEngine
from photo_curator import CURATED_ACTION_PHOTOS, get_action_photo_for_topic
from database import get_recently_posted_titles, get_recently_used_photos

def test_everything():
    print(f"=== BUILTIN FEEDS VERIFICATION ===")
    total = len(BUILTIN_INTELLIGENCE_FEEDS)
    print(f"Total feeds: {total}")
    assert total == 36, f"Expected 36 feeds, got {total}"

    slots = {}
    for f in BUILTIN_INTELLIGENCE_FEEDS:
        s = f.get("slot")
        slots[s] = slots.get(s, 0) + 1
    print(f"Feeds per slot: {slots}")
    assert slots == {"slot_morning": 12, "slot_midday": 12, "slot_evening": 12}, f"Unexpected slot distribution: {slots}"

    titles_km = [f["title_km"] for f in BUILTIN_INTELLIGENCE_FEEDS]
    titles_en = [f["title_en"] for f in BUILTIN_INTELLIGENCE_FEEDS]
    assert len(set(titles_km)) == 36, "Duplicate Khmer title found!"
    assert len(set(titles_en)) == 36, "Duplicate English title found!"
    print("All 36 titles in Khmer and English are 100% unique.")

    categories = set(f.get("photo_category") for f in BUILTIN_INTELLIGENCE_FEEDS)
    print(f"Photo categories used across feeds: {categories}")
    for cat in categories:
        assert cat in CURATED_ACTION_PHOTOS, f"Category '{cat}' missing from CURATED_ACTION_PHOTOS!"

    print("\n=== PHOTO CURATOR VERIFICATION ===")
    total_photos = sum(len(p) for p in CURATED_ACTION_PHOTOS.values())
    unique_photos = len(set(photo["url"] for bucket in CURATED_ACTION_PHOTOS.values() for photo in bucket))
    print(f"Total curated photos: {total_photos}")
    print(f"Unique curated photo URLs: {unique_photos}")
    assert total_photos == unique_photos, "Duplicate photo URL found within CURATED_ACTION_PHOTOS!"

    print("\n=== ENGINE ROTATION & DEDUPLICATION TEST ===")
    engine = LogisticsResearchEngine()
    
    # Test generation for each slot
    used_titles = set()
    used_photos = set()

    for slot_name in ["slot_morning", "slot_midday", "slot_evening"]:
        briefing = engine.get_latest_market_briefing_sync(category_filter=slot_name)
        print(f"[{slot_name}] Selected: {briefing['title_en'][:45]}... | Photo: {briefing['photo_title']}")
        assert briefing["title_en"] not in used_titles, "Briefing title was duplicated!"
        assert briefing["photo_url"] not in used_photos, "Photo was duplicated!"
        used_titles.add(briefing["title_en"])
        used_photos.add(briefing["photo_url"])

    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_everything()
