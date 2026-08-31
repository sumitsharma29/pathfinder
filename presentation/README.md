# 📊 PathFinder Nexus — Presentation & Demo Video Assets

This folder contains all presentation, viva, and video demo assets for **PathFinder Nexus** in all standard formats.

---

## 📁 Included Presentation & Video Files

| File Name | Format | Description |
| :--- | :--- | :--- |
| **`PathFinder_Nexus_Project_Presentation.pptx`** | **PowerPoint (.pptx)** | 16:9 Widescreen dark-themed presentation (15 slides). Fully editable in **PowerPoint**, **Google Slides**, or **Keynote**. |
| **`PathFinder_Nexus_Project_Presentation.pdf`** | **PDF (.pdf)** | High-resolution 16:9 PDF presentation deck ready for print, viva defense, or full-screen slideshow. |
| **`interactive_video_demo.html`** | **Interactive Video Player** | Animated video demo with **real-time AI voiceover speech narration** (`WebSpeech API`), automated scene transitions, live subtitles, and playback controls. |
| **`DEMO_VIDEO_SCRIPT.md`** | **Voiceover Script** | Second-by-second narration script with visual cues for recording demo videos with audio. |
| **`PathFinder_Nexus_Slides.html`** | **HTML Slides** | Standalone offline interactive slide deck with keyboard arrow navigation. |
| **`PROJECT_PRESENTATION.md`** | **Markdown** | Markdown version of the presentation for documentation or Marp export. |

---

## 🎬 How to Run the Interactive Video Demo with Audio
1. Double-click or open [`interactive_video_demo.html`](file:///c:/Users/sumit/OneDrive/Mini%20Project/path%20finder/presentation/interactive_video_demo.html) in Google Chrome or Microsoft Edge.
2. Click **▶ Play Demo Video**.
3. The video will automatically advance through all 6 core system engines with synchronized spoken audio voiceover and subtitles!
4. *(Optional)* Use Windows Game Bar (`Win + Alt + R`) or OBS Studio to record this screen directly to an MP4 video.

---

## 🛠️ How to Rebuild PPTX / PDF
```bash
# Rebuild PowerPoint presentation
python presentation/generate_pptx.py

# Rebuild PDF presentation
python presentation/generate_pdf.py
```
