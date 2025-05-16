# Lights, Camera, ReAction Functions

This repository contains a sitcom script generation pipeline powered by ReAct-based agents, a framework that combines step-by-step reasoning with structured decision-making.

The process begins by generating a sitcom concept from creative keywords. An episode outline is then built scene-by-scene. Scene 1 is scripted directly from the outline to establish the tone and setting. Each subsequent scene is written, reviewed, and refined by a set of ReAct agents acting as a virtual writers' room: a Character Agent, Comedy Agent, and Environment Agent.

The pipeline features structured and transparent decision-making through agent reasoning, dynamic scene generation that adapts to prior character and plot developments, and coherent long-term storytelling with consistent character arcs, emotional continuity, and running jokes.

Each generated scene is summarized and stored in a vector database, enabling fast retrieval of scene metadata to support future episodes and planning. The combination of agent workflows and retrieval-augmented memory ensures consistent, character-driven storytelling from one scene to the next.

---

**Benefits of using ReAct agents**:

- **More structured and transparent thinking:** Agents reason step-by-step before making edits.
- **Dynamic adaptation:** Agents flexibly plan the next creative moves based on scene history.
- **Better long-term coherence:** Scenes evolve logically, with tracked character growth, running jokes, emotional arcs, and worldbuilding.

---

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
