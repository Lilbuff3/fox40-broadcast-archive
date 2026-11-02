import pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = pathlib.Path(r"C:\Users\adam\.gemini\antigravity\brain\4d763763-2f56-420d-8763-3ca83f06e1ef")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 4x supersampling for razor-sharp anti-aliased vector quality
SS = 4


def get_font(name, size):
    paths = {
        "black": r"C:\Windows\Fonts\ariblk.ttf",
        "bold": r"C:\Windows\Fonts\arialbd.ttf",
        "mono": r"C:\Windows\Fonts\consolab.ttf",
        "impact": r"C:\Windows\Fonts\impact.ttf",
    }
    return ImageFont.truetype(paths.get(name, paths["bold"]), size)


def draw_rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build_mtv_logo_v1_geometric_m():
    """
    Modern 2026 Trend 1: Bold Geometric Monogram with Negative-Space Hook ('The Vault Play-M')
    Warm Obsidian (#0B0D11) + Warm Bone White (#F4F1EA) + Broadcast Amber (#F59E0B)
    """
    W = 1000 * SS
    im = Image.new("RGBA", (W, W), (11, 13, 17, 255))
    draw = ImageDraw.Draw(im)

    # Subtle outer geometric ring (Swiss grid touch)
    pad = 70 * SS
    draw.ellipse([pad, pad, W - pad, W - pad], outline=(38, 43, 54, 255), width=6 * SS)

    # Left and Right heavy architectural pillars of the 'M' (also evoking two vertical tape cassettes/towers)
    bone = (244, 241, 234, 255)
    amber = (245, 158, 11, 255)
    dark = (11, 13, 17, 255)

    # Left pillar
    draw_rounded_rect(draw, [215 * SS, 250 * SS, 365 * SS, 750 * SS], radius=28 * SS, fill=bone)
    # Right pillar
    draw_rounded_rect(draw, [635 * SS, 250 * SS, 785 * SS, 750 * SS], radius=28 * SS, fill=bone)

    # Diagonal M-bridge / Magnetic Tape Ribbon in Broadcast Amber (#F59E0B)
    # Forms both the V-dip of the 'M' and a bold forward Play Arrow / Vault Chevron
    poly_left = [
        (290 * SS, 250 * SS),
        (415 * SS, 250 * SS),
        (500 * SS, 470 * SS),
        (585 * SS, 250 * SS),
        (710 * SS, 250 * SS),
        (500 * SS, 695 * SS),
    ]
    draw.polygon(poly_left, fill=amber)

    # Negative-space dark cut separating the amber chevron from the bone pillars for a crisp modern stencil hook
    draw.line([(365 * SS, 230 * SS), (365 * SS, 770 * SS)], fill=dark, width=22 * SS)
    draw.line([(635 * SS, 230 * SS), (635 * SS, 770 * SS)], fill=dark, width=22 * SS)

    # Clean symmetrical geometric Vault Core Dot floating in the upper negative space of the M
    draw.ellipse([464 * SS, 268 * SS, 536 * SS, 340 * SS], fill=bone)

    # Minimalist bottom micro-pill indicator: 60FPS amber bar
    draw_rounded_rect(draw, [420 * SS, 790 * SS, 580 * SS, 816 * SS], radius=13 * SS, fill=amber)

    out = im.resize((1000, 1000), Image.Resampling.LANCZOS).convert("RGB")
    p = OUT_DIR / "Modern2026_MasterTapeVault_Logo_V1_Monogram.png"
    out.save(p, quality=96)
    return p


def build_mtv_logo_v2_dual_spool():
    """
    Modern 2026 Trend 2: Minimalist Geometric Dual-Spool Glyph ('The Infinity Tape Loop')
    """
    W = 1000 * SS
    im = Image.new("RGBA", (W, W), (11, 13, 17, 255))
    draw = ImageDraw.Draw(im)

    bone = (244, 241, 234, 255)
    amber = (245, 158, 11, 255)
    dark = (11, 13, 17, 255)

    # Outer squircle container border
    draw_rounded_rect(draw, [140 * SS, 140 * SS, 860 * SS, 860 * SS], radius=180 * SS, outline=(45, 50, 62, 255), width=8 * SS)

    # Continuous magnetic tape path connecting top-tangents and forming a bold Play/Vault wedge below
    tape_path = [
        (335 * SS, 330 * SS),
        (665 * SS, 330 * SS),
        (665 * SS, 405 * SS),
        (335 * SS, 405 * SS),
    ]
    draw.polygon(tape_path, fill=amber)

    # Bottom V-path of the tape descending to a precision capstan roller at (500, 720)
    draw.line([(230 * SS, 540 * SS), (500 * SS, 735 * SS)], fill=amber, width=56 * SS)
    draw.line([(770 * SS, 540 * SS), (500 * SS, 735 * SS)], fill=amber, width=56 * SS)
    draw.ellipse([460 * SS, 695 * SS, 540 * SS, 775 * SS], fill=amber)
    draw.ellipse([482 * SS, 717 * SS, 518 * SS, 753 * SS], fill=dark)

    # Two bold geometric broadcast tape reels
    for cx in (335 * SS, 665 * SS):
        cy = 465 * SS
        r_out = 148 * SS
        r_mid = 64 * SS
        r_hub = 28 * SS
        draw.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill=bone, outline=dark, width=14 * SS)
        # 3 modern geometric negative-space reel cutouts
        import math
        for angle_deg in (30, 150, 270):
            rad = math.radians(angle_deg)
            hx = cx + int(math.cos(rad) * 96 * SS)
            hy = cy + int(math.sin(rad) * 96 * SS)
            draw.ellipse([hx - 26 * SS, hy - 26 * SS, hx + 26 * SS, hy + 26 * SS], fill=dark)
        draw.ellipse([cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid], fill=amber)
        draw.ellipse([cx - r_hub, cy - r_hub, cx + r_hub, cy + r_hub], fill=dark)

    out = im.resize((1000, 1000), Image.Resampling.LANCZOS).convert("RGB")
    p = OUT_DIR / "Modern2026_MasterTapeVault_Logo_V2_SpoolGlyph.png"
    out.save(p, quality=96)
    return p


def build_ucf_logo_v1_viewfinder():
    """
    Modern 2026 Trend 1: Stark Editorial Duotone + Negative Space ('The Redacted Viewfinder')
    Pitch Black (#08090C) + Bone White (#F4F1EA) + Forensic Signal Red (#EF4444)
    """
    W = 1000 * SS
    im = Image.new("RGBA", (W, W), (8, 9, 12, 255))
    draw = ImageDraw.Draw(im)

    bone = (244, 241, 234, 255)
    crimson = (239, 68, 68, 255)
    dark = (8, 9, 12, 255)

    # 4 Bold Geometric Viewfinder / Evidence Frame Corner Brackets
    b_len = 170 * SS
    b_thick = 48 * SS
    m = 190 * SS

    # Top-Left bracket
    draw.rectangle([m, m, m + b_len, m + b_thick], fill=bone)
    draw.rectangle([m, m, m + b_thick, m + b_len], fill=bone)

    # Bottom-Left bracket
    draw.rectangle([m, W - m - b_thick, m + b_len, W - m], fill=bone)
    draw.rectangle([m, W - m - b_len, m + b_thick, W - m], fill=bone)

    # Bottom-Right bracket
    draw.rectangle([W - m - b_len, W - m - b_thick, W - m, W - m], fill=bone)
    draw.rectangle([W - m - b_thick, W - m - b_len, W - m, W - m], fill=bone)

    # Top-Right: Instead of a static bracket, a bold glowing Signal Crimson REC Circle!
    rec_r = 68 * SS
    rcx, rcy = W - m - rec_r, m + rec_r
    draw.ellipse([rcx - rec_r, rcy - rec_r, rcx + rec_r, rcy + rec_r], fill=crimson)

    # Center Negative-Space Hook: Two redacted document bars, with the lower bar in Crimson and sliced by a forensic magnifier/slash angle
    draw_rounded_rect(draw, [310 * SS, 405 * SS, 690 * SS, 485 * SS], radius=16 * SS, fill=bone)
    draw_rounded_rect(draw, [310 * SS, 525 * SS, 595 * SS, 605 * SS], radius=16 * SS, fill=crimson)

    out = im.resize((1000, 1000), Image.Resampling.LANCZOS).convert("RGB")
    p = OUT_DIR / "Modern2026_UnairedCaseFiles_Logo_V1_Viewfinder.png"
    out.save(p, quality=96)
    return p


def build_ucf_logo_v2_monogram():
    """
    Modern 2026 Trend 2: Heavy Architectural 'U' + Redacted Strike Bar ('The Redacted U')
    """
    W = 1000 * SS
    im = Image.new("RGBA", (W, W), (8, 9, 12, 255))
    draw = ImageDraw.Draw(im)

    bone = (244, 241, 234, 255)
    crimson = (239, 68, 68, 255)
    dark = (8, 9, 12, 255)

    # Heavy geometric U-monogram
    draw_rounded_rect(draw, [240 * SS, 210 * SS, 760 * SS, 790 * SS], radius=240 * SS, fill=bone)
    draw_rounded_rect(draw, [385 * SS, 150 * SS, 615 * SS, 645 * SS], radius=115 * SS, fill=dark)

    # Negative-space dark cut + Redacted Signal Crimson Bar cutting horizontally across the U with a live REC dot
    draw.rectangle([160 * SS, 430 * SS, 840 * SS, 555 * SS], fill=dark)
    draw_rounded_rect(draw, [195 * SS, 452 * SS, 685 * SS, 533 * SS], radius=16 * SS, fill=crimson)
    # Glowing crimson dot on the right of the redaction bar
    draw.ellipse([725 * SS, 452 * SS, 806 * SS, 533 * SS], fill=crimson)

    out = im.resize((1000, 1000), Image.Resampling.LANCZOS).convert("RGB")
    p = OUT_DIR / "Modern2026_UnairedCaseFiles_Logo_V2_RedactedU.png"
    out.save(p, quality=96)
    return p


def build_modern_youtube_banners(mtv_logo_path, ucf_logo_path):
    """
    Builds crisp 2560x1440 YouTube Banners engineered around the exact 1546x423 mobile-safe center zone
    using 2026 Swiss Neo-Minimalist grid & typography (zero AI text hallucinations).
    """
    W, H = 2560, 1440
    # Safe zone is x: 507..2053, y: 508..931

    # 1. MASTER TAPE VAULT BANNER
    mtv_bg = Image.new("RGB", (W, H), (11, 13, 17))
    draw = ImageDraw.Draw(mtv_bg)

    # Architectural Swiss grid lines
    for x in range(0, W, 160):
        draw.line([(x, 0), (x, H)], fill=(20, 24, 32), width=2)
    for y in range(0, H, 160):
        draw.line([(0, y), (W, y)], fill=(20, 24, 32), width=2)

    # Top and bottom safe-zone hairline rules
    draw.line([(0, 508), (W, 508)], fill=(45, 52, 68), width=2)
    draw.line([(0, 931), (W, 931)], fill=(45, 52, 68), width=2)
    # Accent amber bar on left edge of safe zone
    draw.rectangle([520, 548, 534, 891], fill=(245, 158, 11))

    # Paste V1 Monogram icon inside safe zone
    with Image.open(mtv_logo_path) as logo_im:
        logo_resized = logo_im.resize((310, 310), Image.Resampling.LANCZOS)
        mtv_bg.paste(logo_resized, (565, 565))

    f_title = get_font("black", 92)
    f_sub = get_font("bold", 34)
    f_pill = get_font("mono", 28)

    # Pill tag
    draw_rounded_rect(draw, [915, 575, 1645, 628], radius=10, fill=(245, 158, 11))
    draw.text((938, 587), "UNCUT 60FPS BROADCAST ARCHIVE  •  1970–2005", fill=(11, 13, 17), font=f_pill)

    # Main Title
    draw.text((910, 642), "MASTER TAPE VAULT", fill=(244, 241, 234), font=f_title)

    # Subtitle
    draw.text((915, 768), "UNSEEN NBA, NFL & MLB LEGENDS  •  LOCKER ROOM SCRUMS  •  RETRO TV", fill=(156, 163, 175), font=f_sub)
    draw.text((915, 822), "PRESERVED FROM ORIGINAL 2VUY & BETACAM STUDIO REELS", fill=(245, 158, 11), font=f_pill)

    mtv_banner_p = OUT_DIR / "Modern2026_MasterTapeVault_YouTube_Banner.png"
    mtv_bg.save(mtv_banner_p, quality=96)

    # 2. UNAIRED CASE FILES BANNER
    ucf_bg = Image.new("RGB", (W, H), (8, 9, 12))
    udraw = ImageDraw.Draw(ucf_bg)

    for x in range(0, W, 160):
        udraw.line([(x, 0), (x, H)], fill=(18, 20, 26), width=2)
    for y in range(0, H, 160):
        udraw.line([(0, y), (W, y)], fill=(18, 20, 26), width=2)

    udraw.line([(0, 508), (W, 508)], fill=(42, 45, 56), width=2)
    udraw.line([(0, 931), (W, 931)], fill=(42, 45, 56), width=2)
    udraw.rectangle([520, 548, 534, 891], fill=(239, 68, 68))

    with Image.open(ucf_logo_path) as ulogo_im:
        ulogo_resized = ulogo_im.resize((310, 310), Image.Resampling.LANCZOS)
        ucf_bg.paste(ulogo_resized, (565, 565))

    draw_rounded_rect(udraw, [915, 575, 1690, 628], radius=10, fill=(239, 68, 68))
    udraw.text((938, 587), "DECLASSIFIED BROADCAST EVIDENCE  •  TRUE 60FPS", fill=(255, 255, 255), font=f_pill)

    udraw.text((910, 642), "UNAIRED CASE FILES", fill=(244, 241, 234), font=f_title)
    udraw.text((915, 768), "TRUE CRIME TRIALS  •  SWAT STANDOFFS  •  COLD CASES  •  MEGAFIRES", fill=(156, 163, 175), font=f_sub)
    udraw.text((915, 822), "ORIGINAL UNEDITED CRIME-SCENE & COURTROOM MASTER TAPES", fill=(239, 68, 68), font=f_pill)

    ucf_banner_p = OUT_DIR / "Modern2026_UnairedCaseFiles_YouTube_Banner.png"
    ucf_bg.save(ucf_banner_p, quality=96)

    return mtv_banner_p, ucf_banner_p


def build_comparison_board(paths):
    """
    Creates a side-by-side presentation board showing each logo at full size AND inside a real
    circular mobile avatar preview (120px & 48px) so the user can judge instant mobile legibility.
    """
    W, H = 1800, 1050
    board = Image.new("RGB", (W, H), (16, 18, 23))
    draw = ImageDraw.Draw(board)
    f_h = get_font("black", 36)
    f_sub = get_font("bold", 22)
    f_sm = get_font("mono", 18)

    draw.text((50, 32), "2026 MODERN MEDIA BRAND LOGO SYSTEM (LARGE + CIRCULAR MOBILE AVATAR TEST)", fill=(244, 241, 234), font=f_h)
    draw.text((50, 80), "Zero cluttered text inside circles • Bold negative-space geometry • Built for 40x40px TikTok/YouTube dark-mode feeds", fill=(156, 163, 175), font=f_sub)

    cards = [
        ("MTV Option 1: 'The Vault Play-M'", "Bold M + Negative-Space Play Chevron", paths[0], (245, 158, 11)),
        ("MTV Option 2: 'Infinity Tape Loop'", "Minimalist Dual-Spool Geometric Mark", paths[1], (245, 158, 11)),
        ("UCF Option 1: 'Redacted Viewfinder'", "Frame Brackets + Redacted Bar + REC Dot", paths[2], (239, 68, 68)),
        ("UCF Option 2: 'The Redacted U'", "Architectural U + Crimson Redaction Strike", paths[3], (239, 68, 68)),
    ]

    for idx, (title, desc, p, col) in enumerate(cards):
        x0 = 45 + idx * 430
        y0 = 135
        draw_rounded_rect(draw, [x0, y0, x0 + 405, y0 + 865], radius=20, fill=(24, 27, 34), outline=(45, 50, 62), width=2)
        draw.text((x0 + 22, y0 + 22), title, fill=col, font=f_sub)
        draw.text((x0 + 22, y0 + 54), desc, fill=(180, 186, 198), font=f_sm)

        with Image.open(p) as im:
            # Square 360x360 preview
            sq = im.resize((360, 360), Image.Resampling.LANCZOS)
            board.paste(sq, (x0 + 22, y0 + 95))

            # Circular Avatar Crop helper
            def paste_circle(sz, cx, cy):
                av = im.resize((sz, sz), Image.Resampling.LANCZOS)
                mask = Image.new("L", (sz, sz), 0)
                mdraw = ImageDraw.Draw(mask)
                mdraw.ellipse([0, 0, sz - 1, sz - 1], fill=255)
                board.paste(av, (cx, cy), mask)
                draw.ellipse([cx - 2, cy - 2, cx + sz + 2, cy + sz + 2], outline=col, width=3)

            draw.text((x0 + 22, y0 + 485), "CIRCULAR AVATAR SCALE TEST:", fill=(244, 241, 234), font=f_sm)
            paste_circle(160, x0 + 35, y0 + 525)
            draw.text((x0 + 65, y0 + 700), "160px Profile", fill=(156, 163, 175), font=f_sm)

            paste_circle(84, x0 + 245, y0 + 545)
            draw.text((x0 + 235, y0 + 642), "84px Mobile", fill=(156, 163, 175), font=f_sm)

            paste_circle(44, x0 + 265, y0 + 715)
            draw.text((x0 + 225, y0 + 770), "44px Shorts Feed", fill=(156, 163, 175), font=f_sm)

    comp_path = OUT_DIR / "Modern2026_Logo_System_Comparison_Board.png"
    board.save(comp_path, quality=95)
    return comp_path


if __name__ == "__main__":
    p1 = build_mtv_logo_v1_geometric_m()
    p2 = build_mtv_logo_v2_dual_spool()
    p3 = build_ucf_logo_v1_viewfinder()
    p4 = build_ucf_logo_v2_monogram()
    b1, b2 = build_modern_youtube_banners(p1, p3)
    comp = build_comparison_board([p1, p2, p3, p4])
    print("Generated modern 2026 logos & banners:")
    for f in (p1, p2, p3, p4, b1, b2, comp):
        print(" ->", f)
