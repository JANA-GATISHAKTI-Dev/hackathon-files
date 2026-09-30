"""
Script to generate the official 3-minute executive video demo: JANA_GATISHAKTI_3Min_Demo_Video.mp4
Features:
- High-definition 1280x720 video at 24 fps
- 6 structured scenes covering all UI tabs and breakthroughs
- Pre-composited high-res UI screenshots with high contrast framing
- Real-time animated cursor navigation per scene
- Live HUD telemetry, timecode, and progress bar
- Synchronized subtitles and full voiceover audio narration
- Optimized rendering with OpenCV buffer blitting (<10s generation time)
- Muxed with imageio-ffmpeg static binary
"""

import os
import wave
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

def draw_wrapped_text(draw, text, font, x, y, max_width, fill, line_spacing=4):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    
    cur_y = y
    for line in lines:
        draw.text((x, cur_y), line, fill=fill, font=font)
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        cur_y += h + line_spacing
    return cur_y

def create_demo_video():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "frontend", "static", "images")
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Paths to visual screenshot images
    cover_img_path = os.path.join(img_dir, "cover.jpg")
    wa_img_path = os.path.join(img_dir, "whatsapp_voice.jpg")
    opt_img_path = os.path.join(img_dir, "portfolio_optimization.jpg")
    audit_img_path = os.path.join(img_dir, "audit_sentinel.jpg")

    # Paths to generated wav voiceovers
    scene_audios = [
        os.path.join(img_dir, f"scene{i}.wav") for i in range(1, 7)
    ]

    # Calculate exact durations from wav files
    scene_durations = []
    for aud_path in scene_audios:
        if os.path.exists(aud_path):
            with wave.open(aud_path, 'rb') as wf:
                dur = wf.getnframes() / float(wf.getframerate())
                # Add 0.6s padding between scenes for natural pacing
                scene_durations.append(dur + 0.6)
        else:
            scene_durations.append(31.0)

    total_duration = sum(scene_durations)
    print(f"Total Video Duration: {total_duration:.1f} seconds ({total_duration/60.0:.2f} minutes)")

    # Video parameters
    width, height = 1280, 720
    fps = 24
    temp_video_path = os.path.join(base_dir, "temp_video_no_audio.mp4")
    concat_audio_path = os.path.join(base_dir, "temp_full_audio.wav")
    final_output_path = os.path.join(base_dir, "JANA_GATISHAKTI_3Min_Demo_Video.mp4")
    static_output_path = os.path.join(base_dir, "frontend", "static", "JANA_GATISHAKTI_3Min_Demo_Video.mp4")

    # Font setup
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
        font_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
        font_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
        font_caption = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    except:
        font_title = font_sub = font_body = font_mono = font_caption = ImageFont.load_default()

    # Scene definitions with exact narration text
    scenes = [
        {
            "id": 1,
            "title": "SCENE 01: INTRODUCTION & SOVEREIGN VISION",
            "subtitle": "Track 1: AI for Digital Public Infrastructure • Certified DPGA 9/9 Indicators",
            "img_path": cover_img_path,
            "badge": "SOVEREIGN DPI RAIL",
            "caption": "Welcome to the official demonstration of JANA-GATISHAKTI, an open-source Sovereign Digital Public Infrastructure certified against all 9 DPGA indicators. In traditional public administration, citizen grievances remain trapped in siloed portals while capital budgets are allocated in top-down black boxes. JANA-GATISHAKTI unites vernacular citizen voice, GIS spatial intelligence, and mathematical optimization into one unified platform for equitable nation-building.",
            "cur_start": (300, 200),
            "cur_end": (750, 420)
        },
        {
            "id": 2,
            "title": "SCENE 02: GIS COMMAND COCKPIT & HOTSPOT INSPECTOR",
            "subtitle": "Zero-Key Esri Dark Engine • Uber H3 Hexagonal Grid • LGD Spatial Gazetteers",
            "img_path": cover_img_path,
            "badge": "TAB 1: GIS COCKPIT",
            "caption": "In the GIS Command Cockpit, the dashboard integrates a high-performance, zero-API-key Esri Dark map engine with Uber H3 hexagonal spatial indexing. Notice the live infrastructure deficit overlays across Maharashtra and aspirational districts. When an administrator clicks on the Kasansur cluster in Gadchiroli, the inspector instantly surfaces its canonical Local Government Directory code, deficit severity of 78 percent, and historical grievance records.",
            "cur_start": (420, 260),
            "cur_end": (820, 360)
        },
        {
            "id": 3,
            "title": "SCENE 03: CITIZEN EDGE — WHATSAPP BOT & VERHOEFF PRIVACY",
            "subtitle": "Verified Government WhatsApp Rail • DPDP Act 2023 Compliant In-Memory Redaction",
            "img_path": wa_img_path,
            "badge": "TAB 2: CITIZEN EDGE",
            "caption": "Next, we move to the Citizen Edge interface. Citizens can file grievances via WhatsApp chatbots, voice notes, or web forms in their native languages. Under the Digital Personal Data Protection Act 2023, our system enforces privacy by design. The two-pass Verhoeff algorithm scrubs twelve-digit Aadhaar identifiers and phone numbers in-memory with zero data leakage, while Bhasha-Setu processes vernacular audio with transparent bilingual consent.",
            "cur_start": (280, 280),
            "cur_end": (700, 460)
        },
        {
            "id": 4,
            "title": "SCENE 04: NIVESH-DRISHTI — CAPITAL PROJECT PIPELINE",
            "subtitle": "Bankable Preliminary Project Reports (PPR) • Open Contracting OCDS 1.1 JSON Standard",
            "img_path": opt_img_path,
            "badge": "TAB 3: CAPITAL PIPELINE",
            "caption": "In Tab 3, Nivesh-Drishti translates ground-level distress into institutional capital works. Here, the Kasansur drinking water crisis is automatically formulated into a bankable 14.5 Crore Rupee Jal Jeevan Mission project report, complete with population beneficiaries, technical milestones, and bill of quantities. Every proposal is structured compliant with the Open Contracting Data Standard 1.1 JSON format for public procurement.",
            "cur_start": (350, 220),
            "cur_end": (850, 410)
        },
        {
            "id": 5,
            "title": "SCENE 05: MILP POLICY OPTIMIZER & MATHEMATICAL RIGOR",
            "subtitle": "PuLP-CBC Linear Programming Solver • Aspirational Floor (>=40%) • SC/ST Floor (>=30%)",
            "img_path": opt_img_path,
            "badge": "TAB 4: MILP OPTIMIZER",
            "caption": "Tab 4 showcases the Policy and Capex Optimizer. Rather than relying on non-deterministic generative AI hallucinations, capital allocation is governed by Mixed-Integer Linear Programming using the PuLP and COIN-OR CBC solver. Policy makers can enforce statutory equity floors, guaranteeing that at least 40 percent of capital reaches Aspirational Districts and 30 percent reaches marginalized communities, solved in under 35 milliseconds.",
            "cur_start": (400, 250),
            "cur_end": (760, 440)
        },
        {
            "id": 6,
            "title": "SCENE 06: JAN-PRAMAN — GHOST ASSET SENTINEL & AUDIT LEDGER",
            "subtitle": "Automated Citizen IVR Verification • Fraud Discrepancy Gate • SHA-256 Merkle Ledger",
            "img_path": audit_img_path,
            "badge": "TAB 5: AUDIT SENTINEL",
            "caption": "Finally, Tab 5 features the Jan-Praman Ghost Asset Sentinel. Post-construction verification is automated via AI-driven interactive voice calls to actual village residents. If a contractor reports a completed water pipe but citizens confirm dry taps, a red discrepancy flag automatically blocks payment clearance. Every inspection and decision is permanently committed to an immutable SHA-256 hash-chained audit ledger with verifiable Merkle roots. Thank you for exploring JANA-GATISHAKTI.",
            "cur_start": (320, 230),
            "cur_end": (820, 390)
        }
    ]

    # Preload and resize screenshot images
    target_w, target_h = 1000, 430
    ui_x, ui_y = 140, 120
    loaded_imgs = {}
    for sc in scenes:
        p = sc["img_path"]
        if p not in loaded_imgs:
            if os.path.exists(p):
                im = Image.open(p).convert("RGB")
                # Scale smoothly to target card dimensions
                loaded_imgs[p] = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
            else:
                loaded_imgs[p] = Image.new("RGB", (target_w, target_h), (15, 23, 42))

    # Pre-render base frames for each scene to achieve lightning-fast rendering
    scene_base_bgr = []
    for sc in scenes:
        frame_img = Image.new("RGB", (width, height), (7, 13, 30))
        draw = ImageDraw.Draw(frame_img)

        # 1. Top HUD Header
        draw.rectangle([(0, 0), (width, 52)], fill=(12, 19, 40))
        draw.line([(0, 52), (width, 52)], fill=(56, 189, 248), width=1)

        # Header brand
        draw.text((20, 14), "⚡ JANA-GATISHAKTI | SOVEREIGN PUBLIC INFRASTRUCTURE COMMAND CENTER", fill=(241, 245, 249), font=font_title)
        
        # Live HUD status indicator
        draw.ellipse([(width - 330, 21), (width - 320, 31)], fill=(16, 185, 129))
        draw.text((width - 310, 18), "LIVE DPI NETWORK | 24/7 ACTIVE", fill=(16, 185, 129), font=font_mono)

        # 2. Scene Title & Badge Bar
        draw.rectangle([(20, 62), (width - 20, 108)], fill=(15, 23, 48), outline=(56, 189, 248), width=1)
        draw.text((35, 68), sc["title"], fill=(56, 189, 248), font=font_sub)
        draw.text((35, 88), sc["subtitle"], fill=(148, 163, 184), font=font_mono)

        # Badge Right
        draw.rectangle([(width - 230, 70), (width - 35, 100)], fill=(22, 33, 62), outline=(16, 185, 129), width=1)
        draw.text((width - 215, 76), sc["badge"], fill=(16, 185, 129), font=font_mono)

        # 3. Main Center Display: UI Screenshot with sleek card border
        resized_ui = loaded_imgs[sc["img_path"]]
        draw.rectangle([(ui_x - 3, ui_y - 3), (ui_x + target_w + 3, ui_y + target_h + 3)], fill=(22, 33, 62), outline=(56, 189, 248), width=1)
        frame_img.paste(resized_ui, (ui_x, ui_y))

        # 4. On-Screen Synchronized Subtitles Box
        sub_box_y = 562
        sub_box_h = 120
        draw.rectangle([(50, sub_box_y), (width - 50, sub_box_y + sub_box_h)], fill=(10, 17, 36), outline=(56, 189, 248), width=1)
        draw.rectangle([(50, sub_box_y), (160, sub_box_y + 22)], fill=(56, 189, 248))
        draw.text((58, sub_box_y + 3), "NARRATION", fill=(7, 13, 30), font=font_mono)

        # Render wrapped text inside subtitle box
        draw_wrapped_text(draw, sc["caption"], font_caption, 65, sub_box_y + 28, max_width=1150, fill=(241, 245, 249), line_spacing=4)

        # Convert to BGR for OpenCV blitting
        bgr = cv2.cvtColor(np.array(frame_img), cv2.COLOR_RGB2BGR)
        scene_base_bgr.append(bgr)

    # Initialize OpenCV Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    print(f"Rendering video frames at {fps} FPS across {len(scenes)} scenes...")
    global_frame = 0
    total_frames = int(total_duration * fps)

    # Cursor polygon points relative to (cx, cy)
    cursor_pts_template = np.array([
        [0, 0], [0, 18], [5, 14], [11, 19], [14, 16], [8, 11], [14, 11]
    ], dtype=np.int32)

    for sc_idx, sc in enumerate(scenes):
        duration = scene_durations[sc_idx]
        num_frames = int(duration * fps)
        base_bgr = scene_base_bgr[sc_idx]
        cur_x0, cur_y0 = sc["cur_start"]
        cur_x1, cur_y1 = sc["cur_end"]

        for f in range(num_frames):
            global_frame += 1
            progress_ratio = global_frame / float(total_frames)
            scene_progress = f / float(num_frames)

            # Fast buffer copy of pre-rendered base
            frame = base_bgr.copy()

            # Animated Cursor
            cx = int(cur_x0 + (cur_x1 - cur_x0) * scene_progress)
            cy = int(cur_y0 + (cur_y1 - cur_y0) * scene_progress)
            cur_pts = cursor_pts_template + [cx, cy]
            cv2.fillPoly(frame, [cur_pts], (255, 255, 255))
            cv2.polylines(frame, [cur_pts], isClosed=True, color=(15, 23, 42), thickness=1)

            # Bottom Progress Bar
            cv2.rectangle(frame, (0, height - 26), (width, height), (40, 19, 12), -1)
            prog_w = int(width * progress_ratio)
            cv2.rectangle(frame, (0, height - 26), (prog_w, height), (248, 189, 56), -1)

            # Timecode display
            elapsed_sec = int(global_frame / fps)
            cur_min = elapsed_sec // 60
            cur_sec = elapsed_sec % 60
            tot_min = int(total_duration) // 60
            tot_sec = int(total_duration) % 60
            time_str = f"{cur_min:02d}:{cur_sec:02d} / {tot_min:02d}:{tot_sec:02d}"
            cv2.putText(frame, time_str, (width - 150, height - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (241, 245, 249), 1, cv2.LINE_AA)

            out.write(frame)

        print(f"Scene {sc['id']}/6 rendered ({num_frames} frames)...")

    out.release()
    print("Video frame rendering completed successfully!")

    # Step 2: Concatenate all scene wav files into one continuous audio track
    print("Concatenating audio tracks...")
    wav_handles = [wave.open(aud_path, 'rb') for aud_path in scene_audios if os.path.exists(aud_path)]
    if wav_handles:
        params = wav_handles[0].getparams()
        with wave.open(concat_audio_path, 'wb') as outfile:
            outfile.setparams(params)
            for i, wh in enumerate(wav_handles):
                outfile.writeframes(wh.readframes(wh.getnframes()))
                # Add 0.6 second silence between tracks
                silence_frames = int(params.framerate * 0.6)
                outfile.writeframes(b'\x00' * (silence_frames * params.nchannels * params.sampwidth))
                wh.close()

    # Step 3: Mux video and audio using imageio_ffmpeg
    print(f"Muxing video with audio using FFmpeg: {ffmpeg_exe}...")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", temp_video_path,
        "-i", concat_audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output_path
    ]
    subprocess.run(cmd, check=True)

    # Also copy to static folder for direct browser playback & download
    if os.path.exists(final_output_path):
        import shutil
        shutil.copy2(final_output_path, static_output_path)
        file_size_mb = os.path.getsize(final_output_path) / (1024 * 1024)
        print(f"SUCCESS! 3-minute video demo created ({file_size_mb:.2f} MB):\n  {final_output_path}\n  {static_output_path}")

        # Cleanup temp files
        if os.path.exists(temp_video_path): os.remove(temp_video_path)
        if os.path.exists(concat_audio_path): os.remove(concat_audio_path)

if __name__ == "__main__":
    create_demo_video()
