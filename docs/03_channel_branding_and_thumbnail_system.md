# Channel Branding, Show Franchises & Full-Frame VCR OSD Thumbnail System

## 1. Network Brand Architecture

### Channel 1: **Deadstock Tapes** (`@DeadstockTapes`)
* **Core Concept:** *"Deadstock"* is the sneakerhead term for vintage, unworn, fresh-in-the-box grails. Applied to unaired 1970s–2000s broadcast master tapes, it bridges rare hoops/sports history and vintage sneaker heat without locking the channel out of NFL, MLB, or 90s pop-culture reels.
* **Three Recurring Show Franchises:**
  1. **`B-Roll & Breds`** — Uncut NBA legends (1989 Michael Jordan shootaround) and vintage sneaker culture (Dec 2000 Air Jordan XI / XVI Foot Locker mall riot).
  2. **`The Tunnel Tape`** — Pre-game arena/stadium tunnel walk-ins, locker room scrums (2002 WCF Kobe Bryant & Shaquille O'Neal vs. Sacramento Kings), and dugout access (1988 World Series A's vs. Dodgers).
  3. **`The Raw Feed`** — Unedited studio control-room feeds and off-air moments before commercial cutaways (1990s FOX NFL Sunday off-air tape with Howie Long & Terry Bradshaw).

### Channel 2: **Unaired Case Files** (`@UnairedCaseFiles`)
* **Core Concept:** Declassified broadcast evidence—unedited crime-scene reels, courtroom masters, SWAT standoffs, cold cases, and California megafires restored to `59.94 fps`.

---

## 2. Empirical Findings & Design Rules (Adam's Critique)

### Why v1 & v2 Thumbnails Failed
1. **Uncanny / Synthetic Look on 480i Faces:** Stacking `Contrast(1.24) + Color(1.16) + Sharpness(1.40)` onto an already contrast-boosted MP4 frame and zooming `2.2x` into a narrow vertical split-screen half clipped midtone skin highlights on Kobe Bryant and Terry Bradshaw into posterized, plastic-looking regions.
2. **Interlaced Motion-Blend Artifacts:** Picking an action frame blind (`MTV_05` at `ts=38.0s`) caught two colliding NFL players mid-pan across an interlaced field blend.
3. **40/60 Split-Screen & Border Collision:** Using the same vertical divider line across all thumbnails and letting stacked sans-serif text bleed slightly across the center line created visual tension and wasted the darkened left 40% of the canvas.
4. **Corporate Podcast Pill Badges:** Tiny rounded top-left pills (`FEB 1989 • UNSEEN TAPE`) looked like a modern business explainer template and were illegible on mobile.

### The Permanent v3 Full-Frame VCR OSD Standard
1. **One Full-Frame, Native-Gamma Archival Still (`1280x720`):**
   * Ditch split-screens completely.
   * Inspect a multi-timestamp contact sheet (`assets/mockups/contact_sheet_mtv_candidates.jpg` and `contact_sheet_ucf_candidates.jpg`) at native broadcast gamma (`Contrast=1.0`, `Sharpness=1.0`) and pick the single most compelling stationary or low-motion frame.
2. **Top-Left VCR / Betacam SP On-Screen Display (`PLAY ▶` / `TC ...`):**
   * Crisp white monospace OSD text (`Lucida Console` `44pt`) with a hard black drop shadow and a geometric play triangle `▶`.
3. **Bottom-Left 2–3 Word Max Condensed Block Hook:**
   * Heavy condensed block lettering (`Impact` `118pt`) in classic broadcast yellow (`#FFE400`) with a hard black stroke (`6px`) and offset shadow (`+9px, +9px`), tucked into the bottom-left corner so it never blocks the subject or the bottom-right duration badge.
4. **Channel Page & Banner Rules:**
   * **Spell `DEADSTOCK` as one word** across the crest, banner, title, and `@DeadstockTapes` handle.
   * **Zero Banner Logo Redundancy:** Never repeat the circular crest on the left side of the banner directly above YouTube's circular profile avatar.
   * **Front-Load Titles (`<52 chars`):** Put the star player, sneaker, or case in the first 32 characters and place the show franchise (`| B-Roll & Breds`, `| The Tunnel Tape`, `| The Raw Feed`, `| Case Files`) at the end.
