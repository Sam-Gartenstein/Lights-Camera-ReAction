
from typing import Dict, List, Tuple

def analyze_characters(
    client,
    scene_description: str,
    prior_scene_metadata: List[Dict],
    scene_number: int = None
) -> Dict[str, List[str]]:
    """
    Extracts characters from previous scenes and the current scene description separately.

    Returns:
        Dictionary with:
            - 'prior_characters': list of characters from prior scenes
            - 'current_scene_characters': list of characters in the new scene
            - 'new_characters': list of newly introduced characters
            - 'scene_number': current scene number
    """
    # 1. Extract prior characters
    prior_characters = set()
    for meta in prior_scene_metadata:
        for char in meta.get("characters", []):
            prior_characters.add(char)

    prior_characters_text = ", ".join(sorted(prior_characters)) if prior_characters else "None"

    # 2. Build extraction prompt
    prompt = f"""
You are a sitcom character extraction assistant.

Previously established characters: {prior_characters_text}

Given the following new scene description, identify:
1. All characters involved in the scene.
2. Which characters are NEW (not listed among previously established characters).

Scene Description:
{scene_description}

Format exactly:
Characters: [comma-separated list]
New Characters: [comma-separated list]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    # Parse output
    current_scene_characters = []
    new_characters = []

    for line in result.split("\n"):
        if line.strip().startswith("Characters:"):
            chars_text = line.split(":", 1)[1].strip()
            if chars_text.startswith("[") and chars_text.endswith("]"):
                chars_text = chars_text[1:-1]
            current_scene_characters = [char.strip() for char in chars_text.split(",") if char.strip()]
        elif line.strip().startswith("New Characters:"):
            new_chars_text = line.split(":", 1)[1].strip()
            if new_chars_text.startswith("[") and new_chars_text.endswith("]"):
                new_chars_text = new_chars_text[1:-1]
            new_characters = [char.strip() for char in new_chars_text.split(",") if char.strip()]

    return {
        "prior_characters": sorted(list(prior_characters)),
        "current_scene_characters": current_scene_characters,
        "new_characters": new_characters,
        "scene_number": scene_number
    }


def retrieve_character_history(
    client,
    character: str,
    vector_metadata: List[Dict],
    current_scene_description: str,
    max_scenes: int = 3
) -> Dict:
    """
    Retrieves or responsibly builds character history from prior scenes or current scene description.

    Args:
        client: OpenAI client.
        character: Character name.
        vector_metadata: List of prior scene metadata.
        current_scene_description: Full description of the new scene.
        max_scenes: Maximum number of prior scenes to retrieve (default 3).

    Returns:
        Dict containing character profile and source summaries.
    """
    # Filter scenes where the character is explicitly listed
    relevant_scenes = [meta for meta in vector_metadata if character in meta.get("characters", [])]
    relevant_summaries = [scene["summary"] for scene in relevant_scenes][-max_scenes:]

    if relevant_summaries:
        context = "\n".join(relevant_summaries)
        prompt = f"""
Analyze the following previous scenes to build a full character profile for {character}.

Scenes:
{context}

Profile must cover:
- Personality traits
- Speaking style and quirks
- Key relationships
- Running jokes or behaviors
- Emotional arc so far

Format the profile clearly.
"""
    else:
        prompt = f"""
There are no previous scenes involving the character {character}.

Here is the description of the current scene where {character} appears:
{current_scene_description}

Tasks:
- Extract any clear **personality traits** based only on behavior or description.
- Extract **speaking style and quirks** based only on dialogue or description.
- Extract **relationships only to characters explicitly present in this scene** (no outside inventions).
- DO NOT create emotional arcs.
- DO NOT invent history, backstory, or relationships not supported by the scene.

If there is not enough information, say so explicitly.

Format clearly and label each section.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return {
        "character": character,
        "profile": response.choices[0].message.content.strip(),
        "source_summaries": relevant_summaries
    }


def verify_character_consistency(
    client,
    character_profiles: Dict[str, Dict],
    scene_description: str
) -> Tuple[bool, str]:
    """
    Verifies if the upcoming scene's character actions match established traits.
    """

    profiles_text = "\n\n".join([
        f"Character: {char}\n{profile_data['profile']}"
        for char, profile_data in character_profiles.items()
    ])

    prompt = f"""
You are a sitcom character consistency checker.

Character Profiles:
{profiles_text}

Planned Scene Description:
{scene_description}

Check:
- Is each character behaving consistently with their established profile?
- Are their speaking patterns, emotions, and relationships logical based on their profile?
- Identify any contradictions clearly.

Respond exactly in this format:
1. Consistency Verdict (Yes/No)
2. Short Explanation (max 5 lines)
3. Specific Suggestions if inconsistencies exist
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # deterministic
    )

    result = response.choices[0].message.content.strip()

    # Parse verdict
    is_consistent = "yes" in result.lower().split("\n")[0].lower()

    return is_consistent, result


def recommend_character_interactions(
    client,
    character_profiles: Dict[str, Dict],
    scene_description: str
) -> str:
    """
    Recommends how to maximize character interactions in the given scene, limited to 3–4 realistic suggestions.
    """

    profiles_text = "\n\n".join([
        f"Character: {char}\n{profile_data['profile']}"
        for char, profile_data in character_profiles.items()
    ])

    prompt = f"""
You are a sitcom character interaction enhancement assistant.

Character Profiles:
{profiles_text}

Planned Scene Description:
{scene_description}

Tasks:
- Suggest ways to **maximize character interactions** in this scene.
- Base suggestions strictly on character personalities, relationships, and behavior styles.
- Limit yourself to 3 or 4 **specific, realistic** interaction ideas that would naturally fit within a 2–3 minute sitcom scene.
- Ideas can include banter, conflict, tension, emotional beats, callbacks to running jokes, or character quirks.
- Keep the scene grounded, funny, and emotionally resonant without overcrowding it.

Format:
Interaction Recommendations:
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]
- [Suggestion 4] (optional)
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
