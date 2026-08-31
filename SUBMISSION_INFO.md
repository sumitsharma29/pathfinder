# 📋 PathFinder Nexus — Official Project Submission Information

---

### 1. Source Code (ZIP)
- **File Name**: `PathFinder_Nexus_Source_Code.zip`
- **Location**: In project root directory [`PathFinder_Nexus_Source_Code.zip`](file:///PathFinder_Nexus_Source_Code.zip) (Size: ~2.07 MB)
- **Included**: Complete FastAPI backend, React 18 frontend, PostgreSQL migration/seed scripts, test suites, Render & Netlify deployment configs, and presentation assets (excluding `node_modules` and git clutter).

---

### 2. Source Code Repository (GitHub URL)
- **Repository URL**: `https://github.com/<your-username>/pathfinder-nexus`
- **Push Commands**:
  ```bash
  git add .
  git commit -m "feat: complete PathFinder Nexus submission release"
  git branch -M main
  git remote add origin https://github.com/<your-username>/pathfinder-nexus.git
  git push -u origin main
  ```

---

### 3. Solution Documentation (PDF / PPT)
- **Presentation Deck (PPTX)**: [`presentation/PathFinder_Nexus_Project_Presentation.pptx`](file:///presentation/PathFinder_Nexus_Project_Presentation.pptx) (16:9 Widescreen, 15 Slides)
- **Presentation Document (PDF)**: [`presentation/PathFinder_Nexus_Project_Presentation.pdf`](file:///presentation/PathFinder_Nexus_Project_Presentation.pdf) (High-Res 16:9 Landscape PDF)
- **Architectural Documentation**: [`README.md`](file:///README.md) and [`AI_ARCHITECTURE.md`](file:///AI_ARCHITECTURE.md)

---

### 4. Demo Video URL (3–5 minutes)
- **Generated Offline Video File**: [`presentation/PathFinder_Nexus_Demo_Video.mp4`](file:///presentation/PathFinder_Nexus_Demo_Video.mp4) (Full HD 1080p MP4 with voiceover narration & subtitles)
- **Interactive Player**: [`presentation/interactive_video_demo.html`](file:///presentation/interactive_video_demo.html)
- **YouTube Link**: *(Upload `PathFinder_Nexus_Demo_Video.mp4` to YouTube as Unlisted/Public and paste link below)*
  `https://youtu.be/your-video-id`

---

### 5. Deployed Application URL
- **Frontend SPA (Netlify)**: `https://pathfinder-nexus.netlify.app`
- **Backend API Docs (Render / Swagger)**: `https://pathfinder-nexus-backend.onrender.com/docs`
- **Backend Health Probe**: `https://pathfinder-nexus-backend.onrender.com/health`

---

### 6. Local Setup & Execution Instructions

#### Prerequisites
- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL 16+** (Optional: application includes deterministic fallback mode for offline testing)

#### Step 1: Backend Setup
```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Synchronize database schema and seed canonical catalog
python scripts/deploy_init.py

# 3. Start FastAPI development server
uvicorn backend.app.main:app --reload --port 8000
```
API Swagger documentation is accessible at `http://localhost:8000/docs`.

#### Step 2: Frontend Setup
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite SPA server
npm run dev
```
Open `http://localhost:5173` in your browser.

#### Step 3: Run Automated Test Suite
```bash
# Execute all 162 backend unit and integration tests
pytest

# Verify frontend production build
cd frontend && npm run build
```
