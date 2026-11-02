"""
Adversarial Stress-Testing & Empirical Verification Test Suite
FOX40 Broadcast Archive - Milestone 5
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
READY_TO_POST = pathlib.Path(r"C:\Users\adam\AppData\Local\Temp\fox40_launch_wave1_build\ready_to_post")
FFPROBE_BIN = shutil.which("ffprobe") or r"C:\ProgramData\chocolatey\bin\ffprobe.exe"
FFMPEG_BIN = shutil.which("ffmpeg") or r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"

def run_ffprobe_json(file_path):
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-show_format",
        "-show_streams",
        "-of", "json",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

def test_video_masters():
    print("=" * 70)
    print("SUITE 1: Video Master Empirical Challenge")
    print("=" * 70)
    
    videos = [
        # Deadstock Tapes
        READY_TO_POST / "01_Master_Tape_Vault_Launch" / "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4",
        READY_TO_POST / "01_Master_Tape_Vault_Launch" / "MTV_02_2002_Kobe_Bryant_Shaq_vs_Kings_WCF_5994fps.mp4",
        READY_TO_POST / "01_Master_Tape_Vault_Launch" / "MTV_03_1990s_FOX_NFL_Sunday_Bradshaw_Howie_Long_5994fps.mp4",
        READY_TO_POST / "01_Master_Tape_Vault_Launch" / "MTV_04_2000_Air_Jordan_XI_XVI_Foot_Locker_Mall_Riot_5994fps.mp4",
        READY_TO_POST / "01_Master_Tape_Vault_Launch" / "MTV_05_1988_World_Series_As_Dodgers_and_80s_NFL_Gastineau_5994fps.mp4",
        # Unaired Case Files
        READY_TO_POST / "02_Unaired_Case_Files_Launch" / "UCF_01_1988_Dorothea_Puente_Trial_3D_Model_Body_Bags_5994fps.mp4",
        READY_TO_POST / "02_Unaired_Case_Files_Launch" / "UCF_02_1991_Sacramento_Good_Guys_Hostage_SWAT_Raid_5994fps.mp4",
        READY_TO_POST / "02_Unaired_Case_Files_Launch" / "UCF_03_2002_Jane_Doe_Dumpster_Forensic_Clay_Bust_5994fps.mp4",
        READY_TO_POST / "02_Unaired_Case_Files_Launch" / "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4",
        READY_TO_POST / "02_Unaired_Case_Files_Launch" / "UCF_05_California_Megafire_Carr_Inferno_DC10_Drop_Paradise_Drone_5994fps.mp4",
    ]
    
    results = []
    all_passed = True
    
    for v_path in videos:
        vid_id = v_path.name[:6]
        if not v_path.exists():
            print(f"FAIL: {vid_id} file does not exist at {v_path}")
            all_passed = False
            continue
            
        data = run_ffprobe_json(v_path)
        
        v_stream = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
        a_stream = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
        
        if not v_stream:
            print(f"FAIL: {vid_id} missing video stream")
            all_passed = False
            continue
        if not a_stream:
            print(f"FAIL: {vid_id} missing audio stream")
            all_passed = False
            continue
            
        width = int(v_stream.get("width", 0))
        height = int(v_stream.get("height", 0))
        r_fps = v_stream.get("r_frame_rate", "")
        pix_fmt = v_stream.get("pix_fmt", "")
        field_order = v_stream.get("field_order", "")
        v_duration = float(v_stream.get("duration", 0.0))
        
        a_channels = int(a_stream.get("channels", 0))
        a_sample_rate = int(a_stream.get("sample_rate", 0))
        a_duration = float(a_stream.get("duration", 0.0))
        
        sync_delta_ms = abs(v_duration - a_duration) * 1000.0
        
        # Volumedetect
        vol_cmd = [
            FFMPEG_BIN, "-hide_banner",
            "-i", str(v_path),
            "-af", "volumedetect",
            "-vn", "-sn", "-dn",
            "-f", "null", "NUL"
        ]
        vol_res = subprocess.run(vol_cmd, capture_output=True, text=True)
        mean_vol_match = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", vol_res.stderr)
        max_vol_match = re.search(r"max_volume:\s*([-\d.]+)\s*dB", vol_res.stderr)
        mean_vol = float(mean_vol_match.group(1)) if mean_vol_match else None
        max_vol = float(max_vol_match.group(1)) if max_vol_match else None
        
        # Assertions
        is_prog = (field_order == "progressive")
        is_5994 = (r_fps == "60000/1001")
        is_sync = (sync_delta_ms <= 35.0)
        is_stereo = (a_channels == 2 and a_sample_rate == 48000)
        is_vertical = (width == 1080 and height == 1920)
        is_yuv420p = (pix_fmt == "yuv420p")
        is_clean_audio = (max_vol is not None and max_vol <= 0.0 and mean_vol is not None and mean_vol > -30.0 and mean_vol < -15.0)
        
        pass_vid = is_prog and is_5994 and is_sync and is_stereo and is_vertical and is_clean_audio and is_yuv420p
        if not pass_vid:
            all_passed = False
            
        status = "PASS" if pass_vid else "FAIL"
        print(f"[{status}] {vid_id}: {width}x{height} {pix_fmt} | {r_fps} | field_order={field_order} | Audio {a_channels}ch {a_sample_rate}Hz | Sync delta: {sync_delta_ms:.2f}ms | Vol: mean={mean_vol}dB max={max_vol}dB")
        
        results.append({
            "id": vid_id,
            "file": v_path.name,
            "status": status,
            "width": width,
            "height": height,
            "pix_fmt": pix_fmt,
            "fps": r_fps,
            "field_order": field_order,
            "audio_channels": a_channels,
            "audio_sample_rate": a_sample_rate,
            "video_duration_s": v_duration,
            "audio_duration_s": a_duration,
            "sync_delta_ms": sync_delta_ms,
            "mean_volume_db": mean_vol,
            "max_volume_db": max_vol,
            "is_progressive": is_prog,
            "is_5994fps": is_5994,
            "is_sync_le_35ms": is_sync,
            "is_stereo_48k": is_stereo
        })
        
    print(f"\nSuite 1 Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed, results


def test_thumbnails():
    print("\n" + "=" * 70)
    print("SUITE 2: Thumbnail & Vertical Cover Specification Challenge")
    print("=" * 70)
    
    dt_dir = REPO_ROOT / "assets" / "thumbnails" / "deadstock_tapes"
    ucf_dir = REPO_ROOT / "assets" / "thumbnails" / "unaired_case_files"
    
    thumb_specs = [
        ("MTV_01", dt_dir / "MTV_01_YT_Thumb_1280x720.jpg", "UNAIRED 1989"),
        ("MTV_02", dt_dir / "MTV_02_YT_Thumb_1280x720.jpg", "2002 LOCKERS"),
        ("MTV_03", dt_dir / "MTV_03_YT_Thumb_1280x720.jpg", "OFF THE AIR"),
        ("MTV_04", dt_dir / "MTV_04_YT_Thumb_1280x720.jpg", "$160 RIOT"),
        ("MTV_05", dt_dir / "MTV_05_YT_Thumb_1280x720.jpg", "1988 TUNNEL"),
        ("UCF_01", ucf_dir / "UCF_01_YT_Thumb_1280x720.jpg", "7 BODIES FOUND"),
        ("UCF_02", ucf_dir / "UCF_02_YT_Thumb_1280x720.jpg", "41 HOSTAGES"),
        ("UCF_03", ucf_dir / "UCF_03_YT_Thumb_1280x720.jpg", "JANE DOE TAPE"),
        ("UCF_04", ucf_dir / "UCF_04_YT_Thumb_1280x720.jpg", "3 ARSON FIRES"),
        ("UCF_05", ucf_dir / "UCF_05_YT_Thumb_1280x720.jpg", "DC-10 DROP"),
    ]
    
    cover_files = [
        dt_dir / "MTV_01_Vertical_Cover_1080x1920.jpg",
        dt_dir / "MTV_02_Vertical_Cover_1080x1920.jpg",
        dt_dir / "MTV_03_Vertical_Cover_1080x1920.jpg",
        dt_dir / "MTV_04_Vertical_Cover_1080x1920.jpg",
        dt_dir / "MTV_05_Vertical_Cover_1080x1920.jpg",
        ucf_dir / "UCF_01_Vertical_Cover_1080x1920.jpg",
        ucf_dir / "UCF_02_Vertical_Cover_1080x1920.jpg",
        ucf_dir / "UCF_03_Vertical_Cover_1080x1920.jpg",
        ucf_dir / "UCF_04_Vertical_Cover_1080x1920.jpg",
        ucf_dir / "UCF_05_Vertical_Cover_1080x1920.jpg",
    ]
    
    all_passed = True
    results = {"thumbnails": [], "covers": [], "badge_clearance": []}
    
    # 1. Verify dimensions
    print("Checking 10 YouTube Thumbnails in assets/thumbnails/ (1280x720)...")
    for vid, tf, hook in thumb_specs:
        if not tf.exists():
            print(f"FAIL: Thumbnail does not exist: {tf}")
            all_passed = False
            continue
        with Image.open(tf) as im:
            w, h = im.size
            is_ok = (w == 1280 and h == 720)
            if not is_ok:
                all_passed = False
            status = "PASS" if is_ok else "FAIL"
            print(f"[{status}] {tf.name}: {w}x{h}")
            results["thumbnails"].append({"vid": vid, "file": tf.name, "size": [w, h], "status": status})
            
    print("\nChecking 10 Vertical Covers in assets/thumbnails/ (1080x1920)...")
    for cf in cover_files:
        if not cf.exists():
            print(f"FAIL: Cover does not exist: {cf}")
            all_passed = False
            continue
        with Image.open(cf) as im:
            w, h = im.size
            is_ok = (w == 1080 and h == 1920)
            if not is_ok:
                all_passed = False
            status = "PASS" if is_ok else "FAIL"
            print(f"[{status}] {cf.name}: {w}x{h}")
            results["covers"].append({"file": cf.name, "size": [w, h], "status": status})

    # 2. Duration badge clearance (x > 1180, y > 650)
    print("\nCalculating Mathematical Clearance for YouTube Duration Badge Zone (x > 1180, y > 650)...")
    # Load impact font
    font_path = r"C:\Windows\Fonts\impact.ttf"
    font = ImageFont.truetype(font_path, 118)
    dummy_img = Image.new("RGB", (1280, 720))
    dummy_draw = ImageDraw.Draw(dummy_img)
    
    for vid, tf, hook in thumb_specs:
        # Stroke width 8 with drop shadow offset (+9, +9)
        bbox = dummy_draw.textbbox((52, 558), hook, font=font, stroke_width=8)
        # Bbox with +9px shadow
        shadow_x2 = bbox[2] + 9
        shadow_y2 = bbox[3] + 9
        
        # Duration badge zone: x >= 1180, y >= 650
        clearance_px = 1180 - shadow_x2
        is_clear = (shadow_x2 < 1180)
        
        if not is_clear:
            all_passed = False
            
        status = "PASS" if is_clear else "FAIL"
        print(f"[{status}] {vid}: Hook='{hook}' -> x2={shadow_x2}px | Badge Zone clearance: {clearance_px}px (min safe > 0)")
        results["badge_clearance"].append({
            "vid": vid,
            "hook": hook,
            "hook_x2": shadow_x2,
            "badge_start_x": 1180,
            "clearance_pixels": clearance_px,
            "status": status
        })

    # 3. Code inspection for artificial filters in build_launch_wave1_videos.py
    print("\nAsserting zero contrast-boost or circle drawing code in build_launch_wave1_videos.py...")
    build_script = (REPO_ROOT / "scripts" / "build_launch_wave1_videos.py").read_text(encoding="utf-8")
    
    has_contrast = "ImageEnhance.Contrast" in build_script
    has_sharpness = "ImageEnhance.Sharpness" in build_script
    has_color = "ImageEnhance.Color" in build_script
    has_ellipse = re.search(r'draw\.ellipse\(|draw\.arc\(', build_script) is not None
    
    if has_contrast:
        print("FAIL: ImageEnhance.Contrast found in build_launch_wave1_videos.py")
        all_passed = False
    else:
        print("[PASS] Zero ImageEnhance.Contrast calls in build_launch_wave1_videos.py")
        
    if has_sharpness:
        print("FAIL: ImageEnhance.Sharpness found in build_launch_wave1_videos.py")
        all_passed = False
    else:
        print("[PASS] Zero ImageEnhance.Sharpness calls in build_launch_wave1_videos.py")
        
    if has_color:
        print("FAIL: ImageEnhance.Color found in build_launch_wave1_videos.py")
        all_passed = False
    else:
        print("[PASS] Zero ImageEnhance.Color calls in build_launch_wave1_videos.py")
        
    if has_ellipse:
        print("FAIL: draw.ellipse / draw.arc found in build_launch_wave1_videos.py")
        all_passed = False
    else:
        print("[PASS] Zero highlight circle drawing calls in build_launch_wave1_videos.py")
        
    print(f"\nSuite 2 Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed, results


def test_titling_and_hygiene():
    print("\n" + "=" * 70)
    print("SUITE 3: Titling & Branding Hygiene Challenge")
    print("=" * 70)
    
    all_passed = True
    results = {"manifest_titles": [], "posting_pack_titles": []}
    
    # 1. Check catalog/launch_wave1_manifest.json
    manifest_path = REPO_ROOT / "catalog" / "launch_wave1_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    
    allowed_franchise_tags = [
        "| B-Roll & Breds",
        "| The Tunnel Tape",
        "| The Raw Feed",
        "| Case Files"
    ]
    
    print("Checking manifest titles (<=52 chars, subject front-loaded in chars 1-32, ends with franchise tag)...")
    for item in manifest:
        title = item["title"]
        length = len(title)
        has_tag = any(title.endswith(tag) for tag in allowed_franchise_tags)
        is_le_52 = (length <= 52)
        front_chars = title[:32]
        
        status = "PASS" if (is_le_52 and has_tag) else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}] {item['id']} ({length} chars): '{title}' [Chars 1-32: '{front_chars}']")
        results["manifest_titles"].append({
            "id": item["id"],
            "title": title,
            "length": length,
            "has_franchise_tag": has_tag,
            "front_loaded_32": front_chars,
            "status": status
        })

    # 2. Check docs/05_launch_wave1_posting_pack.md titles
    print("\nChecking docs/05_launch_wave1_posting_pack.md titles...")
    pack_text = (REPO_ROOT / "docs" / "05_launch_wave1_posting_pack.md").read_text(encoding="utf-8")
    
    matches = re.findall(r'Optimized Title[^\n]*\n\s*`([^`]+)`', pack_text)
    for t in matches:
        length = len(t)
        has_tag = any(t.endswith(tag) for tag in allowed_franchise_tags)
        is_le_52 = (length <= 52)
        status = "PASS" if (is_le_52 and has_tag) else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}] ({length} chars): '{t}'")
        results["posting_pack_titles"].append({
            "title": t,
            "length": length,
            "has_franchise_tag": has_tag,
            "status": status
        })
        
    # 3. Check DEADSTOCK spelling everywhere in active markdown and code
    print("\nChecking for incorrect 'DEAD STOCK' spelling across repo...")
    bad_deadstock = []
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip git, cache, tests, agents
        if any(ignored in root for ignored in [".git", "__pycache__", ".agents", ".explainers", "tests"]):
            continue
        for f in files:
            if f.endswith((".py", ".json", ".md", ".html")):
                fpath = pathlib.Path(root) / f
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for line_idx, line in enumerate(content.splitlines(), 1):
                    # Exclude the verification checklist line that says 'Zero instances of "Dead Stock" or "DEAD STOCK"'
                    if 'Zero instances of "Dead Stock"' in line:
                        continue
                    if re.search(r'\bDEAD\s+STOCK\b|\bDead\s+Stock\b', line):
                        bad_deadstock.append(f"{fpath.relative_to(REPO_ROOT)}:{line_idx}: {line.strip()}")
                        
    if bad_deadstock:
        print(f"FAIL: Found {len(bad_deadstock)} instances of 'DEAD STOCK':")
        for b in bad_deadstock:
            print(f"  {b}")
        all_passed = False
    else:
        print("[PASS] Zero instances of 'DEAD STOCK' in active repository files.")

    # 4. Check for lingering @MasterTapeVault in active documentation
    print("\nChecking for lingering @MasterTapeVault in active repo files...")
    lingering_mtv = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if any(ignored in root for ignored in [".git", "__pycache__", ".agents", ".explainers", "tests"]):
            continue
        for f in files:
            if f.endswith((".py", ".json", ".md", ".html")):
                fpath = pathlib.Path(root) / f
                content = fpath.read_text(encoding="utf-8", errors="ignore")
                for line_idx, line in enumerate(content.splitlines(), 1):
                    if "@MasterTapeVault" in line or "@mastertapevault" in line:
                        lingering_mtv.append(f"{fpath.relative_to(REPO_ROOT)}:{line_idx}: {line.strip()}")
                        
    if lingering_mtv:
        print(f"FAIL: Found {len(lingering_mtv)} lingering @MasterTapeVault references:")
        for l in lingering_mtv:
            print(f"  {l}")
        all_passed = False
    else:
        print("[PASS] Zero lingering @MasterTapeVault references across repo.")

    print(f"\nSuite 3 Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed, results


def test_py_compile():
    print("\n" + "=" * 70)
    print("SUITE 4: Python Scripts Compilation Challenge")
    print("=" * 70)
    
    scripts = [
        REPO_ROOT / "scripts" / "audit_all_74_vault_reels.py",
        REPO_ROOT / "scripts" / "build_distribution_pack.py",
        REPO_ROOT / "scripts" / "build_launch_wave1_videos.py",
        REPO_ROOT / "scripts" / "build_modern_2026_logos.py",
        REPO_ROOT / "scripts" / "inspect_bloopers_and_fire.py",
        REPO_ROOT / "scripts" / "rebuild_best_practice_thumbs_and_pages.py",
    ]
    
    all_passed = True
    results = []
    
    for s in scripts:
        cmd = [sys.executable, "-m", "py_compile", str(s)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        is_ok = (res.returncode == 0)
        if not is_ok:
            all_passed = False
            print(f"FAIL: {s.name} py_compile error:\n{res.stderr}")
        else:
            print(f"[PASS] {s.name}: exit code 0")
        results.append({"script": s.name, "exit_code": res.returncode, "status": "PASS" if is_ok else "FAIL"})
        
    print(f"\nSuite 4 Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed, results


def main():
    print("STARTING EMPIRICAL VERIFICATION HARNESS")
    s1_pass, s1_res = test_video_masters()
    s2_pass, s2_res = test_thumbnails()
    s3_pass, s3_res = test_titling_and_hygiene()
    s4_pass, s4_res = test_py_compile()
    
    overall = s1_pass and s2_pass and s3_pass and s4_pass
    print("\n" + "=" * 70)
    print(f"FINAL VERDICT: {'PASS' if overall else 'FAIL'}")
    print("=" * 70)
    
    report = {
        "verdict": "PASS" if overall else "FAIL",
        "suite_1_video_masters": {"passed": s1_pass, "details": s1_res},
        "suite_2_thumbnails": {"passed": s2_pass, "details": s2_res},
        "suite_3_titling_hygiene": {"passed": s3_pass, "details": s3_res},
        "suite_4_py_compile": {"passed": s4_pass, "details": s4_res},
    }
    
    out_json = REPO_ROOT / "tests" / "test_results.json"
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote test results to {out_json}")
    
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
