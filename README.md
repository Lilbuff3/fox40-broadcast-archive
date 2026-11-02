# FOX40 Broadcast Archive (`@DeadstockTapes` & `@UnairedCaseFiles`)

Complete cataloging, `59.94 fps` optical restoration (`bwdif`), narration, VCR OSD thumbnail generation, and multi-channel publishing repository for the **FOX40 Broadcast Archive** (`1,500+` digitized broadcast files from 1973–2018, including `103` historical, sports, true-crime, and California wildfire master reels).

---

## Repository Structure

```text
fox40-broadcast-archive/
├── AGENTS.md                  # Canonical project rules, Drive IDs & pipeline architecture
├── CLAUDE.md                  # @AGENTS.md pointer for Claude Code
├── catalog/
│   ├── MASTER_CATALOG.html    # Interactive searchable HTML archive catalog
│   ├── master_catalog.json    # Complete machine-readable metadata for 1,500+ files
│   ├── vault_75_audit_results.json
│   └── launch_wave1_manifest.json
├── docs/
│   ├── 01_archive_structure_and_drive_ids.md
│   ├── 02_complete_103_vault_visual_audit.md
│   ├── 03_channel_branding_and_thumbnail_system.md
│   ├── 04_footage_utilization_and_monetization_plan.md
│   ├── 05_launch_wave1_posting_pack.md
│   ├── 06_wave1_scripts_and_b2b_pitches.md
│   ├── 07_platform_distribution_evaluation.md
│   └── 08_vault_significance_ranking.md
├── assets/
│   ├── branding/              # 1-Word Deadstock Tapes crest avatars, Unaired Case Files logos & banners
│   ├── mockups/               # Full YouTube Channel Page Mockups & 60-frame candidate contact sheets
│   └── thumbnails/
│       ├── deadstock_tapes/   # MTV_01..05 VCR OSD 1280x720 YouTube thumbs & 1080x1920 vertical covers
│       └── unaired_case_files/# UCF_01..05 VCR OSD 1280x720 YouTube thumbs & 1080x1920 vertical covers
└── scripts/
    ├── audit_all_74_vault_reels.py
    ├── inspect_bloopers_and_fire.py
    ├── build_launch_wave1_videos.py
    ├── build_modern_2026_logos.py
    ├── rebuild_best_practice_thumbs_and_pages.py
    └── build_distribution_pack.py
```

---

## Quick Start

1. **Read Project Rules & Drive IDs:** See [`AGENTS.md`](AGENTS.md) and [`docs/03_channel_branding_and_thumbnail_system.md`](docs/03_channel_branding_and_thumbnail_system.md).
2. **Browse the Visual Mockups:**
   * [`assets/mockups/YouTube_Page_Mockup_DeadstockTapes.png`](assets/mockups/YouTube_Page_Mockup_DeadstockTapes.png)
   * [`assets/mockups/YouTube_Page_Mockup_UnairedCaseFiles.png`](assets/mockups/YouTube_Page_Mockup_UnairedCaseFiles.png)
3. **Rebuild Thumbnails & Channel Page Mockups:**
   ```powershell
   & "C:\Program Files\Python312\python.exe" .\scripts\rebuild_best_practice_thumbs_and_pages.py
   ```
4. **Render / Re-build Launch Wave Videos (`59.94 fps`):**
   ```powershell
   & "C:\Program Files\Python312\python.exe" .\scripts\build_launch_wave1_videos.py
   ```
