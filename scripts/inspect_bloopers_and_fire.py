import json
import os
import pathlib
import shutil
import subprocess
import sys
from PIL import Image, ImageDraw

GDRIVE_BIN = shutil.which("gdrive") or "gdrive"
OUT_ROOT = pathlib.Path(r"C:\Users\adam\AppData\Local\Temp\fox40_blooper_fire_audit")
OUT_ROOT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("Fire_File_Video", "1goIqLQTDKdYu6q1JvvpMj4Zeb_rsiS_M", "FOR_KATIE__Fire_File_Video_7094994.mov"),
    ("Glass_Fire_Aerials", "1HplKLx0XdLMO8KE23yJ8Hk3aTP7Ga_iH", "NEWS_MEDIA__MORE_NAPA_COUNTY___GLASS_FIRE__AERIALS___NAPAVALLEYGLASSFIRE0927_11195751.mov"),
    ("DJI_0011_Drone", "14ao2wAJtb4NX55FqmNvF8OynO3CDdHET", "Old_desktop_stuff__DJI_0011_9223094.MOV"),
    ("DJI_0007_Drone", "1NlFJDslffHq8szGOYF-rJKP0awNeGd97", "Old_desktop_stuff__DJI_0007_9223095.MOV"),
    ("BLOOPER1", "1oZA_GrAS169hvffUYnuQa5ccHLl3frwQ", "FOR_KATIE__BLOOPER1_7290786.mov"),
]

def inspect_target(slug, file_id, expected_name):
    print(f"\n================ {slug} ({file_id}) ================", flush=True)
    sub_dir = OUT_ROOT / slug
    sub_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = sub_dir / expected_name
    if not (video_path.exists() and video_path.stat().st_size > 1_000_000):
        dl_cmd = [GDRIVE_BIN, "readonly", "download", file_id, "--out", str(video_path)]
        print(f"Downloading {expected_name}...", flush=True)
        subprocess.run(dl_cmd, check=True)
    
    # ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-show_format", "-show_streams",
        "-print_format", "json",
        str(video_path)
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    meta = json.loads(res.stdout)
    (sub_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    
    fmt = meta.get("format", {})
    dur = float(fmt.get("duration", 0))
    tags = fmt.get("tags", {})
    streams = meta.get("streams", [])
    v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    
    print(f"Duration: {dur:.2f}s ({dur/60:.2f} min) | Size: { int(fmt.get('size',0))/(1024*1024):.1f} MB", flush=True)
    print(f"Video: {v_stream.get('codec_name')} ({v_stream.get('codec_tag_string')}) {v_stream.get('width')}x{v_stream.get('height')} @ {v_stream.get('r_frame_rate')} fps | field_order={v_stream.get('field_order')}", flush=True)
    print(f"Format Tags: {tags}", flush=True)
    if a_stream:
        print(f"Audio: {a_stream.get('codec_name')} {a_stream.get('channels')}ch @ {a_stream.get('sample_rate')}Hz", flush=True)
        vol_cmd = [
            "ffmpeg", "-y", "-ss", "10", "-t", "60", "-i", str(video_path),
            "-af", "volumedetect", "-f", "null", "NUL"
        ]
        vres = subprocess.run(vol_cmd, capture_output=True, text=True)
        for line in vres.stderr.splitlines():
            if "mean_volume" in line or "max_volume" in line:
                print("  " + line.strip(), flush=True)
    else:
        print("Audio: NONE (Silent video)", flush=True)
        
    # Extract 12 evenly spaced frames
    num_frames = 12
    extracted = []
    for i in range(num_frames):
        ts = max(1.0, min(dur - 1.0, (dur * (i + 0.5)) / num_frames))
        out_jpg = sub_dir / f"frame_{i+1:02d}_{int(ts):04d}s.jpg"
        ff_cmd = [
            "ffmpeg", "-y", "-ss", f"{ts:.2f}",
            "-i", str(video_path),
            "-vf", "bwdif=mode=0:parity=-1:deint=0,scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2",
            "-frames:v", "1", "-q:v", "2",
            str(out_jpg)
        ]
        subprocess.run(ff_cmd, capture_output=True)
        if out_jpg.exists():
            extracted.append((ts, out_jpg))
            
    # Build 4x3 contact sheet
    if extracted:
        grid = Image.new("RGB", (640 * 4, 360 * 3), (15, 15, 15))
        draw = ImageDraw.Draw(grid)
        for idx, (ts, jpg_p) in enumerate(extracted[:12]):
            r = idx // 4
            c = idx % 4
            with Image.open(jpg_p) as im:
                grid.paste(im, (c * 640, r * 360))
            m_s = f"{int(ts//60):02d}:{int(ts%60):02d}"
            draw.rectangle([c * 640 + 8, r * 360 + 8, c * 640 + 130, r * 360 + 36], fill=(0, 0, 0))
            draw.text((c * 640 + 14, r * 360 + 12), f"#{idx+1} {m_s}", fill=(255, 230, 0))
        contact_path = OUT_ROOT / f"contact_{slug}.jpg"
        grid.save(contact_path, quality=88)
        print(f"Saved contact sheet: {contact_path}", flush=True)
        
    # Delete temporary large .mov to save disk space
    try:
        video_path.unlink()
        print(f"Cleaned up temporary video: {video_path.name}", flush=True)
    except Exception as e:
        print(f"Warning cleaning {video_path}: {e}", flush=True)

if __name__ == "__main__":
    for slug, fid, name in TARGETS:
        inspect_target(slug, fid, name)
