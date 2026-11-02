import pathlib
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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


def extract_natural_full_frame_16x9(mp4_path, ts_sec, focus_y=0.38):
    """
    Extracts a single 100% authentic, native-gamma 4:3 broadcast still (1080x810)
    from our 59.94fps master MP4 at ts_sec, and crops cleanly to 16:9 (1280x720)
    with ZERO artificial contrast/saturation/skin-smoothing filters.
    """
    tmp_jpg = OUT_ROOT / f"_tmp_nat_{mp4_path.stem}_{ts_sec:.1f}.jpg"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{ts_sec:.2f}", "-i", str(mp4_path),
        "-vf", "crop=1080:810:0:420",
        "-frames:v", "1", "-q:v", "2",
        str(tmp_jpg),
    ]
    subprocess.run(cmd, check=True)
    im = Image.open(tmp_jpg).convert("RGB")
    tmp_jpg.unlink(missing_ok=True)

    # Crop 1080x810 (4:3) -> 1080x608 (16:9) using vertical focus_y, then scale to 1280x720
    src_w, src_h = im.size
    target_h = 608
    y0 = int((src_h - target_h) * focus_y)
    y0 = max(0, min(src_h - target_h, y0))
    cropped = im.crop((0, y0, src_w, y0 + target_h))
    return cropped.resize((1280, 720), Image.Resampling.LANCZOS)


def apply_vcr_osd_and_corner_hook(canvas, tc_str, hook_text, hook_rgb=(255, 230, 0), sub_mode="PLAY"):
    """
    Applies the authentic 90s Betacam SP / VCR On-Screen Display (OSD) graphics:
    - Top-left: 'PLAY ▶' + 'TC 01:14:08:22' in crisp white VCR monospace font with hard black OSD shadow.
    - Bottom-left: 2-3 word max condensed block hook ('UNAIRED 1989', '$160 RIOT', 'OFF THE AIR')
      in classic broadcast yellow (#FFE600) with hard black stroke & drop shadow.
    - Zero split-screen lines, zero modern pill badges, and 100% unobstructed subject & bottom-right corner.
    """
    W, H = canvas.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Smooth 2D corner cushion (zero hard vertical or horizontal edges!)
    for y in range(220):
        ty = 1.0 - (y / 220.0)
        for x in range(560):
            tx = 1.0 - (x / 560.0)
            a = int(115 * ((tx * ty) ** 1.4))
            if a > 0:
                odraw.point((x, y), fill=(0, 0, 0, a))

    # Full-width smooth bottom gradient (only bottom 210px, tapering smoothly across full width W)
    for y in range(510, H):
        ty = (y - 510) / (H - 510)
        alpha = int(150 * (ty ** 1.5))
        odraw.line([(0, y), (W, y)], fill=(4, 6, 8, alpha))

    base = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    # 1. Top-Left VCR / Betacam OSD ('PLAY ▶' + 'TC ...')
    f_osd = get_font("lucida", 44)
    osd_x, osd_y = 52, 42

    # Hard black OSD shadow + crisp white text for 'PLAY'
    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((osd_x + dx, osd_y + dy), sub_mode, fill=(0, 0, 0, 240), font=f_osd)
    draw.text((osd_x, osd_y), sub_mode, fill=(246, 246, 246, 255), font=f_osd)

    # Geometric VCR Play Triangle ▶ next to 'PLAY'
    bbox_play = draw.textbbox((osd_x, osd_y), sub_mode, font=f_osd)
    tri_x = bbox_play[2] + 22
    tri_y = osd_y + 6
    tri_pts_shadow = [(tri_x + 4, tri_y + 4), (tri_x + 4, tri_y + 36), (tri_x + 32, tri_y + 20)]
    tri_pts = [(tri_x, tri_y), (tri_x, tri_y + 32), (tri_x + 28, tri_y + 16)]
    draw.polygon(tri_pts_shadow, fill=(0, 0, 0, 240))
    draw.polygon(tri_pts, fill=(246, 246, 246, 255))

    # Line 2: 'TC 01:14:08:22'
    tc_y = osd_y + 56
    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((osd_x + dx, tc_y + dy), tc_str, fill=(0, 0, 0, 240), font=f_osd)
    draw.text((osd_x, tc_y), tc_str, fill=(246, 246, 246, 255), font=f_osd)

    # 2. Bottom-Left 2-3 Word Condensed Block Hook ('UNAIRED 1989', '$160 RIOT', etc.)
    f_hook = get_font("impact", 118)
    hx, hy = 52, 558

    # Hard retro block drop shadow (+9px, +9px)
    draw.text(
        (hx + 9, hy + 9),
        hook_text,
        fill=(0, 0, 0, 255),
        font=f_hook,
        stroke_width=8,
        stroke_fill=(0, 0, 0, 255),
    )
    # Main condensed yellow/white block text with crisp black outline
    draw.text(
        (hx, hy),
        hook_text,
        fill=hook_rgb + (255,),
        font=f_hook,
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )

    return base.convert("RGB")


def build_all_10_vcr_osd_thumbs():
    vcr_yellow = (255, 228, 0)     # Classic VCR / Broadcast Yellow (matches tunnel reference)
    evidence_yellow = (255, 220, 0)

    specs = [
        # ==================== CHANNEL 1: DEADSTOCK TAPES (5 VIDEOS) ====================
        (
            MTV_DIR / "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4",
            20.8, 0.35,
            "TC 02:14:89:23", "UNAIRED 1989", vcr_yellow,
            MTV_DIR / "MTV_01_YT_Thumb_1280x720.jpg",
        ),
        (
            MTV_DIR / "MTV_02_2002_Kobe_Bryant_Shaq_vs_Kings_WCF_5994fps.mp4",
            5.0, 0.25,
            "TC 05:28:02:08", "2002 LOCKERS", vcr_yellow,
            MTV_DIR / "MTV_02_YT_Thumb_1280x720.jpg",
        ),
        (
            MTV_DIR / "MTV_03_1990s_FOX_NFL_Sunday_Bradshaw_Howie_Long_5994fps.mp4",
            34.0, 0.28,
            "TC 11:12:95:04", "OFF THE AIR", vcr_yellow,
            MTV_DIR / "MTV_03_YT_Thumb_1280x720.jpg",
        ),
        (
            MTV_DIR / "MTV_04_2000_Air_Jordan_XI_XVI_Foot_Locker_Mall_Riot_5994fps.mp4",
            23.0, 0.45,
            "TC 12:23:00:11", "$160 RIOT", vcr_yellow,
            MTV_DIR / "MTV_04_YT_Thumb_1280x720.jpg",
        ),
        (
            MTV_DIR / "MTV_05_1988_World_Series_As_Dodgers_and_80s_NFL_Gastineau_5994fps.mp4",
            11.0, 0.38,
            "TC 10:15:88:01", "1988 TUNNEL", vcr_yellow,
            MTV_DIR / "MTV_05_YT_Thumb_1280x720.jpg",
        ),
        # ==================== CHANNEL 2: UNAIRED CASE FILES (5 VIDEOS) ====================
        (
            UCF_DIR / "UCF_01_1988_Dorothea_Puente_Trial_3D_Model_Body_Bags_5994fps.mp4",
            8.0, 0.45,
            "TC 11:11:88:07", "7 BODIES FOUND", evidence_yellow,
            UCF_DIR / "UCF_01_YT_Thumb_1280x720.jpg",
        ),
        (
            UCF_DIR / "UCF_02_1991_Sacramento_Good_Guys_Hostage_SWAT_Raid_5994fps.mp4",
            38.0, 0.45,
            "TC 04:04:91:21", "41 HOSTAGES", evidence_yellow,
            UCF_DIR / "UCF_02_YT_Thumb_1280x720.jpg",
        ),
        (
            UCF_DIR / "UCF_03_2002_Jane_Doe_Dumpster_Forensic_Clay_Bust_5994fps.mp4",
            12.0, 0.42,
            "TC 01:19:02:14", "JANE DOE TAPE", evidence_yellow,
            UCF_DIR / "UCF_03_YT_Thumb_1280x720.jpg",
        ),
        (
            UCF_DIR / "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4",
            24.0, 0.42,
            "TC 06:18:99:03", "3 ARSON FIRES", evidence_yellow,
            UCF_DIR / "UCF_04_YT_Thumb_1280x720.jpg",
        ),
        (
            UCF_DIR / "UCF_05_California_Megafire_Carr_Inferno_DC10_Drop_Paradise_Drone_5994fps.mp4",
            28.5, 0.48,
            "TC 07:28:18:10", "DC-10 DROP", evidence_yellow,
            UCF_DIR / "UCF_05_YT_Thumb_1280x720.jpg",
        ),
    ]

    for mp4_p, ts, fy, tc, hook, col, out_p in specs:
        frame = extract_natural_full_frame_16x9(mp4_p, ts, focus_y=fy)
        thumb = apply_vcr_osd_and_corner_hook(frame, tc, hook, hook_rgb=col)
        thumb.save(out_p, quality=95)
        dest_dir = THUMB_DT_DIR if out_p.name.startswith("MTV_") else THUMB_UCF_DIR
        shutil.copy2(out_p, dest_dir / out_p.name)


def build_no_redundancy_banners():
    """
    Builds both 2560x1440 YouTube Banners WITHOUT repeating the circular avatar on the left!
    Instead uses an authentic darkened archival video backdrop + Betacam OSD viewfinder brackets
    and pure typographic hierarchy so there is zero logo duplication above the profile avatar.
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

    # --- 1. DEADSTOCK TAPES BANNER (Typographic + Archival Tunnel/Court Texture + VCR OSD) ---
    b1 = Image.new("RGB", (W, H), (10, 12, 15))
    # Composite a subtly darkened, desaturated archival court/tunnel still on the right side of the safe zone
    court_bg = extract_natural_full_frame_16x9(
        MTV_DIR / "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4", 22.4, focus_y=0.4
    ).resize((2560, 1440), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=6))

    # Darken court_bg heavily so typography has 100% contrast while preserving gritty 90s arena atmosphere
    dark_layer = Image.new("RGBA", (W, H), (10, 13, 16, 218))
    b1 = Image.alpha_composite(court_bg.convert("RGBA"), dark_layer).convert("RGB")
    d1 = ImageDraw.Draw(b1)

    # Scanline & grid texture
    for y in range(0, H, 6):
        d1.line([(0, y), (W, y)], fill=(8, 10, 13), width=2)

    # Safe desktop strip: x=400..2160, y=565..875 (1760x310)
    # Draw VCR Viewfinder Corner Brackets inside safe zone
    bx0, by0, bx1, by1 = 440, 582, 2120, 858
    blen = 36
    for cx, cy, sx, sy in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
        d1.line([(cx, cy), (cx + sx * blen, cy)], fill=TEAL, width=4)
        d1.line([(cx, cy), (cx, cy + sy * blen)], fill=TEAL, width=4)

    # Left vertical Betacam SP tape spine accent bars (zero circular logo!)
    d1.rectangle([485, 602, 501, 838], fill=TEAL)
    d1.rectangle([509, 602, 519, 838], fill=ORANGE)

    # Top-right VCR OSD readout inside banner (geometric play triangle, zero tofu glyphs)
    d1.text((1710, 596), "PLAY     SP 59.94Hz", fill=CREAM, font=f_osd)
    d1.polygon([(1790, 598), (1790, 620), (1810, 609)], fill=CREAM)
    d1.text((1710, 630), "TC 19:89:20:02", fill=TEAL, font=f_osd)

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

    # --- 2. UNAIRED CASE FILES BANNER (No circular logo duplication, pure declassified OSD header) ---
    b2 = Image.new("RGB", (W, H), (10, 11, 14))
    crime_bg = extract_natural_full_frame_16x9(
        UCF_DIR / "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4", 24.0, focus_y=0.4
    ).resize((2560, 1440), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=6))
    b2 = Image.alpha_composite(crime_bg.convert("RGBA"), Image.new("RGBA", (W, H), (10, 11, 14, 224))).convert("RGB")
    d2 = ImageDraw.Draw(b2)

    for y in range(0, H, 6):
        d2.line([(0, y), (W, y)], fill=(8, 9, 12), width=2)

    for cx, cy, sx, sy in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
        d2.line([(cx, cy), (cx + sx * blen, cy)], fill=CRIMSON, width=4)
        d2.line([(cx, cy), (cx, cy + sy * blen)], fill=CRIMSON, width=4)

    d2.rectangle([485, 602, 501, 838], fill=CRIMSON)
    d2.rectangle([509, 602, 519, 838], fill=(240, 240, 240))

    d2.text((1710, 596), "REC     EVIDENCE REEL", fill=CRIMSON, font=f_osd)
    d2.ellipse([1772, 600, 1790, 618], fill=CRIMSON)
    d2.text((1710, 630), "TC 11:11:88:07", fill=(220, 220, 220), font=f_osd)

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
    out_path,
    zoom_avatar_path=None,
):
    PW, PH = 1920, 1380
    page = Image.new("RGB", (PW, PH), (15, 15, 15))
    pdraw = ImageDraw.Draw(page)

    # 1. Exact 1:1 crop (1760x310) from the center of the 2560x1440 banner (zero distortion, zero duplicate logo)
    with Image.open(banner_path) as bim:
        b_crop = bim.crop((400, 565, 2160, 875))
        mask_b = Image.new("L", (1760, 310), 0)
        ImageDraw.Draw(mask_b).rounded_rectangle([0, 0, 1759, 309], radius=24, fill=255)
        page.paste(b_crop, (80, 30), mask_b)

    # 2. Circular Profile Avatar (160x160) on the left below banner
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
        # Complete front-loaded title (<52 chars) - zero truncation!
        pdraw.text((px + 4, py + card_h + 10), v_title, fill=title_rgb, font=f_vid_t)
        pdraw.text((px + 4, py + card_h + 36), f"{v_views}  •  Uncut 60fps Master", fill=(160, 160, 160), font=f_vid_m)

    # 6th slot: Diagnostic comparison card
    cx, cy = 1220, 1015
    pdraw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill=(20, 24, 28), outline=accent_rgb, width=3)

    if zoom_avatar_path and zoom_avatar_path.exists():
        pdraw.text((cx + 22, cy + 16), "1-WORD CREST vs. MOBILE ZOOM AT 72px & 42px:", fill=title_rgb, font=f_vid_t)
        with Image.open(avatar_path) as av_full, Image.open(zoom_avatar_path) as av_zm:
            # Left column: Full 1-Word Single-Character Crest
            pdraw.text((cx + 24, cy + 52), "Option A: Full 1-Word Crest", fill=accent_rgb, font=f_vid_m)
            for sz, ox, oy, lbl in [(84, cx + 28, cy + 82, "84px"), (46, cx + 135, cy + 102, "46px Shorts")]:
                a_sz = av_full.resize((sz, sz), Image.Resampling.LANCZOS)
                m_sz = Image.new("L", (sz, sz), 0)
                ImageDraw.Draw(m_sz).ellipse([0, 0, sz - 1, sz - 1], fill=255)
                page.paste(a_sz, (ox, oy), m_sz)
                pdraw.ellipse([ox - 2, oy - 2, ox + sz + 2, oy + sz + 2], outline=accent_rgb, width=2)
                pdraw.text((ox, oy + sz + 8), lbl, fill=(190, 190, 190), font=f_vid_m)

            # Right column: Tight Mobile Zoom Crop (Head + Sneaker + Betacam)
            pdraw.text((cx + 275, cy + 52), "Option B: Tight Character Zoom", fill=(226, 180, 85), font=f_vid_m)
            for sz, ox, oy, lbl in [(84, cx + 285, cy + 82, "84px"), (46, cx + 392, cy + 102, "46px Shorts")]:
                a_sz = av_zm.resize((sz, sz), Image.Resampling.LANCZOS)
                m_sz = Image.new("L", (sz, sz), 0)
                ImageDraw.Draw(m_sz).ellipse([0, 0, sz - 1, sz - 1], fill=255)
                page.paste(a_sz, (ox, oy), m_sz)
                pdraw.ellipse([ox - 2, oy - 2, ox + sz + 2, oy + sz + 2], outline=(226, 180, 85), width=2)
                pdraw.text((ox, oy + sz + 8), lbl, fill=(190, 190, 190), font=f_vid_m)

        pdraw.text((cx + 22, cy + 212), "[+] Full-frame natural broadcast stills (0% AI smoothing)", fill=(210, 220, 215), font=f_vid_m)
        pdraw.text((cx + 22, cy + 238), "[+] Authentic VCR OSD (PLAY / TC) + 2-word corner hook", fill=(210, 220, 215), font=f_vid_m)
        pdraw.text((cx + 22, cy + 264), "[+] Zero banner logo duplication + <50-char front-loaded titles", fill=(210, 220, 215), font=f_vid_m)
    else:
        pdraw.text((cx + 24, cy + 24), "AUTHENTIC VCR OSD THUMBNAIL SYSTEM:", fill=accent_rgb, font=f_tab)
        bullets = [
            "1. 100% Full-Frame Native Broadcast Stills",
            "2. Zero Split-Screen Lines or Border Collisions",
            "3. Authentic VCR OSD (PLAY + SMPTE Timecode)",
            "4. 2-3 Word Condensed Corner Hook (#FFE400)",
            "5. Zero Banner Logo Duplication + Full Titles",
        ]
        for bi, btxt in enumerate(bullets):
            pdraw.text((cx + 24, cy + 74 + bi * 42), btxt, fill=(230, 230, 235), font=f_vid_t)

    page.save(out_path, quality=95)


if __name__ == "__main__":
    print("Building all 10 Full-Frame VCR OSD Thumbnails...", flush=True)
    build_all_10_vcr_osd_thumbs()

    print("Building no-redundancy YouTube Banners...", flush=True)
    b_dt, b_ucf = build_no_redundancy_banners()

    print("Rendering Full YouTube Channel Page Mockups...", flush=True)
    dt_thumbs = [
        (MTV_DIR / "MTV_01_YT_Thumb_1280x720.jpg", "Michael Jordan Uncut 1989 Practice | B-Roll & Breds", "1989 2vuy Master", "3:18"),
        (MTV_DIR / "MTV_02_YT_Thumb_1280x720.jpg", "Kobe & Shaq Raw 2002 WCF Lockers | The Tunnel Tape", "2002 Betacam SP", "4:12"),
        (MTV_DIR / "MTV_03_YT_Thumb_1280x720.jpg", "Howie Long & Bradshaw Off-Air | The Raw Feed", "1995 Studio Master", "2:54"),
        (MTV_DIR / "MTV_04_YT_Thumb_1280x720.jpg", "Air Jordan 11 Mall Riot (2000) | B-Roll & Breds", "Foot Locker Tape", "3:40"),
        (MTV_DIR / "MTV_05_YT_Thumb_1280x720.jpg", "1988 World Series Uncut Dugout | The Tunnel Tape", "Dodger Stadium", "4:05"),
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
        MOCKUP_DIR / "YouTube_Page_Mockup_DeadstockTapes.png",
        zoom_avatar_path=ART_DIR / "DeadstockTapes_Avatar_MobileZoom_1024x1024.png",
    )

    ucf_thumbs = [
        (UCF_DIR / "UCF_01_YT_Thumb_1280x720.jpg", "Dorothea Puente 1988 Crime Scene | Case Files", "7-Reel Archive", "4:22"),
        (UCF_DIR / "UCF_02_YT_Thumb_1280x720.jpg", "1991 Good Guys Hostage SWAT Raid | Case Files", "Nighttime Master", "3:48"),
        (UCF_DIR / "UCF_03_YT_Thumb_1280x720.jpg", "Unsolved 2002 Jane Doe Cold Case | Case Files", "Uncompressed 2vuy", "3:15"),
        (UCF_DIR / "UCF_04_YT_Thumb_1280x720.jpg", "1999 Sacramento Arson ATF Manhunt | Case Files", "June 1999 Master", "3:34"),
        (UCF_DIR / "UCF_05_YT_Thumb_1280x720.jpg", "California Megafire DC-10 & Drone | Case Files", "2.7K Aerial Vault", "4:10"),
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
        MOCKUP_DIR / "YouTube_Page_Mockup_UnairedCaseFiles.png",
    )
    print("All 10 VCR OSD thumbnails, banners, and channel pages rendered!", flush=True)
