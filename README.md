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




## TODO:

- Add in description of workflow
- Perhaps add in an editor agent that edits the previous scene (We have multiple for planning)
- **IMPORTANT** When creating editor, perhaps move `verify_character_consistency` to an Editor Agent
- Continue to refine Character Agent so it explicitly refers to prior scenes!
- Perhaps make function for adding metadata to vector database
- Make sure the script doesn't have "Fade Out" 

## Plan For Creating Baseline

- Modify Generate Scene Prompt so it just takes in a description and recent scenes
- Depenidng on the max number of tokens the prompt can take in, lets cap it at 3 scenes max
   - First scene takes in description only
   - Scene 2 takes in descreption and Scene 1
   - Scene 3 takes in descreption and Scenes 2 and 1
   - Scene 4 takes in descreption and Scenes 3, 2, and 1 so and so forth
