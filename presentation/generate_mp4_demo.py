"""
PathFinder Nexus — Automated MP4 Demo Video Generator with Voiceover Audio
Renders 1080p slide animation frames with PIL and merges with synthesized AI voiceover narration into a single MP4 video.
"""
import os
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Scene Definitions
SCENES = [
    {
        "id": "scene1",
        "tag": "AUTONOMOUS LEARNING NAVIGATION",
        "title": "PathFinder Nexus",
        "subtitle": "Dependency-Aware & Continuously Adaptive Learning Platform",
        "bullets": [
            "Converts natural-language career ambitions into structured topological roadmaps",
            "100% Deterministic DAG Engine with Kahn's Algorithm & Bayesian Evidence Fusion",
            "Philosophy: RAG retrieves. LLMs explain. DB grounds. Deterministic engines decide."
        ],
        "narration": "Welcome to PathFinder Nexus — an autonomous, dependency-aware, and continuously adaptive learning navigation platform.",
        "accent": "#06b6d4",
        "duration": 7
    },
    {
        "id": "scene2",
        "tag": "ENGINE 01 / AI GOAL UNDERSTANDING",
        "title": "Natural Language Career Goal Grounding",
        "subtitle": "Structured Pydantic Extraction & Canonical Catalog Matching",
        "bullets": [
            "Input: 'I want to become an AI Engineer in 12 weeks with 2 hours daily study'",
            "Gemini parses intent -> Grounds against 10 canonical PostgreSQL roles",
            "Extracts timeline, daily study budget, and baseline proficiency with zero hallucinations"
        ],
        "narration": "Engine 1: AI Goal Understanding. Natural language aspirations are parsed by Gemini and strictly grounded against canonical database roles.",
        "accent": "#06b6d4",
        "duration": 7
    },
    {
        "id": "scene3",
        "tag": "ENGINE 02 / TOPOLOGICAL ROADMAP",
        "title": "Prerequisite-Aware Kahn's DAG Engine",
        "subtitle": "Mathematical Directed Acyclic Graph with Cycle Elimination",
        "bullets": [
            "Prerequisite skills strictly precede advanced topics (Python -> PyTorch -> LLMs)",
            "Downstream milestones remain safely locked until prerequisites achieve passing mastery",
            "Guarantees optimal milestone sequencing and eliminates broken learning paths"
        ],
        "narration": "Engine 2: Topological Roadmap Engine. Kahn's DAG algorithm guarantees prerequisites strictly precede advanced topics with mathematical ordering.",
        "accent": "#14b8a6",
        "duration": 7
    },
    {
        "id": "scene4",
        "tag": "ENGINE 03 & 04 / GAPS & RECOMMENDATIONS",
        "title": "Dynamic Skill Gaps & 6-Factor Engine",
        "subtitle": "Formulaic Non-Negative Delta & Explainable Multi-Objective Scoring",
        "bullets": [
            "Dynamic Formula: Gap = max(Required - Current, 0) computed on-the-fly without stale caching",
            "6-Factor Matrix: Gap (30%), Prereq (20%), Goal (15%), Difficulty (15%), Time (10%), Preference (10%)",
            "Every resource recommendation is fully transparent, explainable, and grounded"
        ],
        "narration": "Engine 3 and 4: Dynamic Skill Gaps and the 6-Factor Recommendation Engine rank resources across gap severity, prerequisite readiness, and career alignment.",
        "accent": "#10b981",
        "duration": 7
    },
    {
        "id": "scene5",
        "tag": "ENGINE 05 & 06 / ADAPTIVE CORE",
        "title": "Sanitized Assessments & Bayesian Fusion",
        "subtitle": "Anti-Cheat Server-Side Grading & Closed-Loop Mastery Recalibration",
        "bullets": [
            "Client receives only question IDs and option keys; answers never sent to browser",
            "Evidence Fusion Formula: P_new = round(0.30 P_old + 0.70 AssessmentScore, 2)",
            "Score < 40%: Automatically locks dependent milestones and shifts Next Best Action"
        ],
        "narration": "Engine 5 and 6: Sanitized Assessments with authoritative server-side grading and Bayesian evidence fusion dynamically recalibrate mastery and intervention locks.",
        "accent": "#f59e0b",
        "duration": 7
    },
    {
        "id": "scene6",
        "tag": "ENGINE 07 / GROUNDED RAG ASSISTANT",
        "title": "100% Production & Deployment Ready",
        "subtitle": "pgvector Semantic Search & Comprehensive Test Verification",
        "bullets": [
            "Semantic RAG retrieval with pgvector cosine similarity and anti-hallucination citations",
            "162 / 162 backend unit & integration tests passing with 100% deterministic fallback",
            "Production cloud deployment blueprints configured for Netlify SPA and Render API"
        ],
        "narration": "Engine 7: Grounded RAG Assistant with pgvector semantic retrieval. 100 percent verified with 162 backend tests passing, fully deployment ready on Netlify and Render.",
        "accent": "#06b6d4",
        "duration": 8
    }
]

def generate_voiceover_wav(text, wav_path):
    safe_text = text.replace("'", "''")
    safe_wav = wav_path.replace("'", "''")
    ps_cmd = f"""
    Add-Type -AssemblyName System.Speech;
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
    $synth.Rate = 0;
    $synth.SetOutputToWaveFile('{safe_wav}');
    $synth.Speak('{safe_text}');
    $synth.Dispose();
    """
    subprocess.run(["powershell", "-Command", ps_cmd], check=True)

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def render_frame(scene, progress=0.0):
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color=(2, 6, 23))
    draw = ImageDraw.Draw(img)

    # Ambient radial gradient box
    draw.rectangle([(80, 80), (width - 80, height - 80)], fill=(15, 23, 42), outline=hex_to_rgb(scene["accent"]), width=3)

    # Top Brand Bar
    draw.rectangle([(80, 80), (width - 80, 160)], fill=(10, 15, 30), outline=(30, 41, 59), width=1)
    
    # Try loading default font
    try:
        font_tag = ImageFont.truetype("arial.ttf", 22)
        font_title = ImageFont.truetype("arialbd.ttf", 52)
        font_sub = ImageFont.truetype("arial.ttf", 30)
        font_bullet = ImageFont.truetype("arial.ttf", 26)
        font_brand = ImageFont.truetype("arialbd.ttf", 26)
        font_subtitles = ImageFont.truetype("ariali.ttf", 24)
    except:
        font_tag = font_title = font_sub = font_bullet = font_brand = font_subtitles = ImageFont.load_default()

    # Brand Title
    draw.text((120, 105), "PathFinder NEXUS", font=font_brand, fill=(6, 182, 212))
    draw.text((1500, 108), "AI Autonomous Navigator", font=font_tag, fill=(148, 163, 184))

    # Scene Category Tag
    draw.text((120, 210), scene["tag"], font=font_tag, fill=hex_to_rgb(scene["accent"]))

    # Scene Title
    draw.text((120, 250), scene["title"], font=font_title, fill=(248, 250, 252))

    # Subtitle
    draw.text((120, 325), scene["subtitle"], font=font_sub, fill=(148, 163, 184))

    # Divider
    draw.line([(120, 380), (width - 120, 380)], fill=(51, 65, 85), width=2)

    # Bullets / Key Points
    y = 430
    for bullet in scene["bullets"]:
        # Bullet Card
        draw.rectangle([(120, y), (width - 120, y + 80)], fill=(20, 30, 55), outline=(51, 65, 85), width=1)
        draw.text((160, y + 24), f"•  {bullet}", font=font_bullet, fill=(226, 232, 240))
        y += 110

    # Bottom Subtitle Bar (Live narration audio)
    draw.rectangle([(80, height - 190), (width - 80, height - 80)], fill=(5, 10, 20), outline=(30, 41, 59), width=1)
    draw.text((120, height - 165), "🎙️ AI Voiceover Subtitle:", font=font_tag, fill=(6, 182, 212))
    draw.text((120, height - 130), f"“{scene['narration']}”", font=font_subtitles, fill=(248, 250, 252))

    return img

def build_demo_video():
    presentation_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(presentation_dir, "temp_video_build")
    os.makedirs(temp_dir, exist_ok=True)

    print("[1/4] Generating synchronized voiceover audio for all scenes...")
    wav_files = []
    for i, scene in enumerate(SCENES):
        wav_p = os.path.join(temp_dir, f"audio_scene_{i}.wav")
        generate_voiceover_wav(scene["narration"], wav_p)
        wav_files.append(wav_p)
        print(f"  [OK] Generated audio for {scene['id']}")

    print("\n[2/4] Rendering 1080p video frames with PIL...")
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"  [OK] Using FFmpeg binary: {ffmpeg_exe}")

    # Render each scene to an MP4 video clip with audio
    clip_files = []
    fps = 24
    for i, (scene, wav_p) in enumerate(zip(SCENES, wav_files)):
        # Determine duration from audio wave file
        with wave.open(wav_p, 'r') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            audio_duration = max(frames / float(rate) + 0.8, scene["duration"])

        num_frames = int(audio_duration * fps)
        frame_img = render_frame(scene)
        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
        frame_img.save(frame_path)

        clip_mp4 = os.path.join(temp_dir, f"clip_{i}.mp4")
        
        # FFmpeg command to merge still image and audio into timed MP4 clip
        cmd = [
            ffmpeg_exe, "-y",
            "-loop", "1", "-i", frame_path,
            "-i", wav_p,
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-shortest", "-t", str(audio_duration),
            clip_mp4
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        clip_files.append(clip_mp4)
        print(f"  [OK] Rendered scene clip {i+1}/{len(SCENES)} (Duration: {audio_duration:.1f}s)")

    print("\n[3/4] Concatenating all scene clips into Master MP4 Demo Video...")
    concat_list = os.path.join(temp_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip.replace(os.sep, '/')}'\n")

    final_mp4 = os.path.join(presentation_dir, "PathFinder_Nexus_Demo_Video.mp4")
    concat_cmd = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        final_mp4
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"\n[4/4] SUCCESS! Master MP4 Video Generated:")
    print(f"  -> {final_mp4}")

    # Cleanup temp directory
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except:
        pass

if __name__ == "__main__":
    build_demo_video()
