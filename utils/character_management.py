from typing import Dict, List, Tuple
import numpy as np
import re

def analyze_characters(client, scene_description: str) -> List[str]:
    """
    Analyzes a scene description to identify which characters are involved and what information we need about them.
    Uses ReAct's "Think" step to determine necessary character information.
    """
    prompt = f"""
    Analyze this scene description and identify:
    1. All characters mentioned or implied
    2. What we need to know about each character for this scene
    3. Any potential character interactions that need verification

    Scene Description:
    {scene_description}

    Format your response as:
    Characters: [list of characters]
    Required Info: [list of required information per character]
    Key Interactions: [list of interactions to verify]
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    result = response.choices[0].message.content
    
    # Find the Characters line
    characters_line = None
    for line in result.split("\n"):
        if line.strip().startswith("Characters:"):
            characters_line = line
            break
    
    if not characters_line:
        return []
    
    # Extract the characters list using regex
    characters_text = characters_line.split(":", 1)[1].strip()
    
    # Handle different formats: [char1, char2] or char1, char2
    if characters_text.startswith("[") and characters_text.endswith("]"):
        characters_text = characters_text[1:-1]
    
    # Split by comma and clean up each character name
    characters = [char.strip() for char in characters_text.split(",")]
    
    # Filter out empty strings
    characters = [char for char in characters if char]
    
    return characters

def retrieve_character_history(
    client,
    character: str,
    vector_metadata: List[Dict],
    embedding_model
) -> Dict:
    """
    ReAct's "Act" step: Retrieves and synthesizes character history from previous scenes.
    """
    # Encode character query
    query = f"Character analysis and history for {character}"
    query_embedding = embedding_model.encode(query)

    # Get relevant scenes for this character
    character_scenes = []
    for meta in vector_metadata:
        if character in meta.get("characters", []):
            scene_embedding = embedding_model.encode(meta["summary"])
            similarity = np.dot(query_embedding, scene_embedding)
            character_scenes.append((similarity, meta))
    
    character_scenes.sort(reverse=True)
    relevant_scenes = character_scenes[:3]  # Take top 3 most relevant scenes

    context = "\n".join([scene[1]["summary"] for scene in relevant_scenes])
    
    prompt = f"""
    Based on these previous scenes, provide a comprehensive analysis of the character {character}:
    
    Previous Scenes:
    {context}

    Analyze:
    1. Personality traits shown
    2. Speaking style and mannerisms
    3. Relationships with other characters
    4. Running jokes or recurring behaviors
    5. Character arc progression

    Format as a structured character profile.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return {
        "character": character,
        "profile": response.choices[0].message.content,
        "source_scenes": [scene[1]["summary"] for scene in relevant_scenes]
    }

def verify_character_consistency(
    client,
    character_profiles: Dict,
    scene_description: str
) -> Tuple[bool, str]:
    """
    ReAct's "Observe" step: Verifies if planned character actions align with established traits.
    """
    profiles_text = "\n\n".join([
        f"Character: {char}\n{profile['profile']}"
        for char, profile in character_profiles.items()
    ])

    prompt = f"""
    Verify if this scene's character actions are consistent with their established profiles.

    Character Profiles:
    {profiles_text}

    Planned Scene:
    {scene_description}

    Check for:
    1. Personality consistency
    2. Relationship dynamics
    3. Speech pattern consistency
    4. Character motivation clarity
    5. Arc progression logic

    Provide:
    1. Yes/No consistency verdict
    2. Detailed explanation
    3. Suggestions if inconsistent
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content
    # Extract verdict (you might want to make this more robust)
    is_consistent = "yes" in result.lower().split("\n")[0].lower()
    
    return is_consistent, result

def plan_character_arcs(
    client,
    character_profiles: Dict,
    scene_description: str,
    scene_number: int,
    total_scenes: int = 20
) -> str:
    """
    ReAct's final "Think" step: Plans how characters should develop in this scene.
    """
    profiles_text = "\n\n".join([
        f"Character: {char}\n{profile['profile']}"
        for char, profile in character_profiles.items()
    ])

    prompt = f"""
    Plan character development for scene {scene_number}/{total_scenes}.

    Character Profiles:
    {profiles_text}

    Current Scene Description:
    {scene_description}

    Consider:
    1. Where we are in the episode (scene {scene_number} of {total_scenes})
    2. Each character's arc progression
    3. Relationship development needs
    4. Maintaining established traits while allowing growth
    5. Setup/payoff opportunities

    Provide specific guidance for writing this scene to maintain character consistency
    while advancing their arcs appropriately.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content 