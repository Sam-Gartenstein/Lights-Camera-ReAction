# 🎬 Lights, Camera, ReAction Functions

This notebook builds a full **sitcom script generation pipeline** powered by **ReAct-based agents** — a powerful framework that combines **reasoning** (thinking through a problem) with **acting** (taking structured steps).

We start by **generating a sitcom concept** from creative keywords, then **outlining** the pilot episode scene-by-scene.  
**Scene 1** is generated directly from the outline to establish the world and tone.  
After that, each new scene is **scripted, reviewed, and improved** using specialized **ReAct agents** — a **Character Agent**, **Comedy Agent**, and **Environment Agent** — that simulate a real sitcom writers' room.

---

✅ **Benefits of using ReAct agents**:

- **More structured and transparent thinking:** Agents reason step-by-step before making edits.
- **Dynamic adaptation:** Agents flexibly plan the next creative moves based on scene history.
- **Better long-term coherence:** Scenes evolve logically, with tracked character growth, running jokes, emotional arcs, and worldbuilding.

---

After generation, each scene is **summarized and stored in a vector database**, enabling fast retrieval of scene metadata for future story planning.  
By combining **structured agent workflows** and **retrieval-augmented memory**, we bring sitcom worlds to life — one coherent, character-driven scene at a time.

## Step-by-Step Guide for Web Application

**Follow these steps to get started and troubleshoot common issues:**

### 1. Clear Installation Instructions
- Clone the repository:
  ```bash
  git clone https://github.com/Sam-Gartenstein/lights-camera-reACTion.git
  cd lights-camera-reACTion
  ```
- Install Python dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- (If using the frontend) Install Node.js dependencies:
  ```bash
  npm install
  ```

### 2. Environment Setup Guide
- Copy the example environment file and add your OpenAI API key:
  ```bash
  cp .env.example .env
  ```
- Edit `.env` and set your `OPENAI_API_KEY`.

### 3. Usage Examples and Demonstrations
- **Run the backend Flask server:**
  ```bash
  cd backend
  python app.py
  ```
- **(Optional) Run the frontend React app:**
  ```bash
  npm start
  ```
- Use the provided Jupyter notebook or API endpoints to generate sitcom concepts, outlines, and scripts.

### 4. Troubleshooting Guide
- **Common issues:**
  - *Module not found*: Ensure all dependencies are installed.
  - *API errors*: Check your OpenAI API key and internet connection.
  - *Port conflicts*: Make sure ports 5000 (backend) and 3000 (frontend) are free.
  - *File not ignored by git*: Double-check your `.gitignore` and use `git rm --cached <file>` if needed.
