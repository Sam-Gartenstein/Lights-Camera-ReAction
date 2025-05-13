
from typing import Dict, List, Tuple


def characters_extraction(
    client,
    scene_description: str,
    prior_scene_metadata: List[Dict],
    scene_number: int = None,
    num_scenes: int = 3
) -> Dict[str, List[str]]:
    """
    Extracts characters from previous scenes and the current scene description,
    and identifies former characters along with the scene numbers in which they appeared.

    Returns:
        Dictionary with:
            - 'prior_characters': list of characters from prior scenes
            - 'current_scene_characters': list of characters in the new scene
            - 'new_characters': list of newly introduced characters
            - 'former_characters': list of characters with prior scene numbers
            - 'scene_number': current scene number

    Raises:
        ValueError: If the API response is malformed or missing expected sections.
        Exception: For any other API or runtime error.
    """
    try:
        # Filter to last `num_scenes` prior scenes
        recent_scenes = prior_scene_metadata[-num_scenes:]

        # Map prior character appearances by scene number
        character_scene_map = {}
        for meta in recent_scenes:
            for char in meta.get("characters", []):
                character_scene_map.setdefault(char, []).append(meta.get("scene_number", "?"))

        prior_characters = set(character_scene_map.keys())
        prior_characters_text = ", ".join(sorted(prior_characters)) if prior_characters else "None"

        # Build prompt
        prompt = f"""
You are the Writers' Assistant on the sitcom writing team.

Previously established characters: {prior_characters_text}

Given the following new scene description, identify:
1. All characters involved in the scene.
2. Which characters are NEW (not listed among previously established characters).
3. Which characters are NOT in this scene but appeared in the last {num_scenes} scenes.
   List their names and the scene numbers they appeared in. Example format:
   Former Characters: [Rhea (3, 4, 5), Felix (5)]

Scene Description:
{scene_description}

Respond exactly in this format:
Characters: [comma-separated list]
New Characters: [comma-separated list]
Former Characters: [comma-separated list with scene numbers]
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        result = response.choices[0].message.content.strip()

        # Parse output
        current_scene_characters = []
        new_characters = []
        former_characters = []

        for line in result.split("\n"):
            if line.strip().startswith("Characters:"):
                chars_text = line.split(":", 1)[1].strip().strip("[]")
                current_scene_characters = [char.strip() for char in chars_text.split(",") if char.strip()]
            elif line.strip().startswith("New Characters:"):
                new_chars_text = line.split(":", 1)[1].strip().strip("[]")
                new_characters = [char.strip() for char in new_chars_text.split(",") if char.strip()]
            elif line.strip().startswith("Former Characters:"):
                former_chars_text = line.split(":", 1)[1].strip().strip("[]")
                former_characters = [char.strip() for char in former_chars_text.split(",") if char.strip()]

        return {
            "prior_characters": sorted(list(prior_characters)),
            "current_scene_characters": current_scene_characters,
            "new_characters": new_characters,
            "former_characters": former_characters,
            "scene_number": scene_number
        }

    except Exception as e:
        raise Exception(f"Error extracting characters for Scene {scene_number}: {str(e)}")


def retrieve_character_history(
    client,
    character: str,
    vector_metadata: List[Dict],
    current_scene_description: str,
    num_scenes: int = 1
) -> Dict:
    """
    Retrieves or builds a character history using prior scenes or the current scene.

    Args:
        client: OpenAI client.
        character: Character name to track.
        vector_metadata: List of prior scene metadata.
        current_scene_description: Current scene description.
        num_scenes: Number of scenes to use for reasoning (default = 1).

    Returns:
        Dict with character profile and source summaries:
            - 'character': character name
            - 'profile': full character profile generated from scenes
            - 'source_summaries': list of scene summaries used as input

    Raises:
        ValueError: If the API response is empty or improperly formatted.
        Exception: For general runtime or API-related issues.
    """
    try:
        # Filter scenes where character appears
        relevant_scenes = [meta for meta in vector_metadata if character in meta.get("characters", [])]
        recent_relevant_scenes = relevant_scenes[-num_scenes:]
        relevant_summaries = [scene.get("summary", "") for scene in recent_relevant_scenes]

        if relevant_summaries:
            # Annotate each summary with scene number
            labeled_summaries = "\n\n".join([
                f"Scene {scene.get('scene_number', '?')}:\n{scene.get('summary', '').strip()}"
                for scene in recent_relevant_scenes
            ])

            prompt = f"""
You are the Script Supervisor on the sitcom writing team.

Based on the following prior scenes, build a detailed and **explicitly grounded** character profile for: {character}

Scenes:
{labeled_summaries}

Your profile must include:
1. Personality traits — derived from specific scenes. Mention which scene they appeared in.
2. Speaking style and quirks — cite scene-based examples.
3. Key relationships — who are they close to or in conflict with? Base this only on interactions in the given scenes.
4. Running jokes or behaviors — describe only if patterns emerge across scenes.
5. Emotional arc — explain how their behavior or role has changed across scenes (reference scene numbers clearly).

Do not invent any traits or backstories not present in the text.
Your output should show clear reasoning based on specific scene descriptions or numbers.
Format clearly.
"""
        else:
            prompt = f"""
You are the Script Supervisor on the sitcom writing team.

There are no previous scenes involving the character {character}.

Here is the current scene description:
{current_scene_description}

Your task:
- Identify personality traits based only on this scene’s behavior or description.
- Note speaking style and quirks if any are evident.
- Mention relationships **only** with characters in this scene.
- Do not make up emotional arcs or traits not found in the text.

If there is not enough evidence for any part, say so directly.
Format clearly and label each section.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError(f"Received an empty or malformed response for character {character}.")

        return {
            "character": character,
            "profile": response.choices[0].message.content.strip(),
            "source_summaries": relevant_summaries
        }

    except Exception as e:
        raise Exception(f"Error retrieving history for character '{character}': {str(e)}")


def verify_character_consistency(
    client,
    character_profiles: Dict[str, Dict],
    scene_description: str,
    num_scenes: int = 1
) -> Tuple[bool, str]:
    """
    Verifies whether the upcoming scene's character actions are consistent with their
    previously established traits and emotional arcs based on the last `num_scenes` scenes.

    Args:
        client: OpenAI client.
        character_profiles: Dictionary mapping character names to a dictionary with:
            - 'profile': Generated character profile text
            - 'source_summaries': List of scene summaries used to build the profile
        scene_description: The planned scene description to evaluate.
        num_scenes: Number of past scenes considered for character context (default = 1).

    Returns:
        Tuple of:
            - Boolean indicating whether the scene is consistent (True) or not (False)
            - Model-generated explanation justifying the decision

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general API or runtime issues.
    """
    try:
        profiles_text = "\n\n".join([
            f"Character: {char}\n{profile_data['profile']}"
            for char, profile_data in character_profiles.items()
        ])

        prompt = f"""
You are the Head Writer on the sitcom writing team.

Character Profiles (from the last {num_scenes} scene{'s' if num_scenes > 1 else ''}):
{profiles_text}

Planned Scene Description:
{scene_description}

Check:
- Is each character behaving consistently with their established personality, emotional arc, and speaking style?
- Are their actions and dialogue logical based on traits or relationships from the last {num_scenes} scene{'s' if num_scenes > 1 else ''}?
- Identify contradictions based strictly on past scenes — not general sitcom logic or assumed character arcs.
- Do not invent missing motivations — point them out instead.

Respond exactly in this format:
1. Consistency Verdict (Yes/No)
2. Short Explanation Why (max 5 lines)
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        result = response.choices[0].message.content.strip()
        is_consistent = "yes" in result.lower().split("\n")[0].lower()

        return is_consistent, result

    except Exception as e:
        raise Exception(f"Error verifying character consistency: {str(e)}")


def recommend_character_interactions(
    client,
    character_profiles,
    scene_description,
    num_scenes=1,
    is_consistent=True,
    consistency_result=""
) -> str:
    """
    Recommends two grounded, meaningful character interactions for the given scene,
    based on the last `num_scenes` scenes — or the current description if it's the first scene.
    If the scene is inconsistent, suggestions may aim to resolve or revise those inconsistencies.

    Args:
        client: OpenAI client.
        character_profiles: Dictionary mapping character names to profiles (built from summaries).
        scene_description: Description of the current scene.
        num_scenes: Number of previous scenes to consider (default = 1).
        is_consistent: Whether the scene passed the character consistency check.
        consistency_result: The LLM’s consistency explanation/suggestions, if inconsistent.

    Returns:
        str: Formatted string with two recommended character interactions.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general runtime or API-related errors.
    """
    try:
        profiles_text = "\n\n".join([
            f"Character: {char}\n{profile_data['profile']}"
            for char, profile_data in character_profiles.items()
        ])

        # Add consistency context if applicable
        consistency_context = (
            f"\n\nNote: The current scene was flagged as inconsistent.\n"
            f"Here is the critique provided:\n{consistency_result.strip()}\n\n"
            f"Use this to help adjust or refine the interactions to improve character alignment."
            if not is_consistent else ""
        )

        prompt = f"""
You are the Co-Executive Producer on the sitcom writing team.

You will suggest **exactly two meaningful character interactions** for the following scene.

Character Profiles (based on {'the prior scene' if num_scenes == 1 else f'the last {num_scenes} scenes'}):
{profiles_text}

Planned Scene Description:
{scene_description}
{consistency_context}

Instructions:
- Recommend two character interactions that reflect what has happened in the {'prior scene' if num_scenes == 1 else f'last {num_scenes} scenes'}.
- Refer explicitly to scene numbers when explaining why an interaction fits.
  Example: "In Scene 2, Jimmy promised to change. This scene builds on that."
- If a character is new or has no past context, use the current scene only.
- If the scene has inconsistencies, your suggestions should help resolve those problems while staying true to the profiles.
- Each recommendation must include a short explanation of **why** it fits, citing specific scenes or behaviors.
- Keep each suggestion concise—around 2–3 sentences—and justify clearly.

Format your response like this:
Interaction Recommendations:
1. [Suggestion] — (justification referencing prior scene(s))
2. [Suggestion] — (justification referencing prior scene(s))
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating character interaction recommendations: {str(e)}")
