# lights-camera-reACTion

1. Generates a Sitcom Concept based off key words (`generate_sitcom_pitch`)
2. Generates an outline via `sitcom_pitch`
3. Validates scene cohesion using `validate_episode_outline`
4. Generates Scene 1
   a. Takes `scene_1_desc` from `extract_scene` function
   b. Takes `sitcom_title` from `extract_title` function
5. Edits the script via `edit_scene_script`
6. Gets the scene meta data via `summarize_scene`
7. Adds it to VB via `add_scene_to_vector_db`
8. Generates Scene 2 using the meta stored in the vector_bd with `generate_scene_with_context` function

**TODO**

Implement a ReACT pipeline instead of purely using RAG 
  - ReACT agents Character Consistency, Comedic Consistency, and Enviromental Consisency
    - Each of these would have to take in some sort of metadata and/or scene description of the previous and one to generate to understand and we have it reason to itself why it will generate what it will generate!
-We just need to figure how to do this lol
-We also need to figure out how to add evaluation agents and whether or not it can take in all of the scene script (We will have the perplexity score)
