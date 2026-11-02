import concurrent.futures
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import threading
import time
from PIL import Image, ImageDraw

GDRIVE_BIN = shutil.which("gdrive") or "gdrive"
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "catalog" / "master_catalog.json"
OUT_ROOT = pathlib.Path(r"C:\Users\adam\AppData\Local\Temp\fox40_blooper_fire_audit")
CONTACTS_DIR = OUT_ROOT / "contacts_75"
TEMP_DL_DIR = OUT_ROOT / "temp_dl"
RESULTS_JSON = OUT_ROOT / "vault_75_audit_results.json"

CONTACTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DL_DIR.mkdir(parents=True, exist_ok=True)

ALREADY_DONE = {
    "1oZA_GrAS169hvffUYnuQa5ccHLl3frwQ", # BLOOPER1
    "1_lCA24WFToBkaM8OHIC9y_N8_Z1_bRrh", # BLOOPER2
    "1g_nzRBU5rPKW4fxXAq5enn7AcJEcUHud", # BLOOPER3
    "1goIqLQTDKdYu6q1JvvpMj4Zeb_rsiS_M", # Fire_File_Video
    "1NlFJDslffHq8szGOYF-rJKP0awNeGd97", # DJI_0007
    "14ao2wAJtb4NX55FqmNvF8OynO3CDdHET", # DJI_0011
    "11mptqIMSj8KcZdp_3SFtY-2ZtOkaEb8i", # PUENTE1
    "1Uzg5Olv1n36v3GBn5z5-fDuDg5XMTGbv", # CURTIS_DEAN_ANDERSON
    "1-cuJvcvm5Jq5gPFk-thFAHeAD-068cRX", # MARIO_GARCIA
    "1sj9MxQoXPOoAbxK7QTtIg8rPVlCmXrjS", # NOR_CAL_RAPIST
}

lock = threading.Lock()
results = {}
if RESULTS_JSON.exists():
    try:
        results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    except Exception:
        results = {}

def clean_slug(name):
    base = pathlib.Path(name).stem
    base = re.sub(r"[^A-Za-z0-9_-]+", "_", base)
    return base[:65]

def inspect_one(idx, total, asset):
    did = asset["drive_id"]
    dname = asset["drive_name"]
    slug = f"{idx:02d}_{clean_slug(dname)}"
    contact_path = CONTACTS_DIR / f"contact_{slug}.jpg"

    if did in results and contact_path.exists():
        print(f"[{idx}/{total}] SKIP (cached): {dname}", flush=True)
        return results[did]

    work_dir = TEMP_DL_DIR / slug
    work_dir.mkdir(parents=True, exist_ok=True)
    video_path = work_dir / dname

    t0 = time.time()
    try:
        dl_cmd = [GDRIVE_BIN, "readonly", "download", did, "--out", str(video_path)]
        subprocess.run(dl_cmd, check=True, capture_output=True, text=True)

        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_format", "-show_streams",
            "-print_format", "json",
            str(video_path)
        ]
        pres = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        meta = json.loads(pres.stdout)
        fmt = meta.get("format", {})
        dur = float(fmt.get("duration", 0.0) or 0.0)
        tags = fmt.get("tags", {})
        streams = meta.get("streams", [])
        v_s = next((s for s in streams if s.get("codec_type") == "video"), {})
        a_s = next((s for s in streams if s.get("codec_type") == "audio"), None)

        mean_db = None
        max_db = None
        if a_s and dur > 1.0:
            ss_a = min(5.0, max(0.0, dur * 0.1))
            vol_cmd = [
                "ffmpeg", "-y", "-ss", f"{ss_a:.1f}", "-t", "30",
                "-i", str(video_path),
                "-af", "volumedetect", "-f", "null", "NUL"
            ]
            vres = subprocess.run(vol_cmd, capture_output=True, text=True)
            for line in vres.stderr.splitlines():
                if "mean_volume:" in line:
                    mean_db = line.split("mean_volume:")[-1].strip()
                elif "max_volume:" in line:
                    max_db = line.split("max_volume:")[-1].strip()

        # Extract 12 frames (4x3 grid of 480x270 tiles = 1920x810 + 50px header = 1920x860)
        num_frames = 12
        extracted = []
        for i in range(num_frames):
            ts = max(0.5, min(max(0.5, dur - 0.5), (dur * (i + 0.5)) / num_frames)) if dur > 1.0 else 0.0
            f_jpg = work_dir / f"f_{i:02d}.jpg"
            ff_cmd = [
                "ffmpeg", "-y", "-ss", f"{ts:.2f}",
                "-i", str(video_path),
                "-vf", "bwdif=mode=0:parity=-1:deint=0,scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2",
                "-frames:v", "1", "-q:v", "3",
                str(f_jpg)
            ]
            subprocess.run(ff_cmd, capture_output=True)
            if f_jpg.exists():
                extracted.append((ts, f_jpg))

        if extracted:
            grid = Image.new("RGB", (480 * 4, 270 * 3 + 50), (18, 18, 22))
            draw = ImageDraw.Draw(grid)
            v_info = f"{v_s.get('codec_name','?')} {v_s.get('width','?')}x{v_s.get('height','?')} @ {v_s.get('r_frame_rate','?')} ({v_s.get('field_order','prog')})"
            a_info = f"{a_s.get('codec_name')} {a_s.get('channels')}ch (mean {mean_db}, max {max_db})" if a_s else "SILENT (No Audio)"
            c_time = tags.get("creation_time", "unknown-date")[:19]
            loc = tags.get("location", "")
            header_txt = f"[{idx:02d}/{total}] {dname} | {dur/60:.1f}m ({dur:.0f}s) | {asset['size_display']} | {v_info} | Audio: {a_info} | TagDate: {c_time} {loc}"
            draw.text((12, 16), header_txt, fill=(255, 235, 100))

            for f_i, (ts, jpg_p) in enumerate(extracted[:12]):
                r = f_i // 4
                c = f_i % 4
                x0 = c * 480
                y0 = 50 + r * 270
                with Image.open(jpg_p) as im:
                    grid.paste(im, (x0, y0))
                m_s = f"{int(ts//60):02d}:{int(ts%60):02d}"
                draw.rectangle([x0 + 6, y0 + 6, x0 + 96, y0 + 28], fill=(0, 0, 0))
                draw.text((x0 + 10, y0 + 9), f"#{f_i+1} {m_s}", fill=(255, 230, 0))
            grid.save(contact_path, quality=86)

        rec = {
            "index": idx,
            "drive_id": did,
            "drive_name": dname,
            "parent_folder": asset["parent_folder"],
            "size_display": asset["size_display"],
            "size_bytes": asset["size_bytes"],
            "duration_sec": round(dur, 2),
            "duration_min": round(dur / 60.0, 2),
            "video_codec": v_s.get("codec_name"),
            "codec_tag": v_s.get("codec_tag_string"),
            "width": v_s.get("width"),
            "height": v_s.get("height"),
            "fps": v_s.get("r_frame_rate"),
            "field_order": v_s.get("field_order"),
            "audio_codec": a_s.get("codec_name") if a_s else None,
            "audio_channels": a_s.get("channels") if a_s else 0,
            "mean_volume": mean_db,
            "max_volume": max_db,
            "creation_time": tags.get("creation_time"),
            "location": tags.get("location"),
            "contact_sheet": str(contact_path),
            "elapsed_sec": round(time.time() - t0, 1),
        }
        with lock:
            results[did] = rec
            RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

        print(f"[{idx:02d}/{total}] OK ({rec['elapsed_sec']}s): {dname} -> {dur/60:.1f}m, {v_s.get('width')}x{v_s.get('height')}, audio={mean_db}/{max_db}", flush=True)
        return rec
    except Exception as e:
        print(f"[{idx:02d}/{total}] ERROR on {dname}: {e}", flush=True)
        return None
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

def main():
    assets = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    videos = [a for a in assets if a["drive_name"].lower().endswith((".mov", ".mp4", ".mxf", ".mpg", ".avi"))]
    target_pool = [
        a for a in videos
        if a["drive_name"].startswith(("FOR_AMY", "FOR_KATIE", "Old_desktop_stuff__DJI"))
        or a["parent_folder"] == "06_Videos_Bloopers_and_Specials"
    ]
    seen = set()
    todo = []
    for a in target_pool:
        did = a["drive_id"]
        dn = a["drive_name"]
        if did in seen or did in ALREADY_DONE or "Untitled_" in dn:
            continue
        seen.add(did)
        todo.append(a)

    # Sort by size ascending so fast/medium files finish rapidly first, followed by 2-4GB files
    todo.sort(key=lambda x: x["size_bytes"])
    total = len(todo)
    print(f"Starting parallel visual & audio audit of {total} reels ({sum(x['size_bytes'] for x in todo)/1e9:.2f} GB)...", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(inspect_one, i + 1, total, a) for i, a in enumerate(todo)]
        concurrent.futures.wait(futs)

    print(f"\nALL DONE! Completed {len(results)} / {total} reels. Results saved to {RESULTS_JSON}", flush=True)

if __name__ == "__main__":
    main()
