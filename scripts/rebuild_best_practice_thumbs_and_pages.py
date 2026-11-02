import pathlib
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_ROOT = pathlib.Path(r"C:\Users\adam\AppData\Local\Temp\fox40_launch_wave1_build\ready_to_post")
MTV_DIR = OUT_ROOT / "01_Master_Tape_Vault_Launch"
UCF_DIR = OUT_ROOT / "02_Unaired_Case_Files_Launch"
ART_DIR = REPO_ROOT / "assets" / "branding"
MOCKUP_DIR = REPO_ROOT / "assets" / "mockups"
THUMB_DT_DIR = REPO_ROOT / "assets" / "thumbnails" / "deadstock_tapes"
THUMB_UCF_DIR = REPO_ROOT / "assets" / "thumbnails" / "unaired_case_files"

for _d in (ART_DIR, MOCKUP_DIR, THUMB_DT_DIR, THUMB_UCF_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def get_font(name, size):
    paths = {
        "impact": r"C:\Windows\Fonts\impact.ttf",
        "black": r"C:\Windows\Fonts\ariblk.ttf",
        "bold": r"C:\Windows\Fonts\arialbd.ttf",
        "regular": r"C:\Windows\Fonts\arial.ttf",
        "mono": r"C:\Windows\Fonts\consolab.ttf",
        "lucida": r"C:\Windows\Fonts\lucon.ttf",
    }
    p = paths.get(name, paths["bold"])
    if not pathlib.Path(p).exists():
        p = paths["bold"]
    return ImageFont.truetype(p, size)


def extract_natural_4x3_frame(mp4_path, ts_sec):
    """
    Extracts the 100% authentic, native-gamma 4:3 broadcast frame (1080x810)
    from our 59.94fps master MP4 at ts_sec with ZERO artificial contrast/skin-smoothing.
    """
    ffmpeg_bin = shutil.which("ffmpeg") or r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
    tmp_jpg = OUT_ROOT / f"_tmp_nat43_{mp4_path.stem}_{ts_sec:.2f}.jpg"
    cmd = [
        ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ts_sec:.2f}", "-i", str(mp4_path),
        "-vf", "crop=1080:810:0:420",
        "-frames:v", "1", "-q:v", "2",
        str(tmp_jpg),
    ]
    subprocess.run(cmd, check=True)
    im = Image.open(tmp_jpg).convert("RGB")
    tmp_jpg.unlink(missing_ok=True)
    return im


def extract_natural_full_frame_16x9(mp4_path, ts_sec, focus_y=0.38):
    """
    Extracts a single 100% authentic, native-gamma 4:3 broadcast still (1080x810)
    from our 59.94fps master MP4 at ts_sec, and crops cleanly to 16:9 (1280x720)
    with ZERO artificial contrast/saturation/skin-smoothing filters.
    """
    im = extract_natural_4x3_frame(mp4_path, ts_sec)
    src_w, src_h = im.size
    target_h = 608
    y0 = int((src_h - target_h) * focus_y)
    y0 = max(0, min(src_h - target_h, y0))
    cropped = im.crop((0, y0, src_w, y0 + target_h))
    return cropped.resize((1280, 720), Image.Resampling.LANCZOS)


def apply_vcr_osd_and_corner_hook(canvas, tc_str, hook_text, hook_rgb=(255, 228, 0), sub_mode="PLAY"):
    """
    Applies the authentic 90s Betacam SP / VCR On-Screen Display (OSD) graphics:
    - Top-left: 'PLAY ▶' + valid SMPTE 'TC ...' in crisp white VCR monospace font with hard black OSD shadow
      plus a smooth 2D top-left corner cushion for 100% contrast over bright backgrounds.
    - Bottom-left: 2-3 word max condensed block hook ('UNAIRED 1989', '$160 RIOT', 'OFF THE AIR')
      in classic broadcast yellow (#FFE400) with hard black stroke & drop shadow.
    - Zero split-screen lines, zero face boxes, and 100% unobstructed subject & bottom-right corner.
    """
    W, H = canvas.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Smooth 2D top-left corner cushion for OSD contrast on bright frames (UCF_01, UCF_03)
    for y in range(235):
        ty = 1.0 - (y / 235.0)
        for x in range(600):
            tx = 1.0 - (x / 600.0)
            a = int(158 * ((tx * ty) ** 1.35))
            if a > 0:
                odraw.point((x, y), fill=(0, 0, 0, a))

    # Full-width smooth bottom gradient (only bottom 215px)
    for y in range(505, H):
        ty = (y - 505) / (H - 505)
        alpha = int(160 * (ty ** 1.45))
        odraw.line([(0, y), (W, y)], fill=(4, 6, 8, alpha))

    base = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    # 1. Top-Left VCR / Betacam OSD ('PLAY ▶' + 'TC ...')
    f_osd = get_font("lucida", 44)
    osd_x, osd_y = 52, 42

    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2), (0, 3), (3, 0)]:
        draw.text((osd_x + dx, osd_y + dy), sub_mode, fill=(0, 0, 0, 245), font=f_osd)
    draw.text((osd_x, osd_y), sub_mode, fill=(248, 248, 248, 255), font=f_osd)

    bbox_play = draw.textbbox((osd_x, osd_y), sub_mode, font=f_osd)
    tri_x = bbox_play[2] + 22
    tri_y = osd_y + 6
    tri_pts_shadow = [(tri_x + 4, tri_y + 4), (tri_x + 4, tri_y + 36), (tri_x + 32, tri_y + 20)]
    tri_pts = [(tri_x, tri_y), (tri_x, tri_y + 32), (tri_x + 28, tri_y + 16)]
    draw.polygon(tri_pts_shadow, fill=(0, 0, 0, 245))
    draw.polygon(tri_pts, fill=(248, 248, 248, 255))

    tc_y = osd_y + 56
    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2), (0, 3), (3, 0)]:
        draw.text((osd_x + dx, tc_y + dy), tc_str, fill=(0, 0, 0, 245), font=f_osd)
    draw.text((osd_x, tc_y), tc_str, fill=(248, 248, 248, 255), font=f_osd)

    # 2. Bottom-Left 2-3 Word Condensed Block Hook ('UNAIRED 1989', '$160 RIOT', etc.)
    f_hook = get_font("impact", 118)
    hx, hy = 52, 558

    draw.text(
        (hx + 9, hy + 9),
        hook_text,
        fill=(0, 0, 0, 255),
        font=f_hook,
        stroke_width=8,
        stroke_fill=(0, 0, 0, 255),
    )
    draw.text(
        (hx, hy),
        hook_text,
        fill=hook_rgb + (255,),
        font=f_hook,
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )

    return base.convert("RGB")


def build_vertical_cover_1080x1920(
    mp4_path,
    ts_sec,
    channel_tag,
    headline,
    sub_meta,
    tc_str,
    hook_text,
    accent_rgb,
    hook_rgb,
    sub_rgb,
):
    """
    Builds a clean 1080x1920 Vertical Cover for YouTube Shorts / TikTok / Reels:
    - ZERO artificial face-tracking boxes or labels over faces/bodies.
    - Fast-blurred darkened archival background canvas (1080x1920).
    - Top archival header block (y=155..395) with spine accent bar, series tag, headline, and tape metadata.
    - Full 4:3 native broadcast frame (1080x810 at y=440..1250) with crisp top-left VCR OSD ('PLAY ▶ / TC ...').
    - Bottom condensed Impact hook ('UNAIRED 1989', '7 BODIES FOUND') in #FFE400 above the Shorts UI zone.
    """
    W, H = 1080, 1920
    frame_4x3 = extract_natural_4x3_frame(mp4_path, ts_sec)

    # Fast downscale-blur-upscale background canvas
    bg_small = frame_4x3.resize((270, 480), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(radius=10))
    bg_full = bg_small.resize((W, H), Image.Resampling.BICUBIC)
    dark_scrim = Image.new("RGBA", (W, H), (8, 10, 14, 210))
    canvas = Image.alpha_composite(bg_full.convert("RGBA"), dark_scrim)
    draw = ImageDraw.Draw(canvas)

    # Top Header Card (y=150..392)
    draw.rounded_rectangle([38, 150, W - 38, 392], radius=12, fill=(10, 12, 16, 232))
    draw.rectangle([38, 150, 52, 392], fill=accent_rgb + (255,))

    f_tag = get_font("bold", 29)
    f_head = get_font("black", 46)
    f_meta = get_font("bold", 25)

    draw.text((76, 174), channel_tag, fill=accent_rgb + (255,), font=f_tag)
    draw.text((76, 226), headline, fill=(248, 248, 248, 255), font=f_head)
    draw.text((76, 326), sub_meta, fill=sub_rgb + (255,), font=f_meta)

    # Center 4:3 Broadcast Master Still (1080x810 at y=430..1240) with top-left VCR OSD
    vy0 = 430
    vy1 = vy0 + 810

    # Add smooth top-left OSD cushion on the 4:3 frame
    frame_rgba = frame_4x3.convert("RGBA")
    f_overlay = Image.new("RGBA", (1080, 810), (0, 0, 0, 0))
    f_odraw = ImageDraw.Draw(f_overlay)
    for y in range(210):
        ty = 1.0 - (y / 210.0)
        for x in range(520):
            tx = 1.0 - (x / 520.0)
            a = int(155 * ((tx * ty) ** 1.35))
            if a > 0:
                f_odraw.point((x, y), fill=(0, 0, 0, a))
    frame_rgba = Image.alpha_composite(frame_rgba, f_overlay)
    f_draw = ImageDraw.Draw(frame_rgba)

    f_osd = get_font("lucida", 38)
    ox, oy = 42, 34
    for dx, dy in [(3, 3), (-2, -2), (2, -2), (-2, 2), (0, 3)]:
        f_draw.text((ox + dx, oy + dy), "PLAY", fill=(0, 0, 0, 245), font=f_osd)
    f_draw.text((ox, oy), "PLAY", fill=(248, 248, 248, 255), font=f_osd)

    bbox_p = f_draw.textbbox((ox, oy), "PLAY", font=f_osd)
    tx_tri = bbox_p[2] + 18
    ty_tri = oy + 5
    f_draw.polygon([(tx_tri + 3, ty_tri + 3), (tx_tri + 3, ty_tri + 31), (tx_tri + 27, ty_tri + 17)], fill=(0, 0, 0, 245))
    f_draw.polygon([(tx_tri, ty_tri), (tx_tri, ty_tri + 28), (tx_tri + 24, ty_tri + 14)], fill=(248, 248, 248, 255))

    tcy = oy + 48
    for dx, dy in [(3, 3), (-2, -2), (2, -2), (-2, 2), (0, 3)]:
        f_draw.text((ox + dx, tcy + dy), tc_str, fill=(0, 0, 0, 245), font=f_osd)
    f_draw.text((ox, tcy), tc_str, fill=(248, 248, 248, 255), font=f_osd)

    canvas.paste(frame_rgba, (0, vy0))
    draw.line([(0, vy0 - 2), (W, vy0 - 2)], fill=accent_rgb + (255,), width=4)
    draw.line([(0, vy1 + 2), (W, vy1 + 2)], fill=accent_rgb + (255,), width=4)

    # Technical Spec Strip directly below 4:3 frame (y=1266..1318)
    draw.rounded_rectangle([38, 1266, W - 38, 1320], radius=8, fill=(8, 10, 12, 230))
    f_spec = get_font("mono", 24)
    draw.text((64, 1279), "59.94 FPS OPTICAL DEINTERLACE   |   ORIGINAL BROADCAST MASTER", fill=accent_rgb + (255,), font=f_spec)

    # Bottom Hook Zone (y=1375..1545) — centered condensed Impact hook in #FFE400
    f_hook = get_font("impact", 112)
    bbox_h = draw.textbbox((0, 0), hook_text, font=f_hook)
    hw = bbox_h[2] - bbox_h[0]
    hx = (W - hw) // 2
    hy = 1385

    draw.text(
        (hx + 8, hy + 8),
        hook_text,
        fill=(0, 0, 0, 255),
        font=f_hook,
        stroke_width=8,
        stroke_fill=(0, 0, 0, 255),
    )
    draw.text(
        (hx, hy),
        hook_text,
        fill=hook_rgb + (255,),
        font=f_hook,
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )

    return canvas.convert("RGB")


def build_all_10_thumbs_and_vertical_covers():
    vcr_yellow = (255, 228, 0)
    evidence_yellow = (255, 220, 0)
    dt_gold = (226, 180, 85)
    dt_teal = (122, 168, 159)
    ucf_crimson = (239, 68, 68)

    items = [
        # ==================== CHANNEL 1: DEADSTOCK TAPES (5 VIDEOS) ====================
        {
            "id": "MTV_01",
            "mp4": MTV_DIR / "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4",
            "yt_ts": 20.5, "yt_fy": 0.25,
            "vc_ts": 22.2,
            "tc": "TC 02:14:19:23",
            "hook": "UNAIRED 1989",
            "hook_rgb": vcr_yellow,
            "ch_tag": "DEADSTOCK TAPES  |  B-ROLL & BREDS",
            "headline": "1989 MICHAEL JORDAN UNCUT",
            "sub_meta": "FEB 1989  •  ARCO ARENA  •  UNCOMPRESSED 2VUY MASTER",
            "accent_rgb": dt_gold,
            "sub_rgb": dt_teal,
            "yt_out": MTV_DIR / "MTV_01_YT_Thumb_1280x720.jpg",
            "vc_out": MTV_DIR / "MTV_01_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "MTV_02",
            "mp4": MTV_DIR / "MTV_02_2002_Kobe_Bryant_Shaq_vs_Kings_WCF_5994fps.mp4",
            "yt_ts": 5.0, "yt_fy": 0.25,
            "vc_ts": 5.0,
            "tc": "TC 05:28:02:08",
            "hook": "2002 LOCKERS",
            "hook_rgb": vcr_yellow,
            "ch_tag": "DEADSTOCK TAPES  |  THE TUNNEL TAPE",
            "headline": "2002 KOBE & SHAQ vs. KINGS",
            "sub_meta": "MAY 2002  •  WESTERN CONF. FINALS  •  BETACAM MASTER",
            "accent_rgb": dt_gold,
            "sub_rgb": dt_teal,
            "yt_out": MTV_DIR / "MTV_02_YT_Thumb_1280x720.jpg",
            "vc_out": MTV_DIR / "MTV_02_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "MTV_03",
            "mp4": MTV_DIR / "MTV_03_1990s_FOX_NFL_Sunday_Bradshaw_Howie_Long_5994fps.mp4",
            "yt_ts": 34.0, "yt_fy": 0.28,
            "vc_ts": 34.0,
            "tc": "TC 11:12:19:04",
            "hook": "OFF THE AIR",
            "hook_rgb": vcr_yellow,
            "ch_tag": "DEADSTOCK TAPES  |  THE RAW FEED",
            "headline": "1990s FOX NFL STUDIO TAPE",
            "sub_meta": "1995 STUDIO MASTER  •  HOWIE LONG & TERRY BRADSHAW",
            "accent_rgb": dt_gold,
            "sub_rgb": dt_teal,
            "yt_out": MTV_DIR / "MTV_03_YT_Thumb_1280x720.jpg",
            "vc_out": MTV_DIR / "MTV_03_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "MTV_04",
            "mp4": MTV_DIR / "MTV_04_2000_Air_Jordan_XI_XVI_Foot_Locker_Mall_Riot_5994fps.mp4",
            "yt_ts": 23.0, "yt_fy": 0.45,
            "vc_ts": 23.0,
            "tc": "TC 12:23:00:11",
            "hook": "$160 RIOT",
            "hook_rgb": vcr_yellow,
            "ch_tag": "DEADSTOCK TAPES  |  B-ROLL & BREDS",
            "headline": "2000 AIR JORDAN 11 STAMPEDE",
            "sub_meta": "DEC 2000  •  FOOT LOCKER MALL RIOT  •  BETACAM SP",
            "accent_rgb": dt_gold,
            "sub_rgb": dt_teal,
            "yt_out": MTV_DIR / "MTV_04_YT_Thumb_1280x720.jpg",
            "vc_out": MTV_DIR / "MTV_04_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "MTV_05",
            "mp4": MTV_DIR / "MTV_05_1988_World_Series_As_Dodgers_and_80s_NFL_Gastineau_5994fps.mp4",
            "yt_ts": 11.0, "yt_fy": 0.38,
            "vc_ts": 11.0,
            "tc": "TC 10:15:19:28",
            "hook": "1988 TUNNEL",
            "hook_rgb": vcr_yellow,
            "ch_tag": "DEADSTOCK TAPES  |  THE TUNNEL TAPE",
            "headline": "1988 WORLD SERIES DUGOUT",
            "sub_meta": "OCT 1988  •  DODGER STADIUM TUNNEL  •  2VUY MASTER",
            "accent_rgb": dt_gold,
            "sub_rgb": dt_teal,
            "yt_out": MTV_DIR / "MTV_05_YT_Thumb_1280x720.jpg",
            "vc_out": MTV_DIR / "MTV_05_Vertical_Cover_1080x1920.jpg",
        },
        # ==================== CHANNEL 2: UNAIRED CASE FILES (5 VIDEOS) ====================
        {
            "id": "UCF_01",
            "mp4": UCF_DIR / "UCF_01_1988_Dorothea_Puente_Trial_3D_Model_Body_Bags_5994fps.mp4",
            "yt_ts": 8.0, "yt_fy": 0.45,
            "vc_ts": 8.0,
            "tc": "TC 11:11:19:07",
            "hook": "7 BODIES FOUND",
            "hook_rgb": evidence_yellow,
            "ch_tag": "UNAIRED CASE FILES  |  CASE FILES",
            "headline": "DOROTHEA PUENTE 1426 F ST DIG",
            "sub_meta": "NOV 1988  •  1426 F STREET EXCAVATION & 3D MODEL",
            "accent_rgb": ucf_crimson,
            "sub_rgb": evidence_yellow,
            "yt_out": UCF_DIR / "UCF_01_YT_Thumb_1280x720.jpg",
            "vc_out": UCF_DIR / "UCF_01_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "UCF_02",
            "mp4": UCF_DIR / "UCF_02_1991_Sacramento_Good_Guys_Hostage_SWAT_Raid_5994fps.mp4",
            "yt_ts": 38.0, "yt_fy": 0.45,
            "vc_ts": 38.0,
            "tc": "TC 04:04:19:21",
            "hook": "41 HOSTAGES",
            "hook_rgb": evidence_yellow,
            "ch_tag": "UNAIRED CASE FILES  |  CASE FILES",
            "headline": "1991 GOOD GUYS HOSTAGE SIEGE",
            "sub_meta": "APR 1991  •  SACRAMENTO SWAT STANDOFF  •  LIVE FEED",
            "accent_rgb": ucf_crimson,
            "sub_rgb": evidence_yellow,
            "yt_out": UCF_DIR / "UCF_02_YT_Thumb_1280x720.jpg",
            "vc_out": UCF_DIR / "UCF_02_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "UCF_03",
            "mp4": UCF_DIR / "UCF_03_2002_Jane_Doe_Dumpster_Forensic_Clay_Bust_5994fps.mp4",
            "yt_ts": 12.0, "yt_fy": 0.42,
            "vc_ts": 12.0,
            "tc": "TC 01:19:02:14",
            "hook": "JANE DOE TAPE",
            "hook_rgb": evidence_yellow,
            "ch_tag": "UNAIRED CASE FILES  |  CASE FILES",
            "headline": "2002 JANE DOE FORENSIC CASE",
            "sub_meta": "2002  •  CORONER RECOVERY & FORENSIC RECONSTRUCTION",
            "accent_rgb": ucf_crimson,
            "sub_rgb": evidence_yellow,
            "yt_out": UCF_DIR / "UCF_03_YT_Thumb_1280x720.jpg",
            "vc_out": UCF_DIR / "UCF_03_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "UCF_04",
            "mp4": UCF_DIR / "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4",
            "yt_ts": 8.5, "yt_fy": 0.42,
            "vc_ts": 8.5,
            "tc": "TC 06:18:19:03",
            "hook": "3 ARSON FIRES",
            "hook_rgb": evidence_yellow,
            "ch_tag": "UNAIRED CASE FILES  |  CASE FILES",
            "headline": "1999 SYNAGOGUE ARSON WAVE",
            "sub_meta": "JUNE 1999  •  ATF & FIRE RESPONSE  •  UNEDITED TAPE",
            "accent_rgb": ucf_crimson,
            "sub_rgb": evidence_yellow,
            "yt_out": UCF_DIR / "UCF_04_YT_Thumb_1280x720.jpg",
            "vc_out": UCF_DIR / "UCF_04_Vertical_Cover_1080x1920.jpg",
        },
        {
            "id": "UCF_05",
            "mp4": UCF_DIR / "UCF_05_California_Megafire_Carr_Inferno_DC10_Drop_Paradise_Drone_5994fps.mp4",
            "yt_ts": 28.5, "yt_fy": 0.48,
            "vc_ts": 28.5,
            "tc": "TC 07:28:18:10",
            "hook": "DC-10 DROP",
            "hook_rgb": evidence_yellow,
            "ch_tag": "UNAIRED CASE FILES  |  CASE FILES",
            "headline": "CALIFORNIA MEGAFIRE VAULT",
            "sub_meta": "CARR FIRESTORM  •  DC-10 DROP  •  2.7K PARADISE DRONE",
            "accent_rgb": ucf_crimson,
            "sub_rgb": evidence_yellow,
            "yt_out": UCF_DIR / "UCF_05_YT_Thumb_1280x720.jpg",
            "vc_out": UCF_DIR / "UCF_05_Vertical_Cover_1080x1920.jpg",
        },
    ]

    for it in items:
        # 1. Horizontal 1280x720 YouTube Thumbnail
        frame_16x9 = extract_natural_full_frame_16x9(it["mp4"], it["yt_ts"], focus_y=it["yt_fy"])
        thumb = apply_vcr_osd_and_corner_hook(frame_16x9, it["tc"], it["hook"], hook_rgb=it["hook_rgb"])
        thumb.save(it["yt_out"], quality=95)

        # 2. Vertical 1080x1920 Cover (Clean 4:3 frame, zero face boxes)
        vc = build_vertical_cover_1080x1920(
            it["mp4"],
            it["vc_ts"],
            it["ch_tag"],
            it["headline"],
            it["sub_meta"],
            it["tc"],
            it["hook"],
            it["accent_rgb"],
            it["hook_rgb"],
            it["sub_rgb"],
        )
        vc.save(it["vc_out"], quality=95)

        dest_dir = THUMB_DT_DIR if it["id"].startswith("MTV_") else THUMB_UCF_DIR
        shutil.copy2(it["yt_out"], dest_dir / it["yt_out"].name)
        shutil.copy2(it["vc_out"], dest_dir / it["vc_out"].name)


def upgrade_channel_logos():
    """
    1. Upgrades Modern2026_UnairedCaseFiles_Logo_V1_Viewfinder.png to combine the iconic
       Redacted 'U' monogram (V2_RedactedU) with architectural viewfinder corner ticks,
       so it reads unmistakably at both 84px desktop and 46px Shorts sizes.
    2. Refines DeadstockTapes_Avatar_MobileZoom_1024x1024.png with a clean circular frame
       mask so the outer half-cropped letters ('DEADSTOCK'/'TAPES') are cleanly framed out.
    """
    # --- 1. Unaired Case Files Combined Viewfinder + Redacted U Logo (1024x1024) ---
    W, H = 1024, 1024
    v2_path = ART_DIR / "Modern2026_UnairedCaseFiles_Logo_V2_RedactedU.png"
    v1_path = ART_DIR / "Modern2026_UnairedCaseFiles_Logo_V1_Viewfinder.png"

    if v2_path.exists():
        with Image.open(v2_path).convert("RGBA") as v2_im:
            bg_px = v2_im.getpixel((0, 0))
            base = Image.new("RGBA", (W, H), bg_px)
            # Scale Redacted U slightly to 820x820 centered so viewfinder corners frame it cleanly
            u_scaled = v2_im.resize((820, 820), Image.Resampling.LANCZOS)
            base.paste(u_scaled, (102, 102))

        draw = ImageDraw.Draw(base)
        bone = (244, 242, 236, 255)
        crimson = (239, 68, 68, 255)

        # Architectural Viewfinder Corner Brackets around the Redacted U
        m = 158
        arm = 112
        thick = 24
        # Top-Left
        draw.rectangle([m, m, m + arm, m + thick], fill=bone)
        draw.rectangle([m, m, m + thick, m + arm], fill=bone)
        # Top-Right
        draw.rectangle([W - m - arm, m, W - m, m + thick], fill=crimson)
        draw.rectangle([W - m - thick, m, W - m, m + arm], fill=crimson)
        # Bottom-Left
        draw.rectangle([m, H - m - thick, m + arm, H - m], fill=bone)
        draw.rectangle([m, H - m - arm, m + thick, H - m], fill=bone)
        # Bottom-Right
        draw.rectangle([W - m - arm, H - m - thick, W - m, H - m], fill=bone)
        draw.rectangle([W - m - thick, H - m - arm, W - m, H - m], fill=bone)

        base.convert("RGB").save(v1_path, quality=95)

    # --- 2. Deadstock Tapes MobileZoom Avatar clean ring mask (zero half-chopped letters) ---
    src_crest = ART_DIR / "DeadstockTapes_Crest_Source_OneWord.jpg"
    av_one = ART_DIR / "DeadstockTapes_Avatar_OneWord_1024x1024.png"
    av_zoom = ART_DIR / "DeadstockTapes_Avatar_MobileZoom_1024x1024.png"

    if src_crest.exists():
        with Image.open(src_crest).convert("RGB") as cim:
            # Slightly boost sharpness for 46px mobile clarity
            cim_crisp = ImageEnhance.Sharpness(cim.resize((1024, 1024), Image.Resampling.LANCZOS)).enhance(1.15)
            cim_crisp.save(av_one, quality=95)

            # For MobileZoom: crop tight on character + sneaker + Betacam, then mask out the outer
            # half-cut letters with a clean dark/teal double-ring border!
            cw, ch = cim.size
            crop_box = (int(cw * 0.11), int(ch * 0.13), int(cw * 0.89), int(ch * 0.91))
            zoomed = cim.crop(crop_box).resize((1024, 1024), Image.Resampling.LANCZOS)

            # Create circular mask that hides the outer half-sliced letter ring outside r=452
            z_canvas = Image.new("RGB", (1024, 1024), (10, 13, 16))
            mask_inner = Image.new("L", (1024, 1024), 0)
            ImageDraw.Draw(mask_inner).ellipse([60, 60, 964, 964], fill=255)
            z_canvas.paste(zoomed, (0, 0), mask_inner)

            z_draw = ImageDraw.Draw(z_canvas)
            z_draw.ellipse([48, 48, 976, 976], outline=(122, 168, 159), width=16)
            z_draw.ellipse([64, 64, 960, 960], outline=(226, 180, 85), width=6)
            z_canvas.save(av_zoom, quality=95)


def build_no_redundancy_banners():
    """
    Builds both 2560x1440 YouTube Banners WITHOUT repeating the circular avatar on the left:
    - Uses a directional horizontal gradient scrim over the archival still (dark behind left text,
      brighter on the right so the 1989 Bulls/Kings arena and ATF crime scene are visibly recognizable).
    - Adds balanced right-side Betacam/U-Matic deck status readouts at both top-right and bottom-right
      inside the viewfinder brackets.
    """
    W, H = 2560, 1440
    TEAL = (122, 168, 159)
    CREAM = (234, 224, 200)
    ORANGE = (223, 108, 57)
    GOLD = (226, 180, 85)
    CRIMSON = (239, 68, 68)

    f_title = get_font("black", 96)
    f_sub = get_font("bold", 31)
    f_osd = get_font("lucida", 26)
    f_tag = get_font("mono", 24)
    f_spec = get_font("mono", 21)

    def make_directional_scrim():
        scrim = Image.new("RGBA", (W, H), (10, 12, 15, 226))
        sdraw = ImageDraw.Draw(scrim)
        for x in range(W):
            # Keep left/far-left dark (alpha ~220) behind text, open up right half (x=1250..2150) to alpha ~155
            if 1150 <= x <= 2250:
                t = 1.0 - abs(x - 1750) / 600.0
                t = max(0.0, min(1.0, t))
                alpha = int(222 - 68 * t)
            else:
                alpha = 222
            sdraw.line([(x, 0), (x, H)], fill=(10, 12, 15, alpha))
        return scrim

    dir_scrim = make_directional_scrim()

    # --- 1. DEADSTOCK TAPES BANNER ---
    court_bg = extract_natural_full_frame_16x9(
        MTV_DIR / "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4", 22.4, focus_y=0.4
    ).resize((2560, 1440), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=4))

    b1 = Image.alpha_composite(court_bg.convert("RGBA"), dir_scrim).convert("RGB")
    d1 = ImageDraw.Draw(b1)

    for y in range(0, H, 6):
        d1.line([(0, y), (W, y)], fill=(8, 10, 13), width=2)

    bx0, by0, bx1, by1 = 440, 582, 2120, 858
    blen = 36
    for cx, cy, sx, sy in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
        d1.line([(cx, cy), (cx + sx * blen, cy)], fill=TEAL, width=4)
        d1.line([(cx, cy), (cx, cy + sy * blen)], fill=TEAL, width=4)

    d1.rectangle([485, 602, 501, 838], fill=TEAL)
    d1.rectangle([509, 602, 519, 838], fill=ORANGE)

    # Top-right VCR OSD readout inside banner
    d1.text((1685, 596), "PLAY     SP 59.94Hz", fill=CREAM, font=f_osd)
    d1.polygon([(1765, 598), (1765, 620), (1785, 609)], fill=CREAM)
    d1.text((1685, 630), "TC 02:14:19:23", fill=TEAL, font=f_osd)

    # Bottom-right deck technical readout to balance composition
    d1.rounded_rectangle([1685, 796, 2088, 836], radius=6, fill=(12, 16, 20))
    d1.text((1702, 804), "2VUY MASTER • BETACAM SP", fill=TEAL, font=f_spec)

    # Top pill badge
    d1.rounded_rectangle([550, 594, 1310, 640], radius=8, fill=ORANGE)
    d1.text((572, 603), "UNCUT 60FPS BROADCAST VAULT  •  1975–2005", fill=(12, 12, 12), font=f_tag)

    # Giant 1-word 'DEADSTOCK TAPES' headline
    d1.text((555, 648), "DEADSTOCK TAPES", fill=(35, 52, 48), font=f_title)
    d1.text((548, 642), "DEADSTOCK TAPES", fill=CREAM, font=f_title, stroke_width=2, stroke_fill=TEAL)

    # Sub-series franchises bar
    d1.text((552, 760), "B-ROLL & BREDS   •   THE TUNNEL TAPE   •   THE RAW FEED", fill=TEAL, font=f_sub)
    d1.text((552, 806), "UNSEEN NBA, NFL & SNEAKER GRAILS PRESERVED FROM ORIGINAL STUDIO REELS", fill=GOLD, font=f_tag)

    b1_path = ART_DIR / "DeadstockTapes_YouTube_Banner.png"
    b1.save(b1_path, quality=95)

    # --- 2. UNAIRED CASE FILES BANNER ---
    crime_bg = extract_natural_full_frame_16x9(
        UCF_DIR / "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4", 24.0, focus_y=0.4
    ).resize((2560, 1440), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=4))
    b2 = Image.alpha_composite(crime_bg.convert("RGBA"), dir_scrim).convert("RGB")
    d2 = ImageDraw.Draw(b2)

    for y in range(0, H, 6):
        d2.line([(0, y), (W, y)], fill=(8, 9, 12), width=2)

    for cx, cy, sx, sy in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
        d2.line([(cx, cy), (cx + sx * blen, cy)], fill=CRIMSON, width=4)
        d2.line([(cx, cy), (cx, cy + sy * blen)], fill=CRIMSON, width=4)

    d2.rectangle([485, 602, 501, 838], fill=CRIMSON)
    d2.rectangle([509, 602, 519, 838], fill=(240, 240, 240))

    d2.text((1685, 596), "REC     EVIDENCE REEL", fill=CRIMSON, font=f_osd)
    d2.ellipse([1747, 600, 1765, 618], fill=CRIMSON)
    d2.text((1685, 630), "TC 11:11:19:07", fill=(220, 220, 220), font=f_osd)

    d2.rounded_rectangle([1685, 796, 2088, 836], radius=6, fill=(16, 12, 14))
    d2.text((1702, 804), "U-MATIC / BETACAM ARCHIVE", fill=(220, 220, 225), font=f_spec)

    d2.rounded_rectangle([550, 594, 1320, 640], radius=8, fill=CRIMSON)
    d2.text((572, 603), "DECLASSIFIED BROADCAST EVIDENCE  •  TRUE 60FPS", fill=(255, 255, 255), font=f_tag)

    d2.text((555, 648), "UNAIRED CASE FILES", fill=(50, 15, 15), font=f_title)
    d2.text((548, 642), "UNAIRED CASE FILES", fill=(245, 245, 247), font=f_title)

    d2.text((552, 760), "TRUE CRIME TRIALS   •   SWAT STANDOFFS   •   COLD CASES   •   MEGAFIRES", fill=(210, 214, 220), font=f_sub)
    d2.text((552, 806), "ORIGINAL UNEDITED CRIME-SCENE, COURTROOM & AERIAL MASTER TAPES", fill=CRIMSON, font=f_tag)

    b2_path = ART_DIR / "Modern2026_UnairedCaseFiles_YouTube_Banner.png"
    b2.save(b2_path, quality=95)
    return b1_path, b2_path


def render_channel_page(
    banner_path,
    avatar_path,
    channel_name,
    handle,
    sub_line,
    bio_line,
    accent_rgb,
    title_rgb,
    thumbs_info,
    vertical_covers_info,
    out_path,
    zoom_avatar_path=None,
):
    PW, PH = 1920, 1380
    page = Image.new("RGB", (PW, PH), (15, 15, 15))
    pdraw = ImageDraw.Draw(page)

    with Image.open(banner_path) as bim:
        b_crop = bim.crop((400, 565, 2160, 875))
        mask_b = Image.new("L", (1760, 310), 0)
        ImageDraw.Draw(mask_b).rounded_rectangle([0, 0, 1759, 309], radius=24, fill=255)
        page.paste(b_crop, (80, 30), mask_b)

    with Image.open(avatar_path) as av_im:
        av_160 = av_im.resize((160, 160), Image.Resampling.LANCZOS)
        mask_av = Image.new("L", (160, 160), 0)
        ImageDraw.Draw(mask_av).ellipse([0, 0, 159, 159], fill=255)
        page.paste(av_160, (110, 370), mask_av)
        pdraw.ellipse([108, 368, 272, 532], outline=accent_rgb, width=3)

    f_ch = get_font("black", 42)
    f_meta = get_font("regular", 22)
    f_btn = get_font("bold", 22)
    f_tab = get_font("bold", 24)
    f_vid_t = get_font("bold", 20)
    f_vid_m = get_font("regular", 18)
    f_dur = get_font("bold", 17)

    pdraw.text((305, 375), channel_name, fill=title_rgb, font=f_ch)
    pdraw.text((305, 432), f"{handle}  •  {sub_line}", fill=accent_rgb, font=f_meta)
    pdraw.text((305, 466), bio_line, fill=(180, 180, 180), font=f_meta)

    pdraw.rounded_rectangle([305, 505, 465, 553], radius=24, fill=title_rgb)
    pdraw.text((335, 517), "Subscribe", fill=(15, 15, 15), font=f_btn)

    tabs = ["Home", "Videos", "Shorts", "Playlists"]
    tx = 110
    for i, tb in enumerate(tabs):
        col = title_rgb if i == 0 else (160, 160, 160)
        pdraw.text((tx, 585), tb, fill=col, font=f_tab)
        if i == 0:
            pdraw.rectangle([tx, 622, tx + 70, 626], fill=accent_rgb)
        tx += 140
    pdraw.line([(80, 627), (1840, 627)], fill=(45, 45, 45), width=2)

    card_w, card_h = 540, 304
    positions = [(80, 660), (650, 660), (1220, 660), (80, 1015), (650, 1015)]

    for idx, (t_path, v_title, v_views, v_dur) in enumerate(thumbs_info):
        px, py = positions[idx]
        with Image.open(t_path) as tim:
            t_resized = tim.resize((card_w, card_h), Image.Resampling.LANCZOS)
            mask_t = Image.new("L", (card_w, card_h), 0)
            ImageDraw.Draw(mask_t).rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=16, fill=255)
            page.paste(t_resized, (px, py), mask_t)
        bx0, by0 = px + card_w - 68, py + card_h - 36
        pdraw.rounded_rectangle([bx0, by0, px + card_w - 10, py + card_h - 10], radius=6, fill=(10, 10, 10))
        pdraw.text((bx0 + 10, by0 + 4), v_dur, fill=(255, 255, 255), font=f_dur)
        pdraw.text((px + 4, py + card_h + 10), v_title, fill=title_rgb, font=f_vid_t)
        pdraw.text((px + 4, py + card_h + 36), f"{v_views}  •  Uncut 60fps Master", fill=(160, 160, 160), font=f_vid_m)

    # 6th slot: Upgraded Shorts Vertical Covers + Avatar Preview Card
    cx, cy = 1220, 1015
    pdraw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill=(20, 24, 28), outline=accent_rgb, width=3)
    pdraw.text((cx + 20, cy + 14), "SHORTS 9:16 COVERS + AVATAR SCALE:", fill=title_rgb, font=f_vid_t)

    # Render 3 mini 9:16 Vertical Covers on the left side of the 6th card (zero face boxes!)
    vc_w, vc_h = 108, 192
    for vi, vc_p in enumerate(vertical_covers_info[:3]):
        vx = cx + 20 + vi * 118
        vy = cy + 48
        with Image.open(vc_p) as vim:
            v_res = vim.resize((vc_w, vc_h), Image.Resampling.LANCZOS)
            m_v = Image.new("L", (vc_w, vc_h), 0)
            ImageDraw.Draw(m_v).rounded_rectangle([0, 0, vc_w - 1, vc_h - 1], radius=8, fill=255)
            page.paste(v_res, (vx, vy), m_v)
            pdraw.rounded_rectangle([vx, vy, vx + vc_w, vy + vc_h], radius=8, outline=accent_rgb, width=1)

    # Right column of 6th card: Avatar at 84px & 46px Shorts scale
    ax = cx + 378
    pdraw.text((ax, cy + 48), "Avatar @84/46px", fill=accent_rgb, font=f_vid_m)
    with Image.open(avatar_path) as av_full:
        for sz, ox, oy in [(84, ax + 4, cy + 80), (46, ax + 98, cy + 98)]:
            a_sz = av_full.resize((sz, sz), Image.Resampling.LANCZOS)
            m_sz = Image.new("L", (sz, sz), 0)
            ImageDraw.Draw(m_sz).ellipse([0, 0, sz - 1, sz - 1], fill=255)
            page.paste(a_sz, (ox, oy), m_sz)
            pdraw.ellipse([ox - 2, oy - 2, ox + sz + 2, oy + sz + 2], outline=accent_rgb, width=2)

    if zoom_avatar_path and zoom_avatar_path.exists():
        with Image.open(zoom_avatar_path) as av_zm:
            for sz, ox, oy in [(56, ax + 12, cy + 178), (42, ax + 82, cy + 185)]:
                a_sz = av_zm.resize((sz, sz), Image.Resampling.LANCZOS)
                m_sz = Image.new("L", (sz, sz), 0)
                ImageDraw.Draw(m_sz).ellipse([0, 0, sz - 1, sz - 1], fill=255)
                page.paste(a_sz, (ox, oy), m_sz)
                pdraw.ellipse([ox - 2, oy - 2, ox + sz + 2, oy + sz + 2], outline=(226, 180, 85), width=2)

    pdraw.text((cx + 20, cy + 250), "[+] 1080x1920 Shorts covers rebuilt (0% face boxes)", fill=(210, 220, 215), font=f_vid_m)
    pdraw.text((cx + 20, cy + 274), "[+] Valid SMPTE timecodes + lifted banner backdrop", fill=(210, 220, 215), font=f_vid_m)

    page.save(out_path, quality=95)


if __name__ == "__main__":
    print("1. Upgrading Channel Logos & Avatars...", flush=True)
    upgrade_channel_logos()

    print("2. Building all 10 Full-Frame 16:9 Thumbnails & 10 Clean 9:16 Vertical Covers...", flush=True)
    build_all_10_thumbs_and_vertical_covers()

    print("3. Building no-redundancy YouTube Banners with lifted right-side backdrop...", flush=True)
    b_dt, b_ucf = build_no_redundancy_banners()

    print("4. Rendering Full YouTube Channel Page Mockups...", flush=True)
    dt_thumbs = [
        (MTV_DIR / "MTV_01_YT_Thumb_1280x720.jpg", "1989 Michael Jordan Uncut Practice | B-Roll & Breds", "1989 2vuy Master", "3:18"),
        (MTV_DIR / "MTV_02_YT_Thumb_1280x720.jpg", "2002 WCF Kobe & Shaq Locker Room | The Tunnel Tape", "2002 Betacam SP", "4:12"),
        (MTV_DIR / "MTV_03_YT_Thumb_1280x720.jpg", "1990s Terry Bradshaw Studio Blooper | The Raw Feed", "1995 Studio Master", "2:54"),
        (MTV_DIR / "MTV_04_YT_Thumb_1280x720.jpg", "2000 Air Jordan 11 Mall Stampede | B-Roll & Breds", "Foot Locker Tape", "3:40"),
        (MTV_DIR / "MTV_05_YT_Thumb_1280x720.jpg", "1988 World Series Dodgers Dugout | The Tunnel Tape", "Dodger Stadium", "4:05"),
    ]
    dt_vcs = [
        MTV_DIR / "MTV_01_Vertical_Cover_1080x1920.jpg",
        MTV_DIR / "MTV_02_Vertical_Cover_1080x1920.jpg",
        MTV_DIR / "MTV_04_Vertical_Cover_1080x1920.jpg",
    ]
    render_channel_page(
        b_dt,
        ART_DIR / "DeadstockTapes_Avatar_OneWord_1024x1024.png",
        "Deadstock Tapes",
        "@DeadstockTapes",
        "B-Roll & Breds  •  The Tunnel Tape  •  The Raw Feed",
        "Uncut 1970s–2000s hoops, sneaker heat & raw broadcast master tapes in true 60fps.",
        (122, 168, 159),
        (234, 224, 200),
        dt_thumbs,
        dt_vcs,
        MOCKUP_DIR / "YouTube_Page_Mockup_DeadstockTapes.png",
        zoom_avatar_path=ART_DIR / "DeadstockTapes_Avatar_MobileZoom_1024x1024.png",
    )

    ucf_thumbs = [
        (UCF_DIR / "UCF_01_YT_Thumb_1280x720.jpg", "Dorothea Puente 1426 F St Dig | Case Files", "7-Reel Archive", "4:22"),
        (UCF_DIR / "UCF_02_YT_Thumb_1280x720.jpg", "1991 Good Guys Hostage Siege SWAT | Case Files", "Nighttime Master", "3:48"),
        (UCF_DIR / "UCF_03_YT_Thumb_1280x720.jpg", "2002 Jane Doe Border Operation | Case Files", "Uncompressed 2vuy", "3:15"),
        (UCF_DIR / "UCF_04_YT_Thumb_1280x720.jpg", "1999 Synagogue Arson Wave Standoff | Case Files", "June 1999 Master", "3:34"),
        (UCF_DIR / "UCF_05_YT_Thumb_1280x720.jpg", "2018 Camp Fire Paradise Drone Flight | Case Files", "2.7K Aerial Vault", "4:10"),
    ]
    ucf_vcs = [
        UCF_DIR / "UCF_01_Vertical_Cover_1080x1920.jpg",
        UCF_DIR / "UCF_04_Vertical_Cover_1080x1920.jpg",
        UCF_DIR / "UCF_05_Vertical_Cover_1080x1920.jpg",
    ]
    render_channel_page(
        b_ucf,
        ART_DIR / "Modern2026_UnairedCaseFiles_Logo_V1_Viewfinder.png",
        "Unaired Case Files",
        "@UnairedCaseFiles",
        "Declassified Crime-Scene, Courtroom, SWAT & Disaster Tapes",
        "Original unedited crime-scene, courtroom, SWAT & disaster master tapes in true 60fps.",
        (239, 68, 68),
        (241, 241, 241),
        ucf_thumbs,
        ucf_vcs,
        MOCKUP_DIR / "YouTube_Page_Mockup_UnairedCaseFiles.png",
    )
    print("All 10 VCR OSD thumbnails, 10 vertical covers, logos, banners, and channel pages rendered!", flush=True)
