import asyncio
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

import edge_tts

GDRIVE_BIN = shutil.which("gdrive") or "gdrive"
FFMPEG_BIN = shutil.which("ffmpeg") or r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
FFPROBE_BIN = shutil.which("ffprobe") or r"C:\ProgramData\chocolatey\bin\ffprobe.exe"
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK_ROOT = pathlib.Path(r"C:\Users\adam\AppData\Local\Temp\fox40_launch_wave1_build")
RAW_CACHE = WORK_ROOT / "raw_cache"
INTER_DIR = WORK_ROOT / "intermediate"
OUT_ROOT = WORK_ROOT / "ready_to_post"
BRANDING_SRC_DIR = REPO_ROOT / "assets" / "branding"
DOCS_DIR = REPO_ROOT / "docs"
THUMB_DT_DIR = REPO_ROOT / "assets" / "thumbnails" / "deadstock_tapes"
THUMB_UCF_DIR = REPO_ROOT / "assets" / "thumbnails" / "unaired_case_files"

for d in (RAW_CACHE, INTER_DIR, OUT_ROOT, DOCS_DIR, THUMB_DT_DIR, THUMB_UCF_DIR):
    d.mkdir(parents=True, exist_ok=True)


VIDEOS = [
    # ==================== BRAND 1: DEADSTOCK TAPES (5 VIDEOS) ====================
    {
        "id": "MTV_01",
        "brand": "Deadstock Tapes",
        "voice": "en-US-GuyNeural",
        "accent_hex": "E2B455",       # Mustard Gold
        "accent_rgb": (226, 180, 85),
        "accent_ass": "&H0055B4E2",   # BGR for ASS (&H00BBGGRR)
        "sub_hex": "7AA89F",          # Vintage Mint-Teal
        "badge_text": "DEADSTOCK TAPES  |  B-ROLL & BREDS",
        "header_title": "1989 MICHAEL JORDAN UNCUT",
        "header_sub": "FEB 1989  •  ARCO ARENA  •  UNCOMPRESSED 2VUY MASTER",
        "telestration": {"x": 360, "y": 540, "w": 360, "h": 480, "label": "MICHAEL JORDAN #23 (AGE 26)"},
        "thumb_hook_top": "UNSEEN 1989 MASTER TAPE",
        "thumb_hook_main": "26-YR-OLD JORDAN",
        "thumb_circle": (640, 340, 175),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 6.0,
        "thumb_ts": 20.8,
        "thumb_focus_y": 0.35,
        "thumb_tc": "TC 02:14:89:23",
        "thumb_hook": "UNAIRED 1989",
        "thumb_hook_rgb": (255, 228, 0),
        "out_name": "MTV_01_1989_Michael_Jordan_Uncut_Practice_5994fps.mp4",
        "narration": (
            "Unseen 1989 master tape. Before Michael Jordan won a single NBA championship, "
            "our broadcast cameras rolled courtside at Sacramento's original ARCO Arena. "
            "Watch a twenty-six-year-old Jordan effortlessly draining jumpers during shootaround "
            "and joking with teammate Craig Hodges, while Kings head coach Dick Motta tries to "
            "game-plan for a man about to drop fifty. Preserved directly from an uncompressed "
            "studio master at sixty frames per second. Follow Deadstock Tapes for uncut sports history."
        ),
        "segments": [
            {
                "drive_id": "1r_CHsukl4CL50hEl19wlgOzMh31Ko6-_",
                "raw_name": "01B_1989_Michael_Jordan_Full_Reel_Motta_and_MJ_16x9_Master_60fps.mp4",
                "ss": 53.0,
                "t": 28.0,
                "pre_deinterlaced_crop": "crop=1440:1080:240:0",
                "keep_raw": True,
            },
            {
                "drive_id": "1r_CHsukl4CL50hEl19wlgOzMh31Ko6-_",
                "raw_name": "01B_1989_Michael_Jordan_Full_Reel_Motta_and_MJ_16x9_Master_60fps.mp4",
                "ss": 24.0,
                "t": 15.0,
                "pre_deinterlaced_crop": "crop=1440:1080:240:0",
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "MTV_02",
        "brand": "Deadstock Tapes",
        "voice": "en-US-GuyNeural",
        "accent_hex": "E2B455",
        "accent_rgb": (226, 180, 85),
        "accent_ass": "&H0055B4E2",
        "sub_hex": "7AA89F",
        "badge_text": "DEADSTOCK TAPES  |  THE TUNNEL TAPE",
        "header_title": "2002 KOBE & SHAQ vs. KINGS",
        "header_sub": "MAY 2002  •  WESTERN CONF. FINALS  •  BETACAM MASTER",
        "telestration": {"x": 380, "y": 490, "w": 420, "h": 520, "label": "KOBE BRYANT #8 (2002 WCF)"},
        "thumb_hook_top": "2002 WCF LOCKER ROOM",
        "thumb_hook_main": "23-YR-OLD KOBE & SHAQ",
        "thumb_circle": (700, 320, 175),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 7.5,
        "thumb_ts": 5.0,
        "thumb_focus_y": 0.25,
        "thumb_tc": "TC 05:28:02:08",
        "thumb_hook": "2002 LOCKERS",
        "thumb_hook_rgb": (255, 228, 0),
        "out_name": "MTV_02_2002_Kobe_Bryant_Shaq_vs_Kings_WCF_5994fps.mp4",
        "narration": (
            "May 2002. Inside the locker room during the most controversial playoff series in NBA history. "
            "This raw FOX40 Betacam tape captures a twenty-three-year-old Kobe Bryant moments after "
            "battling the Sacramento Kings in the Western Conference Finals. On the floor, our courtside "
            "camera caught Shaquille O'Neal trading blows in the paint with Vlade Divac, followed by "
            "raw locker room reactions from Mike Bibby and Chris Webber. Uncut and unseen for over twenty years. "
            "Follow Deadstock Tapes for uncut sports history."
        ),
        "segments": [
            {
                "drive_id": "1q5sBG3EPAq7LPCitDoSoDPdsNkYaxNYh",
                "raw_name": "FOR_KATIE__KINGS_2002_7400145.mov",
                "ss": 114.5,
                "t": 14.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1q5sBG3EPAq7LPCitDoSoDPdsNkYaxNYh",
                "raw_name": "FOR_KATIE__KINGS_2002_7400145.mov",
                "ss": 63.0,
                "t": 16.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1q5sBG3EPAq7LPCitDoSoDPdsNkYaxNYh",
                "raw_name": "FOR_KATIE__KINGS_2002_7400145.mov",
                "ss": 34.0,
                "t": 14.5,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "MTV_03",
        "brand": "Deadstock Tapes",
        "voice": "en-US-GuyNeural",
        "accent_hex": "E2B455",
        "accent_rgb": (226, 180, 85),
        "accent_ass": "&H0055B4E2",
        "sub_hex": "7AA89F",
        "badge_text": "DEADSTOCK TAPES  |  THE RAW FEED",
        "header_title": "90s FOX NFL SUNDAY UNCUT",
        "header_sub": "TERRY BRADSHAW  •  HOWIE LONG  •  RONNIE LOTT",
        "telestration": {"x": 300, "y": 500, "w": 460, "h": 520, "label": "TERRY BRADSHAW OFF-AIR"},
        "thumb_hook_top": "LOST 1990s STUDIO TAPE",
        "thumb_hook_main": "FOX NFL SUNDAY UNCUT",
        "thumb_circle": (640, 340, 180),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 12.0,
        "thumb_ts": 34.0,
        "thumb_focus_y": 0.28,
        "thumb_tc": "TC 11:12:95:04",
        "thumb_hook": "OFF THE AIR",
        "thumb_hook_rgb": (255, 228, 0),
        "out_name": "MTV_03_1990s_FOX_NFL_Sunday_Bradshaw_Howie_Long_5994fps.mp4",
        "narration": (
            "Hidden inside an unlabeled 1990s news tape, we discovered an exclusive behind-the-scenes "
            "tour of the original FOX NFL Sunday studio in Hollywood. Watch Hall of Famer Terry Bradshaw "
            "cutting up between takes when the network cameras were turned off, alongside Howie Long, "
            "James Brown, and forty-niners legend Ronnie Lott at the iconic broadcast desk. "
            "This raw local station tape hasn't been seen since the nineties. "
            "Follow Deadstock Tapes for uncut sports history."
        ),
        "segments": [
            {
                "drive_id": "1XkgAN8rxcF1fwPU14oPctQ85oRb7ke0b",
                "raw_name": "FOR_AMY_2__DONNA_7037749.mov",
                "ss": 198.0,
                "t": 18.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1XkgAN8rxcF1fwPU14oPctQ85oRb7ke0b",
                "raw_name": "FOR_AMY_2__DONNA_7037749.mov",
                "ss": 260.0,
                "t": 15.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1XkgAN8rxcF1fwPU14oPctQ85oRb7ke0b",
                "raw_name": "FOR_AMY_2__DONNA_7037749.mov",
                "ss": 315.0,
                "t": 12.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "MTV_04",
        "brand": "Deadstock Tapes",
        "voice": "en-US-GuyNeural",
        "accent_hex": "E2B455",
        "accent_rgb": (226, 180, 85),
        "accent_ass": "&H0055B4E2",
        "sub_hex": "7AA89F",
        "badge_text": "DEADSTOCK TAPES  |  B-ROLL & BREDS",
        "header_title": "AIR JORDAN MALL RIOT (2000)",
        "header_sub": "FOOT LOCKER STAMPEDE  •  JORDAN XI & XVI RELEASE",
        "telestration": {"x": 220, "y": 520, "w": 640, "h": 500, "label": "FOOT LOCKER CROWD SURGE"},
        "thumb_hook_top": "BEFORE SNKRS APP EXISTED",
        "thumb_hook_main": "2000 JORDAN MALL RIOT",
        "thumb_circle": (600, 380, 180),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 5.0,
        "thumb_ts": 23.0,
        "thumb_focus_y": 0.45,
        "thumb_tc": "TC 12:23:00:11",
        "thumb_hook": "$160 RIOT",
        "thumb_hook_rgb": (255, 228, 0),
        "out_name": "MTV_04_2000_Air_Jordan_XI_XVI_Foot_Locker_Mall_Riot_5994fps.mp4",
        "narration": (
            "Before sneaker apps and online raffles, buying a pair of Air Jordans meant surviving "
            "a literal mall riot. This raw year-2000 and 2001 broadcast tape shows hundreds of shoppers "
            "surging against the security gates at Foot Locker while Sacramento Sheriff's deputies "
            "scramble to hold the line. All to get their hands on the retro patent-leather Air Jordan "
            "Eleven and the brand-new Jordan Sixteen for a hundred and sixty bucks. "
            "Follow Deadstock Tapes for uncut sports history."
        ),
        "segments": [
            {
                "drive_id": "1lob1KkNCXPYUimcM2MKU30_gYMZI-sAY",
                "raw_name": "FOR_AMY_2__NIKE_MALL_RIOT_7984457.mov",
                "ss": 38.0,
                "t": 18.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1lob1KkNCXPYUimcM2MKU30_gYMZI-sAY",
                "raw_name": "FOR_AMY_2__NIKE_MALL_RIOT_7984457.mov",
                "ss": 18.0,
                "t": 12.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1lob1KkNCXPYUimcM2MKU30_gYMZI-sAY",
                "raw_name": "FOR_AMY_2__NIKE_MALL_RIOT_7984457.mov",
                "ss": 96.0,
                "t": 14.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "MTV_05",
        "brand": "Deadstock Tapes",
        "voice": "en-US-GuyNeural",
        "accent_hex": "E2B455",
        "accent_rgb": (226, 180, 85),
        "accent_ass": "&H0055B4E2",
        "sub_hex": "7AA89F",
        "badge_text": "DEADSTOCK TAPES  |  THE TUNNEL TAPE",
        "header_title": "1988 WORLD SERIES & 80s NFL",
        "header_sub": "DODGER STADIUM FIELD TAPE  •  MARK GASTINEAU #99",
        "telestration": {"x": 300, "y": 520, "w": 480, "h": 520, "label": "1988 OAKLAND A's AT DODGER STADIUM"},
        "thumb_hook_top": "1988 WORLD SERIES VAULT",
        "thumb_hook_main": "A's vs DODGERS + 80s NFL",
        "thumb_circle": (620, 360, 175),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 14.0,
        "thumb_ts": 11.0,
        "thumb_focus_y": 0.38,
        "thumb_tc": "TC 10:15:88:01",
        "thumb_hook": "1988 TUNNEL",
        "thumb_hook_rgb": (255, 228, 0),
        "out_name": "MTV_05_1988_World_Series_As_Dodgers_and_80s_NFL_Gastineau_5994fps.mp4",
        "narration": (
            "Two legendary 1980s sports moments preserved on a single broadcast master reel. "
            "First, step onto the grass at Dodger Stadium during the 1988 World Series between "
            "the Oakland A's and Los Angeles Dodgers, with field-level cameras right outside the "
            "dugout tunnel. And on the exact same tape, raw eighties NFL action featuring New York Jets "
            "pass rusher Mark Gastineau celebrating a sack against Kansas City with his famous sack dance. "
            "Follow Deadstock Tapes for uncut sports history."
        ),
        "segments": [
            {
                "drive_id": "1qqMRQaaT-Wu-rB0JDS_6-FBYHK8AxNIy",
                "raw_name": "FOR_KATIE__DODGERS_7400152.mov",
                "ss": 52.0,
                "t": 28.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1qqMRQaaT-Wu-rB0JDS_6-FBYHK8AxNIy",
                "raw_name": "FOR_KATIE__DODGERS_7400152.mov",
                "ss": 35.0,
                "t": 15.0,
                "keep_raw": False,
            },
        ],
    },


    # ==================== BRAND 2: UNAIRED CASE FILES (5 VIDEOS) ====================
    {
        "id": "UCF_01",
        "brand": "Unaired Case Files",
        "voice": "en-US-ChristopherNeural",
        "accent_hex": "EF4444",       # Forensic Crimson
        "accent_rgb": (239, 68, 68),
        "accent_ass": "&H004444EF",   # BGR for ASS
        "sub_hex": "EAB308",          # Crime-Scene Amber
        "badge_text": "UNAIRED CASE FILES  |  CASE FILES",
        "header_title": "DOROTHEA PUENTE MURDER TRIAL",
        "header_sub": "NOV 1988  •  1426 F STREET EXCAVATION & 3D MODEL",
        "telestration": {"x": 240, "y": 560, "w": 620, "h": 440, "label": "EVIDENCE: 1426 F ST BODY BAG RECOVERY"},
        "thumb_hook_top": "7 BODIES IN HER GARDEN",
        "thumb_hook_main": "THE PUENTE TRIAL TAPES",
        "thumb_circle": (640, 380, 190),
        "thumb_seg_idx": 0,
        "thumb_offset_sec": 6.5,
        "thumb_ts": 8.0,
        "thumb_focus_y": 0.45,
        "thumb_tc": "TC 11:11:88:07",
        "thumb_hook": "7 BODIES FOUND",
        "thumb_hook_rgb": (255, 220, 0),
        "out_name": "UCF_01_1988_Dorothea_Puente_Trial_3D_Model_Body_Bags_5994fps.mp4",
        "narration": (
            "November 1988, Sacramento, California. Behind the white picket fence of 1426 F Street, "
            "police uncovered seven bodies buried in the garden of boarding-house landlady Dorothea Puente. "
            "This raw archival tape captures coroners carrying body bags from her yard while detectives "
            "dig through the soil. Inside the courtroom, prosecutors wheeled in a three-dimensional scale "
            "model of the house as Puente sat in silence, dressed like a harmless grandmother on trial for murder."
        ),
        "segments": [
            {
                "drive_id": "10T08RUfxWMBfV18ydgcpwZTjpd4V4F9O",
                "raw_name": "FOR_AMY_2__PUENTE5_7228689.mov",
                "ss": 44.0,
                "t": 14.0,
                "keep_raw": True,
            },
            {
                "drive_id": "10T08RUfxWMBfV18ydgcpwZTjpd4V4F9O",
                "raw_name": "FOR_AMY_2__PUENTE5_7228689.mov",
                "ss": 89.0,
                "t": 11.0,
                "keep_raw": False,
            },
            {
                "drive_id": "1Gjtc4Vy0sb5tKWnSSaNzvelmAS_PEBLv",
                "raw_name": "FOR_AMY_2__PUENTE3_7228685.mov",
                "ss": 15.0,
                "t": 11.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1Gjtc4Vy0sb5tKWnSSaNzvelmAS_PEBLv",
                "raw_name": "FOR_AMY_2__PUENTE3_7228685.mov",
                "ss": 136.0,
                "t": 10.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "UCF_02",
        "brand": "Unaired Case Files",
        "voice": "en-US-ChristopherNeural",
        "accent_hex": "EF4444",
        "accent_rgb": (239, 68, 68),
        "accent_ass": "&H004444EF",
        "sub_hex": "EAB308",
        "badge_text": "UNAIRED CASE FILES  |  CASE FILES",
        "header_title": "1991 'GOOD GUYS!' SWAT RAID",
        "header_sub": "APRIL 4, 1991  •  41 HOSTAGES  •  SACRAMENTO, CA",
        "telestration": {"x": 260, "y": 520, "w": 560, "h": 480, "label": "HOSTAGES INSIDE GLASS DOORS"},
        "thumb_hook_top": "41 HOSTAGES HELD INSIDE",
        "thumb_hook_main": "LIVE 1991 SWAT BREACH",
        "thumb_circle": (640, 360, 185),
        "thumb_seg_idx": 1,
        "thumb_offset_sec": 8.0,
        "thumb_ts": 38.0,
        "thumb_focus_y": 0.45,
        "thumb_tc": "TC 04:04:91:21",
        "thumb_hook": "41 HOSTAGES",
        "thumb_hook_rgb": (255, 220, 0),
        "out_name": "UCF_02_1991_Sacramento_Good_Guys_Hostage_SWAT_Raid_5994fps.mp4",
        "narration": (
            "April fourth, 1991. Four heavily armed gunmen walk into a Good Guys electronics store in "
            "Sacramento and take forty-one people hostage—one of the largest hostage standoffs in American "
            "history. Found hidden inside an unlabeled reporter tape, our night cameras zoomed in on "
            "hostages tied together right behind the glass front doors, moments before Sacramento Sheriff "
            "SWAT teams detonated flashbangs and stormed the entrance in a cloud of smoke."
        ),
        "segments": [
            {
                "drive_id": "1BFP3N8xKoHMYjOP9ihmerE7nafQQQSiU",
                "raw_name": "FOR_AMY_2__TERI_7037733.mov",
                "ss": 156.0,
                "t": 15.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1BFP3N8xKoHMYjOP9ihmerE7nafQQQSiU",
                "raw_name": "FOR_AMY_2__TERI_7037733.mov",
                "ss": 220.0,
                "t": 18.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1BFP3N8xKoHMYjOP9ihmerE7nafQQQSiU",
                "raw_name": "FOR_AMY_2__TERI_7037733.mov",
                "ss": 26.0,
                "t": 12.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "UCF_03",
        "brand": "Unaired Case Files",
        "voice": "en-US-ChristopherNeural",
        "accent_hex": "EF4444",
        "accent_rgb": (239, 68, 68),
        "accent_ass": "&H004444EF",
        "sub_hex": "EAB308",
        "badge_text": "UNAIRED CASE FILES  |  CASE FILES",
        "header_title": "2002 JANE DOE CLAY RECONSTRUCTION",
        "header_sub": "JAN 2002  •  UNSOLVED HOMICIDE  •  2VUY MASTER",
        "telestration": {"x": 280, "y": 510, "w": 500, "h": 480, "label": "CRIME SCENE DUMPSTER RECOVERY"},
        "thumb_hook_top": "UNSOLVED 2002 COLD CASE",
        "thumb_hook_main": "FORENSIC CLAY FACE",
        "thumb_circle": (740, 360, 175),
        "thumb_seg_idx": 2,
        "thumb_offset_sec": 6.0,
        "thumb_ts": 12.0,
        "thumb_focus_y": 0.42,
        "thumb_tc": "TC 01:19:02:14",
        "thumb_hook": "JANE DOE TAPE",
        "thumb_hook_rgb": (255, 220, 0),
        "out_name": "UCF_03_2002_Jane_Doe_Dumpster_Forensic_Clay_Bust_5994fps.mp4",
        "narration": (
            "January 2002. When a woman's body was discovered inside a commercial dumpster with no "
            "identification and no matching fingerprints, homicide detectives turned to a last-resort "
            "forensic technique. Preserved on an uncompressed studio master tape, watch a forensic sculptor "
            "build a lifelike clay reconstruction directly over the victim's skull structure, before "
            "investigators morphed the sculpture into a composite photograph hoping someone watching "
            "at home would recognize her face."
        ),
        "segments": [
            {
                "drive_id": "15wtFghVlNPq75Gv3i-wmY9aRCELxufPT",
                "raw_name": "FOR_AMY_2__Facial_reconstruction_6448778.mov",
                "ss": 13.0,
                "t": 15.0,
                "keep_raw": True,
            },
            {
                "drive_id": "15wtFghVlNPq75Gv3i-wmY9aRCELxufPT",
                "raw_name": "FOR_AMY_2__Facial_reconstruction_6448778.mov",
                "ss": 44.0,
                "t": 18.0,
                "keep_raw": True,
            },
            {
                "drive_id": "15wtFghVlNPq75Gv3i-wmY9aRCELxufPT",
                "raw_name": "FOR_AMY_2__Facial_reconstruction_6448778.mov",
                "ss": 84.0,
                "t": 14.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "UCF_04",
        "brand": "Unaired Case Files",
        "voice": "en-US-ChristopherNeural",
        "accent_hex": "EF4444",
        "accent_rgb": (239, 68, 68),
        "accent_ass": "&H004444EF",
        "sub_hex": "EAB308",
        "badge_text": "UNAIRED CASE FILES  |  CASE FILES",
        "header_title": "1999 SYNAGOGUE ARSON TERROR CASE",
        "header_sub": "JUNE 18, 1999  •  DOMESTIC TERROR INVESTIGATION",
        "telestration": {"x": 240, "y": 500, "w": 600, "h": 500, "label": "ACTIVE ARSON SCENE (JUNE 18, 1999)"},
        "thumb_hook_top": "3 SYNAGOGUES FIREBOMBED",
        "thumb_hook_main": "1999 ATF TERROR MANHUNT",
        "thumb_circle": (640, 350, 185),
        "thumb_seg_idx": 1,
        "thumb_offset_sec": 5.0,
        "thumb_ts": 24.0,
        "thumb_focus_y": 0.42,
        "thumb_tc": "TC 06:18:99:03",
        "thumb_hook": "3 ARSON FIRES",
        "thumb_hook_rgb": (255, 220, 0),
        "out_name": "UCF_04_1999_Sacramento_Synagogue_Arson_Terror_Case_5994fps.mp4",
        "narration": (
            "Before dawn on June eighteenth, 1999, three Jewish synagogues across Sacramento were "
            "firebombed in a coordinated domestic terror attack. Our archival cameras captured "
            "firefighters battling the nighttime blaze and the smoke-scarred inscription on the "
            "sanctuary wall reading Love Thy Neighbor As Thyself. Weeks later, federal ATF agents "
            "raided a Northern California property and brought the extremist brothers responsible "
            "into court in handcuffs."
        ),
        "segments": [
            {
                "drive_id": "13OxqgxMhAaZOY6bJA4HEr0x-kU8x2eMq",
                "raw_name": "FOR_KATIE__Synagogue_fire_for_Doug_7856407.mov",
                "ss": 56.0,
                "t": 13.0,
                "keep_raw": True,
            },
            {
                "drive_id": "13OxqgxMhAaZOY6bJA4HEr0x-kU8x2eMq",
                "raw_name": "FOR_KATIE__Synagogue_fire_for_Doug_7856407.mov",
                "ss": 35.0,
                "t": 12.0,
                "keep_raw": False,
            },
            {
                "drive_id": "1Iru6hozKK7epNRTVMs1Ecattn15jCrk_",
                "raw_name": "FOR_KATIE__Synagoge_fire_suspect_for_Doug_7856473.mov",
                "ss": 94.0,
                "t": 10.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1Iru6hozKK7epNRTVMs1Ecattn15jCrk_",
                "raw_name": "FOR_KATIE__Synagoge_fire_suspect_for_Doug_7856473.mov",
                "ss": 38.0,
                "t": 10.0,
                "keep_raw": False,
            },
        ],
    },
    {
        "id": "UCF_05",
        "brand": "Unaired Case Files",
        "voice": "en-US-ChristopherNeural",
        "accent_hex": "EF4444",
        "accent_rgb": (239, 68, 68),
        "accent_ass": "&H004444EF",
        "sub_hex": "EAB308",
        "badge_text": "UNAIRED CASE FILES  |  CASE FILES",
        "header_title": "CALIFORNIA MEGAFIRE VAULT",
        "header_sub": "CARR FIRESTORM  •  DC-10 DROP  •  2.7K PARADISE DRONE",
        "telestration": {"x": 200, "y": 480, "w": 680, "h": 540, "label": "100-FOOT CROWN FIRESTORM WALL"},
        "thumb_hook_top": "100-FT CROWN FIRESTORM",
        "thumb_hook_main": "CA MEGAFIRE VAULT",
        "thumb_circle": (640, 350, 185),
        "thumb_seg_idx": 2,
        "thumb_offset_sec": 5.5,
        "thumb_ts": 28.5,
        "thumb_focus_y": 0.48,
        "thumb_tc": "TC 07:28:18:10",
        "thumb_hook": "DC-10 DROP",
        "thumb_hook_rgb": (255, 220, 0),
        "out_name": "UCF_05_California_Megafire_Carr_Inferno_DC10_Drop_Paradise_Drone_5994fps.mp4",
        "narration": (
            "Raw broadcast and aerial master reels from Northern California's deadliest megafires. "
            "Watch a hundred-foot crown firestorm devouring an entire pine forest on the Carr Fire, "
            "flames engulfing a Napa Valley estate at night, and a top-down helicopter view of a "
            "DC-10 supertanker dropping a river of red retardant across a ridge. Then, see what "
            "remained five days after the 2018 Camp Fire—captured in raw two-point-seven-K drone "
            "footage over the leveled town of Paradise."
        ),
        "segments": [
            {
                "drive_id": "1R-sH0emn3N-iqhtQxpKNKlDbnyLofc-y",
                "raw_name": "NEWS_MEDIA__10PM_CARR_FIRE_UPDATE_VOSIDEBAR_7175744.mov",
                "ss": 12.0,
                "t": 15.0,
                "keep_raw": False,
            },
            {
                "drive_id": "1JbCHTThau814vAAto_WR-cQCCXJHUDZd",
                "raw_name": "NEWS_MEDIA__WILDFIRES_IN_NAPA_COUNTY_VO_2_.mxf_11195761.mov",
                "ss": 4.0,
                "t": 9.0,
                "keep_raw": True,
            },
            {
                "drive_id": "1JbCHTThau814vAAto_WR-cQCCXJHUDZd",
                "raw_name": "NEWS_MEDIA__WILDFIRES_IN_NAPA_COUNTY_VO_2_.mxf_11195761.mov",
                "ss": 42.0,
                "t": 11.0,
                "keep_raw": False,
            },
            {
                "drive_id": "1M1RGpWo7wMpLCg1bFvmZPpo-otnT7vZ8",
                "raw_name": "Old_desktop_stuff__DJI_0013_9223096.MOV",
                "ss": 12.0,
                "t": 13.0,
                "silent_source": True,
                "keep_raw": False,
            },
        ],
    },
]


def run_cmd(cmd, desc):
    print(f"  [*] {desc}...", flush=True)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  [!] FAILED {desc}:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}", flush=True)
        raise RuntimeError(f"Command failed: {desc}")
    return res.stdout


def download_raw(drive_id, raw_name):
    dest = RAW_CACHE / raw_name
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"  [+] Using cached {raw_name} ({dest.stat().st_size / 1e6:.1f} MB)", flush=True)
        return dest
    cmd = [GDRIVE_BIN, "readonly", "download", drive_id, "--out", str(dest)]
    run_cmd(cmd, f"Downloading {raw_name} ({drive_id})")
    return dest


def extract_normalized_segment(raw_path, seg_spec, out_seg_path, audio_bed_path=None):
    """
    Normalizes any archival source (4:3 SD interlaced, 16:9 HD, or 2.7K silent drone)
    into a uniform 1080x810 @ 59.94 fps progressive (bwdif) MP4 with 48kHz stereo audio.
    """
    ss = seg_spec["ss"]
    t = seg_spec["t"]
    crop_pre = seg_spec.get("pre_deinterlaced_crop")
    silent = seg_spec.get("silent_source", False)

    if crop_pre:
        vf = f"{crop_pre},scale=1080:810:flags=lanczos,setsar=1,fps=60000/1001,format=yuv420p"
    else:
        vf = (
            "bwdif=mode=1:parity=-1:deint=0,"
            "scale=1080:810:force_original_aspect_ratio=increase:flags=lanczos,"
            "crop=1080:810,setsar=1,fps=60000/1001,format=yuv420p"
        )

    cmd = [FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(ss), "-t", str(t), "-i", str(raw_path)]
    if silent and audio_bed_path and pathlib.Path(audio_bed_path).exists():
        cmd.extend(["-t", str(t), "-i", str(audio_bed_path)])
        cmd.extend([
            "-vf", vf,
            "-af", "aresample=48000,pan=stereo|c0=c0|c1=c0",
            "-map", "0:v:0", "-map", "1:a:0",
        ])
    elif silent:
        cmd.extend(["-f", "lavfi", "-t", str(t), "-i", "anoisesrc=d=" + str(t) + ":c=brown:r=48000:a=0.015"])
        cmd.extend([
            "-vf", vf,
            "-af", "pan=stereo|c0=c0|c1=c0",
            "-map", "0:v:0", "-map", "1:a:0",
        ])
    else:
        cmd.extend([
            "-vf", vf,
            "-af", "aresample=48000,pan=stereo|c0=c0|c1=c0",
            "-map", "0:v:0", "-map", "0:a:0",
        ])

    cmd.extend([
        "-r", "60000/1001",
        "-c:v", "libx264", "-preset", "Ultrafast", "-crf", "15",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        str(out_seg_path)
    ])
    run_cmd(cmd, f"Extracting normalized segment {out_seg_path.name} (ss={ss}, t={t})")


def generate_vo_and_ass(vid_spec, vo_mp3_path, srt_path, ass_path):
    cmd = [
        sys.executable, "-m", "edge_tts",
        "-v", vid_spec["voice"],
        "--rate", "+6%",
        "-t", vid_spec["narration"],
        "--write-media", str(vo_mp3_path),
        "--write-subtitles", str(srt_path),
    ]
    run_cmd(cmd, f"Generating neural voiceover ({vid_spec['voice']}) for {vid_spec['id']}")

    # Parse SRT and split longer sentences into punchy 4-6 word dynamic caption chunks
    srt_text = srt_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", srt_text.strip())

    def parse_srt_ts(ts_str):
        ts_str = ts_str.strip().replace(",", ".")
        parts = ts_str.split(":")
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    def fmt_ass_ts(sec):
        sec = max(0.0, sec)
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    accent_ass = vid_spec["accent_ass"]
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,Arial,58,&H00FFFFFF,{accent_ass},&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4.5,2.0,2,60,60,360,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    highlight_re = re.compile(
        r"\b(1988|1989|1991|1999|2000|2001|2002|2018|Jordan|Kobe|Bryant|Shaq|Shaquille|Bradshaw|Howie|Puente|SWAT|Jane|Doe|ATF|Paradise|Carr|DC-10|FIFTY|FORTY-ONE)\b",
        re.IGNORECASE
    )

    for b in blocks:
        lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        ts_line = next((ln for ln in lines if "-->" in ln), None)
        if not ts_line:
            continue
        ts_idx = lines.index(ts_line)
        txt = " ".join(lines[ts_idx + 1:])
        t_start_str, t_end_str = ts_line.split("-->")
        t0 = parse_srt_ts(t_start_str)
        t1 = parse_srt_ts(t_end_str)
        dur = max(0.2, t1 - t0)

        words = txt.split()
        if not words:
            continue
        chunk_size = 5
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        total_chars = sum(len(c) for c in chunks) or 1

        cur_t = t0
        for c in chunks:
            c_dur = dur * (len(c) / total_chars)
            c_end = cur_t + c_dur
            styled_c = c.upper()
            styled_c = highlight_re.sub(lambda m: f"{{\\c{accent_ass}}}{m.group(0)}{{\\c&H00FFFFFF&}}", styled_c)
            ass_lines.append(f"Dialogue: 0,{fmt_ass_ts(cur_t)},{fmt_ass_ts(c_end)},Default,,0,0,0,,{styled_c}")
            cur_t = c_end

    ass_path.write_text("\n".join(ass_lines), encoding="utf-8")


def esc_drawtext(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "")


def render_final_short(vid_spec, concat_mp4, vo_mp3, ass_path, out_mp4):
    accent = vid_spec["accent_hex"]
    sub_hex = vid_spec["sub_hex"]
    badge = esc_drawtext(vid_spec["badge_text"])
    title = esc_drawtext(vid_spec["header_title"])
    sub = esc_drawtext(vid_spec["header_sub"])
    tele = vid_spec["telestration"]
    tele_lbl = esc_drawtext(tele["label"])

    # Convert Windows path for FFmpeg subtitles filter: C:/Users/... with escaped colon
    ass_ff_path = str(ass_path).replace("\\", "/").replace(":", "\\:")

    vf = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,"
        "boxblur=10:2,scale=1080:1920,eq=brightness=-0.28:saturation=0.75[bgblur];"
        "[bgblur][fg]overlay=0:420,"
        f"drawbox=x=0:y=414:w=1080:h=6:color=0x{accent}:t=fill,"
        f"drawbox=x=0:y=1230:w=1080:h=6:color=0x{accent}:t=fill,"
        "drawbox=x=40:y=140:w=1000:h=230:color=black@0.82:t=fill,"
        f"drawbox=x=40:y=140:w=12:h=230:color=0x{accent}:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{badge}':fontcolor=0x{accent}:fontsize=28:x=76:y=165,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{title}':fontcolor=white:fontsize=46:x=76:y=212,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{sub}':fontcolor=0x{sub_hex}:fontsize=25:x=76:y=282,"
        f"drawbox=x={tele['x']}:y={tele['y']}:w={tele['w']}:h={tele['h']}:color=0x{accent}@0.92:t=6:enable='between(t,0.2,3.5)',"
        f"drawbox=x={tele['x']}:y={tele['y']-44}:w={tele['w']}:h=44:color=0x{accent}@0.92:t=fill:enable='between(t,0.2,3.5)',"
        f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='{tele_lbl}':fontcolor=black:fontsize=24:x={tele['x']+14}:y={tele['y']-34}:enable='between(t,0.2,3.5)',"
        "drawbox=x=40:y=1255:w=1000:h=52:color=black@0.70:t=fill,"
        f"drawtext=fontfile='C\\:/Windows/Fonts/consolab.ttf':text='59.94 FPS OPTICAL DEINTERLACE  |  ORIGINAL BROADCAST MASTER':fontcolor=0x{accent}:fontsize=24:x=65:y=1270,"
        f"ass='{ass_ff_path}',format=yuv420p[vout]"
    )

    af = (
        "[0:a]volume=0.28[a_orig];"
        "[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume=1.35[a_vo];"
        "[a_orig][a_vo]amix=inputs=2:duration=first:dropout_transition=2:normalize=0,"
        "alimiter=limit=0.95[aout]"
    )

    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(concat_mp4),
        "-i", str(vo_mp3),
        "-filter_complex", vf + ";" + af,
        "-map", "[vout]", "-map", "[aout]",
        "-r", "60000/1001",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    run_cmd(cmd, f"Rendering final narrated 59.94fps Short {out_mp4.name}")


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
    with ZERO artificial contrast/saturation/skin-smoothing filters (Contrast=1.0).
    """
    tmp_jpg = INTER_DIR / f"_tmp_nat_{mp4_path.stem}_{ts_sec:.1f}.jpg"
    cmd = [
        FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error",
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


def apply_vcr_osd_and_corner_hook(canvas, tc_str, hook_text, hook_rgb=(255, 228, 0), sub_mode="PLAY"):
    """
    Applies the authentic 90s Betacam SP / VCR On-Screen Display (OSD) graphics:
    - Top-left: 'PLAY ▶' + 'TC ...' in Lucida Console 44pt with hard black OSD shadow.
    - Bottom-left: 2-3 word max condensed block hook in broadcast yellow with hard black stroke & drop shadow.
    - Zero split-screen lines, zero modern pill badges, unobstructed subject & bottom-right corner clear.
    """
    W, H = canvas.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)

    # Smooth 2D corner cushion (zero hard vertical or horizontal edges)
    for y in range(220):
        ty = 1.0 - (y / 220.0)
        for x in range(560):
            tx = 1.0 - (x / 560.0)
            a = int(115 * ((tx * ty) ** 1.4))
            if a > 0:
                odraw.point((x, y), fill=(0, 0, 0, a))

    # Full-width smooth bottom gradient (bottom 210px)
    for y in range(510, H):
        ty = (y - 510) / (H - 510)
        alpha = int(150 * (ty ** 1.5))
        odraw.line([(0, y), (W, y)], fill=(4, 6, 8, alpha))

    base = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)

    # 1. Top-Left VCR / Betacam OSD ('PLAY ▶' + 'TC ...')
    f_osd = get_font("lucida", 44)
    osd_x, osd_y = 52, 42

    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((osd_x + dx, osd_y + dy), sub_mode, fill=(0, 0, 0, 240), font=f_osd)
    draw.text((osd_x, osd_y), sub_mode, fill=(246, 246, 246, 255), font=f_osd)

    # Geometric VCR Play Triangle ▶
    bbox_play = draw.textbbox((osd_x, osd_y), sub_mode, font=f_osd)
    tri_x = bbox_play[2] + 22
    tri_y = osd_y + 6
    tri_pts_shadow = [(tri_x + 4, tri_y + 4), (tri_x + 4, tri_y + 36), (tri_x + 32, tri_y + 20)]
    tri_pts = [(tri_x, tri_y), (tri_x, tri_y + 32), (tri_x + 28, tri_y + 16)]
    draw.polygon(tri_pts_shadow, fill=(0, 0, 0, 240))
    draw.polygon(tri_pts, fill=(246, 246, 246, 255))

    # Line 2: SMPTE timecode
    tc_y = osd_y + 56
    for dx, dy in [(4, 4), (3, 3), (-2, -2), (2, -2), (-2, 2)]:
        draw.text((osd_x + dx, tc_y + dy), tc_str, fill=(0, 0, 0, 240), font=f_osd)
    draw.text((osd_x, tc_y), tc_str, fill=(246, 246, 246, 255), font=f_osd)

    # 2. Bottom-Left 2-3 Word Condensed Block Hook
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
    # Main condensed yellow block text with crisp black outline
    draw.text(
        (hx, hy),
        hook_text,
        fill=hook_rgb + (255,),
        font=f_hook,
        stroke_width=6,
        stroke_fill=(0, 0, 0, 255),
    )

    return base.convert("RGB")


def generate_thumbnails(vid_spec, final_short_path, yt_thumb_path, vert_cover_path):
    ts = vid_spec.get("thumb_ts", vid_spec.get("thumb_offset_sec", 5.0))
    fy = vid_spec.get("thumb_focus_y", 0.38)
    tc = vid_spec.get("thumb_tc", "TC 00:00:00:00")
    hook = vid_spec.get("thumb_hook", vid_spec.get("thumb_hook_main", "UNAIRED"))
    hook_rgb = vid_spec.get("thumb_hook_rgb", (255, 228, 0) if vid_spec["brand"] == "Deadstock Tapes" else (255, 220, 0))

    # 1. Generate 1280x720 YouTube Thumbnail (100% natural gamma broadcast still)
    frame = extract_natural_full_frame_16x9(final_short_path, ts, focus_y=fy)
    thumb = apply_vcr_osd_and_corner_hook(frame, tc, hook, hook_rgb=hook_rgb)
    thumb.save(yt_thumb_path, quality=95)

    # Sync to repository assets/thumbnails directory
    repo_thumb_dir = THUMB_DT_DIR if vid_spec["brand"] == "Deadstock Tapes" else THUMB_UCF_DIR
    shutil.copy2(yt_thumb_path, repo_thumb_dir / yt_thumb_path.name)

    # 2. Extract 1080x1920 Vertical Cover directly from rendered Short at t=2.0s
    cmd2 = [
        FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", "2.0", "-i", str(final_short_path),
        "-frames:v", "1", "-q:v", "2",
        str(vert_cover_path),
    ]
    run_cmd(cmd2, f"Extracting 1080x1920 Vertical Cover for {vid_spec['id']}")
    shutil.copy2(vert_cover_path, repo_thumb_dir / vert_cover_path.name)


def load_manifest_titles():
    manifest_p = REPO_ROOT / "catalog" / "launch_wave1_manifest.json"
    titles = {}
    if manifest_p.exists():
        try:
            data = json.loads(manifest_p.read_text(encoding="utf-8"))
            for item in data:
                titles[item["id"]] = item.get("title", "")
        except Exception:
            pass
    return titles


def main():
    import argparse
    parser = argparse.ArgumentParser(description="FOX40 Broadcast Archive - Wave 1 Video & Thumbnail Pipeline")
    parser.add_argument("--force", action="store_true", help="Force re-rendering even if output exists")
    parser.add_argument("--thumbs-only", action="store_true", help="Regenerate only thumbnails and vertical covers")
    parser.add_argument("--video", type=str, default=None, help="Process single video ID or comma-separated list (e.g. MTV_01 or MTV_01,MTV_02)")
    parser.add_argument("--channel", type=str, default=None, help="Filter by channel: 1, 2, 'deadstock', or 'casefiles'")
    args = parser.parse_args()

    t_start = time.time()
    canonical_titles = load_manifest_titles()

    video_filter = None
    if args.video:
        video_filter = {x.strip().upper() for x in args.video.split(",") if x.strip()}

    def matches_target(v):
        if video_filter and v["id"].upper() not in video_filter:
            return False
        if args.channel:
            c = str(args.channel).lower()
            if c in ("1", "deadstock", "deadstock_tapes"):
                if v["brand"] not in ("Deadstock Tapes", "Master Tape Vault"):
                    return False
            elif c in ("2", "casefiles", "unaired_case_files"):
                if v["brand"] != "Unaired Case Files":
                    return False
        return True

    target_videos = [v for v in VIDEOS if matches_target(v)]

    # Load existing manifest so partial runs preserve entries for all 10 videos
    manifest_dict = {}
    manifest_p = OUT_ROOT / "launch_wave1_manifest.json"
    if manifest_p.exists():
        try:
            for item in json.loads(manifest_p.read_text(encoding="utf-8")):
                manifest_dict[item["id"]] = item
        except Exception:
            pass
    repo_manifest_p = REPO_ROOT / "catalog" / "launch_wave1_manifest.json"
    if repo_manifest_p.exists():
        try:
            for item in json.loads(repo_manifest_p.read_text(encoding="utf-8")):
                if item["id"] not in manifest_dict:
                    manifest_dict[item["id"]] = item
        except Exception:
            pass

    for idx, vid in enumerate(target_videos, 1):
        vid_id = vid["id"]
        print(f"\n==================================================================", flush=True)
        print(f"[{idx}/{len(target_videos)}] PROCESSING {vid_id}: {vid['out_name']}", flush=True)
        print(f"==================================================================", flush=True)

        brand_folder = "01_Master_Tape_Vault_Launch" if vid["brand"] in ("Deadstock Tapes", "Master Tape Vault") else "02_Unaired_Case_Files_Launch"
        dest_dir = OUT_ROOT / brand_folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        out_mp4 = dest_dir / vid["out_name"]
        yt_thumb = dest_dir / f"{vid_id}_YT_Thumb_1280x720.jpg"
        vert_cover = dest_dir / f"{vid_id}_Vertical_Cover_1080x1920.jpg"

        title = canonical_titles.get(vid_id, f"{vid['header_title']} | {vid['badge_text'].split('|')[-1].strip()}")

        if args.thumbs_only:
            if out_mp4.exists():
                generate_thumbnails(vid, out_mp4, yt_thumb, vert_cover)
                print(f"  [+] Regenerated v3 thumbnails for {vid_id}", flush=True)
            manifest_dict[vid_id] = {"id": vid_id, "title": title, "mp4": str(out_mp4), "yt_thumb": str(yt_thumb), "vert_cover": str(vert_cover)}
            continue

        if not args.force and out_mp4.exists() and out_mp4.stat().st_size > 1_000_000 and yt_thumb.exists():
            print(f"  [+] {out_mp4.name} already built ({out_mp4.stat().st_size / 1e6:.1f} MB), skipping render.", flush=True)
            manifest_dict[vid_id] = {"id": vid_id, "title": title, "mp4": str(out_mp4), "yt_thumb": str(yt_thumb), "vert_cover": str(vert_cover)}
            continue

        if args.force:
            for p in (INTER_DIR / f"{vid_id}_vo.mp3", INTER_DIR / f"{vid_id}_vo.srt", INTER_DIR / f"{vid_id}_captions.ass", INTER_DIR / f"{vid_id}_concat_raw.mp4", INTER_DIR / f"{vid_id}_concat.txt"):
                p.unlink(missing_ok=True)

        # 1. Extract normalized segments
        seg_files = []
        for s_i, seg in enumerate(vid["segments"]):
            seg_out = INTER_DIR / f"{vid_id}_seg_{s_i:02d}.mp4"
            if not (seg_out.exists() and seg_out.stat().st_size > 100_000):
                raw_path = download_raw(seg["drive_id"], seg["raw_name"])
                audio_bed = seg_files[0] if (seg.get("silent_source") and seg_files) else None
                extract_normalized_segment(raw_path, seg, seg_out, audio_bed_path=audio_bed)
                if not seg.get("keep_raw", False):
                    try:
                        raw_path.unlink(missing_ok=True)
                        print(f"  [-] Deleted raw cache {raw_path.name} to free disk space.", flush=True)
                    except Exception:
                        pass
            seg_files.append(seg_out)

        # 2. Concatenate normalized segments
        concat_list_txt = INTER_DIR / f"{vid_id}_concat.txt"
        concat_list_txt.write_text(
            "\n".join(f"file '{str(p).replace(chr(92), '/')}'" for p in seg_files),
            encoding="utf-8"
        )
        concat_mp4 = INTER_DIR / f"{vid_id}_concat_raw.mp4"
        cmd_concat = [
            FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list_txt),
            "-c", "copy", str(concat_mp4)
        ]
        run_cmd(cmd_concat, f"Concatenating {len(seg_files)} segments for {vid_id}")

        # 3. Generate neural documentary voiceover + dynamic ASS captions
        vo_mp3 = INTER_DIR / f"{vid_id}_vo.mp3"
        vo_srt = INTER_DIR / f"{vid_id}_vo.srt"
        vo_ass = INTER_DIR / f"{vid_id}_captions.ass"
        generate_vo_and_ass(vid, vo_mp3, vo_srt, vo_ass)

        # 4. Render final 1080x1920 @ 59.94 fps Short
        render_final_short(vid, concat_mp4, vo_mp3, vo_ass, out_mp4)

        # 5. Generate YouTube 1280x720 Thumbnail & 1080x1920 Vertical Cover
        generate_thumbnails(vid, out_mp4, yt_thumb, vert_cover)

        print(f"  [SUCCESS] {out_mp4.name} ({out_mp4.stat().st_size / 1e6:.2f} MB) + Thumbnails ready!", flush=True)
        manifest_dict[vid_id] = {"id": vid_id, "title": title, "mp4": str(out_mp4), "yt_thumb": str(yt_thumb), "vert_cover": str(vert_cover)}

    final_manifest = [manifest_dict[v["id"]] for v in VIDEOS if v["id"] in manifest_dict]
    manifest_json = json.dumps(final_manifest, indent=2) + "\n"
    (OUT_ROOT / "launch_wave1_manifest.json").write_text(manifest_json, encoding="utf-8")
    (REPO_ROOT / "catalog" / "launch_wave1_manifest.json").write_text(manifest_json, encoding="utf-8")
    print(f"\nAll {len(final_manifest)} Launch Wave 1 videos & thumbnails tracked in manifest (built in {(time.time() - t_start)/60:.1f} minutes)!", flush=True)


if __name__ == "__main__":
    main()

