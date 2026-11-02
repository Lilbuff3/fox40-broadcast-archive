import os
import subprocess
import sys
import json
from pathlib import Path

import shutil

GDRIVE_CMD = shutil.which("gdrive") or "gdrive"
STAGING_DIR = Path(r"C:\Users\adam\AppData\Local\Temp\fox40_wave1_staging")
RAW_DIR = STAGING_DIR / "raw"
OUT_DIR = STAGING_DIR / "ready_mp4"
DRIVE_DEST_FOLDER = "1n0tFUP97IYcJkpYrFCSkQDTO-9YrHq00"  # 08_Ready_For_YouTube_and_TikTok

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Curated Wave 1 Reels covering NBA/Jordan, 2000s Kings, 49ers, 1980s/90s Retro TV, and True Crime
WAVE1_JOBS = [
    {
        "slug": "01_1989_Michael_Jordan_vs_Kings",
        "drive_id": "1bBHLUU0QnRcwxtIFvFLHEJr58zW-0HF4",
        "raw_name": "FOR_AMY_2__Untitled_03_6039347.mov",
        "outputs": [
            {
                "name": "01A_1989_Michael_Jordan_Courtside_Only_16x9_Master_60fps.mp4",
                "ss": "52.5",
                "t": "36.6",
                "mode": "16x9_master",
            },
            {
                "name": "01B_1989_Michael_Jordan_Full_Reel_Motta_and_MJ_16x9_Master_60fps.mp4",
                "ss": "0",
                "t": "89.1",
                "mode": "16x9_master",
            },
            {
                "name": "01C_1989_Michael_Jordan_Courtside_B2B_Screener_Watermarked_60fps.mp4",
                "ss": "52.5",
                "t": "36.6",
                "mode": "16x9_screener",
                "label": "REEL ID: UNTITLED_03 (NOV 14 1989 BULLS AT KINGS) | ARCHIVAL SCREENER",
            },
            {
                "name": "01D_1989_Michael_Jordan_Courtside_9x16_Shorts_Reels_60fps.mp4",
                "ss": "52.5",
                "t": "36.6",
                "mode": "9x16_vertical",
            },
            {
                "name": "01E_1989_Michael_Jordan_and_Motta_65s_TikTok_CreatorRewards_9x16_60fps.mp4",
                "ss": "24.0",
                "t": "65.0",
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "02_2004_Kings_Bibby_PowderBlue_vs_Pistons",
        "drive_id": "1rdjYjWSegAETU0IqAwxMQ18ZVC3pGxXq",
        "raw_name": "FOR_KATIE__Untitled_05_8082294.mov",
        "outputs": [
            {
                "name": "02A_2004_Kings_Bibby_vs_Pistons_16x9_Master_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "16x9_master",
            },
            {
                "name": "02B_2004_Kings_Bibby_vs_Pistons_B2B_Screener_Watermarked_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "16x9_screener",
                "label": "REEL ID: KATIE_05 (2004-05 KINGS ROYALS THROWBACKS VS PISTONS) | SCREENER",
            },
            {
                "name": "02C_2004_Kings_Bibby_vs_Pistons_9x16_Vertical_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "03_2000s_Kings_vs_76ers_Allen_Iverson",
        "drive_id": "1w_bKc1LgWf49Of5teVCRpS2SJ4BK_rMD",
        "raw_name": "FOR_KATIE__Untitled_02_8082282.mov",
        "outputs": [
            {
                "name": "03A_2000s_Kings_vs_76ers_Iverson_16x9_Master_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "16x9_master",
            },
            {
                "name": "03B_2000s_Kings_vs_76ers_Iverson_9x16_Vertical_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "04_49ers_Coach_Steve_Mariucci",
        "drive_id": "1wJBQ1XI-shRLHTajO4TjHDeyc8XgWNCy",
        "raw_name": "FOR_KATIE__Untitled_08_7759698.mov",
        "outputs": [
            {
                "name": "04A_49ers_Steve_Mariucci_Press_Conf_16x9_Master_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "16x9_master",
            },
            {
                "name": "04B_49ers_Steve_Mariucci_Press_Conf_9x16_Vertical_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "05_1980s_KTXL_10_OClock_News_Promo",
        "drive_id": "1WGIIedHkwk0hdvPvj6vInz0NEg_zNPY4",
        "raw_name": "FOR_AMY_2__Untitled_01_6771327.mov",
        "outputs": [
            {
                "name": "05A_1980s_KTXL_10_OClock_News_Promo_16x9_Master_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "16x9_master",
            },
            {
                "name": "05B_1980s_KTXL_10_OClock_News_Promo_9x16_Vertical_60fps.mp4",
                "ss": None,
                "t": None,
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "06_1990s_FOX40_Kids_Club_Promo",
        "drive_id": "1Q2KI8PaeHG_rRbSXcJvsoF-AtaRQ4Ywu",
        "raw_name": "FOR_KATIE__FOX_KIDS_CLUB_7384004.mov",
        "outputs": [
            {
                "name": "06A_1990s_FOX40_Kids_Club_Promo_16x9_Master_60fps.mp4",
                "ss": None,
                "t": "90",
                "mode": "16x9_master",
            },
            {
                "name": "06B_1990s_FOX40_Kids_Club_Promo_9x16_Vertical_60fps.mp4",
                "ss": None,
                "t": "65",
                "mode": "9x16_vertical",
            },
        ],
    },
    {
        "slug": "07_1988_Dorothea_Puente_Excavation_Reel1",
        "drive_id": "11mptqIMSj8KcZdp_3SFtY-2ZtOkaEb8i",
        "raw_name": "FOR_AMY_2__PUENTE1_7228678.mov",
        "outputs": [
            {
                "name": "07A_1988_Dorothea_Puente_Excavation_Reel1_16x9_Master_60fps.mp4",
                "ss": "0",
                "t": "120",
                "mode": "16x9_master",
            },
            {
                "name": "07B_1988_Dorothea_Puente_Excavation_Reel1_B2B_Screener_Watermarked_60fps.mp4",
                "ss": "0",
                "t": "120",
                "mode": "16x9_screener",
                "label": "REEL ID: PUENTE_1 (NOV 1988 1426 F ST EXCAVATION) | ARCHIVAL SCREENER",
            },
            {
                "name": "07C_1988_Dorothea_Puente_Excavation_65s_TikTok_9x16_Vertical_60fps.mp4",
                "ss": "10",
                "t": "65",
                "mode": "9x16_vertical",
            },
        ],
    },
]


def run_cmd(cmd, desc):
    print(f"[*] {desc}...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Error in {desc}:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
        return False, res.stdout + "\n" + res.stderr
    return True, res.stdout


def download_from_drive(drive_id, dest_path):
    if dest_path.exists() and dest_path.stat().st_size > 1000000:
        print(f"[+] Using cached {dest_path.name} ({dest_path.stat().st_size / 1e6:.1f} MB)")
        return True
    cmd = [GDRIVE_CMD, "readonly", "download", drive_id, "--out", str(dest_path)]
    ok, _ = run_cmd(cmd, f"Downloading {dest_path.name} ({drive_id})")
    return ok


def build_filter(mode, label=None):
    if mode == "16x9_master":
        return (
            "bwdif=mode=send_field:parity=auto:deint=all,"
            "split=2[bg][fg];"
            "[bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=20:5,eq=brightness=-0.15[bgblur];"
            "[fg]scale=1440:1080:flags=lanczos,setsar=1[fgscale];"
            "[bgblur][fgscale]overlay=(W-w)/2:(H-h)/2,format=yuv420p"
        )
    elif mode == "16x9_screener":
        safe_label = (label or "CALIFORNIA BROADCAST VAULT | ARCHIVAL SCREENER").replace(":", r"\:")
        return (
            "bwdif=mode=send_field:parity=auto:deint=all,"
            "split=2[bg][fg];"
            "[bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=20:5,eq=brightness=-0.15[bgblur];"
            "[fg]scale=1440:1080:flags=lanczos,setsar=1[fgscale];"
            "[bgblur][fgscale]overlay=(W-w)/2:(H-h)/2,"
            "drawbox=x=0:y=ih-85:w=iw:h=65:color=black@0.65:t=fill,"
            f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{safe_label}':fontcolor=white@0.90:fontsize=26:x=(w-text_w)/2:y=h-65,"
            "format=yuv420p"
        )
    elif mode == "9x16_vertical":
        return (
            "bwdif=mode=send_field:parity=auto:deint=all,"
            "split=2[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.18[bgblur];"
            "[fg]scale=1080:810:flags=lanczos,setsar=1[fgscale];"
            "[bgblur][fgscale]overlay=(W-w)/2:(H-h)/2,format=yuv420p"
        )
    raise ValueError(f"Unknown mode: {mode}")


def convert_clip(src_path, out_spec):
    out_path = OUT_DIR / out_spec["name"]
    if out_path.exists() and out_path.stat().st_size > 100000:
        print(f"[+] Already converted: {out_path.name}")
        return out_path

    vf = build_filter(out_spec["mode"], out_spec.get("label"))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    if out_spec.get("ss"):
        cmd.extend(["-ss", str(out_spec["ss"])])
    cmd.extend(["-i", str(src_path)])
    if out_spec.get("t"):
        cmd.extend(["-t", str(out_spec["t"])])

    cmd.extend([
        "-vf", vf,
        "-r", "60000/1001",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ac", "2",
        "-movflags", "+faststart",
        str(out_path),
    ])
    ok, _ = run_cmd(cmd, f"Encoding {out_path.name}")
    return out_path if ok else None


def verify_mp4(mp4_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,codec_name,duration",
        "-of", "json",
        str(mp4_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        info = json.loads(res.stdout)
        streams = info.get("streams", [{}])
        if streams:
            s = streams[0]
            print(f"    Verified {mp4_path.name}: {s.get('width')}x{s.get('height')} @ {s.get('r_frame_rate')} fps ({s.get('codec_name')}, {float(s.get('duration', 0)):.1f}s, {mp4_path.stat().st_size / 1e6:.2f} MB)")
            return True
    return False


def upload_to_drive(mp4_path):
    cmd = [GDRIVE_CMD, "mutate", "upload", str(mp4_path), "--parent", DRIVE_DEST_FOLDER]
    ok, out = run_cmd(cmd, f"Uploading {mp4_path.name} to 08_Ready_For_YouTube_and_TikTok")
    if ok:
        print(f"    {out.strip()}")
    return ok


def main():
    # Ensure gdrive is initialized
    subprocess.run([GDRIVE_CMD, "--version"], capture_output=True)

    generated_files = []
    for job in WAVE1_JOBS:
        raw_path = RAW_DIR / job["raw_name"]
        if not download_from_drive(job["drive_id"], raw_path):
            print(f"[!] Skipping job {job['slug']} due to download failure")
            continue

        for out_spec in job["outputs"]:
            mp4_path = convert_clip(raw_path, out_spec)
            if mp4_path and verify_mp4(mp4_path):
                upload_to_drive(mp4_path)
                generated_files.append(mp4_path.name)

        # Remove large raw file after converting its outputs to keep disk clean
        try:
            if raw_path.exists() and raw_path.stat().st_size > 200_000_000:
                raw_path.unlink()
                print(f"[*] Cleaned up temporary raw file {raw_path.name}")
        except Exception as e:
            print(f"[!] Warning cleaning up {raw_path.name}: {e}")

    print(f"\n=== COMPLETED WAVE 1 CONVERSION & UPLOAD ({len(generated_files)} files) ===")
    for fn in generated_files:
        print(f" - {fn}")


if __name__ == "__main__":
    main()
