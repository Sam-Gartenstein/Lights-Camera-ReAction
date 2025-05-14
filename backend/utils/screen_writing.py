

def generate_scene_1_script(
    client,
    sitcom_title,
    scene_description,
    scene_index,
    rag_context=None
):
    """
    Generates the first sitcom scene script with natural comedic rhythm and logical laugh track placement.
    Includes a numbered heading for the scene using scene_index, but avoids timestamp formatting.

    Args:
        client: OpenAI client instance.
        sitcom_title (str): Title of the sitcom.
        scene_description (str): Short summary of the first scene.
        scene_index (int): Index number of the scene (e.g., 0 for Scene 1).
        rag_context (str, optional): Background information to include in the prompt for continuity or world-building.

    Returns:
        str: The generated sitcom scene script.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For any other runtime or API-related errors.
    """
    context_section = f"\nRelevant background information:\n{rag_context}" if rag_context else ""
    scene_number = scene_index + 1
    scene_header = f"# Scene {scene_number}\n"

    prompt = f"""
You are a professional sitcom scriptwriter.

Sitcom Title: {sitcom_title}
Scene Description: {scene_description}{context_section}

Write the opening scene of the pilot episode as a fully formatted sitcom script.

Formatting Guidelines:
- Begin with a scene heading (e.g., INT. EARL'S LOCKSMITH SHOP – DAY)
- Character names in ALL CAPS
- Dialogue should reflect natural flow and comedic timing
- Stage directions in parentheses
- Use [LAUGH TRACK] sparingly and only where it fits (e.g., punchlines, awkward pauses, physical comedy)
- Place [LAUGH TRACK] no more than 4 to 5 times

Scene Constraints:
- This should be the first scene in the episode
- It should be self-contained and take place in a single location
- The scene should introduce tone, key characters, or comedic premise
- Aim for approximately 50 to 70 total lines (including dialogue, directions, and laugh tracks)
- End the scene cleanly without cinematic transitions like 'Fade out' or location jumps
- The tone and pacing should emerge naturally from the description and any provided context

Only output the script.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return f"{response.choices[0].message.content.strip()}"

    except Exception as e:
        raise Exception(f"Error generating Scene {scene_number} script: {str(e)}")


def generate_scene(
    client,
    scene_plan: str,
    scene_number: int
) -> str:
    """
    Generates a new sitcom scene based on a structured scene plan.

    Args:
        client: OpenAI client for prompting.
        scene_plan: The structured scene plan from the ScenePlannerAgent.
        scene_number: The number for the next scene (e.g., 6 if last scene was 5).

    Returns:
        str: The generated sitcom scene script.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For any runtime or API-related errors.
    """
    prompt = f"""
You are a sitcom scene writer.

Definition:
A sitcom scene is a self-contained 2–3 minute unit of story that:
- Takes place in a single, consistent environment.
- Involves 2–5 characters who advance emotional, comedic, or narrative goals.
- Focuses on dialogue, quick pacing, and situation-based humor.

Scene Plan for Scene {scene_number}:
{scene_plan}

STRICT INSTRUCTIONS:
- Use ONLY the goals and suggestions from the scene plan.
- DO NOT invent new characters, jokes, or settings not in the plan.
- DO NOT use "Fade out", "Fade to black", or any cinematic transitions.
- DO NOT end with a direction like [Scene fades out].
- You MUST include 4–5 [Laugh Track] cues spaced throughout the scene.
- Write 50–70 lines maximum with natural dialogue and actions.
- Ensure the environment remains consistent and reflected in dialogue/props.

Goal:
Write a complete sitcom scene using only the provided goals and suggestions. End the scene with character-driven closure—NOT a cinematic fade.

Now begin writing Scene {scene_number}:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating Scene {scene_number} script: {str(e)}")


def generate_scene_baseline(
    client,
    sitcom_title,
    scene_description,
    previous_scenes=None
):
    """
    Generates a sitcom scene script based on a description and optional prior scenes.

    This is the baseline generation function for sitcom scenes. It produces a complete,
    formatted script using a single prompt without the involvement of specialized agents
    (e.g., comedy, character, or tone agents). The output can be used as a reference point
    for evaluating the impact of multi-agent enhancements or prompt engineering strategies.

    Args:
        client: OpenAI client.
        sitcom_title (str): Title of the sitcom.
        scene_description (str): Short summary of the scene to generate.
        previous_scenes (list of str, optional): Prior scene scripts for continuity.

    Returns:
        str: Generated sitcom scene as a formatted script.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For any runtime or API-related errors.
    """
    if previous_scenes:
        combined_context = "\n\n".join(previous_scenes)
        prior_script_note = f"\nHere are the scripts for the previous scenes:\n{combined_context}\n"
    else:
        prior_script_note = ""

    prompt = f"""
You are a professional sitcom scriptwriter.

Sitcom Title: {sitcom_title}
Scene Description: {scene_description}
{prior_script_note}

Write this scene as a fully formatted sitcom script.

Formatting Rules:
- Start with a scene heading (e.g., INT. EARL'S LOCKSMITH SHOP – DAY)
- Character names in ALL CAPS
- Dialogue with natural comedic rhythm
- Stage directions in parentheses
- Insert [LAUGH TRACK] only where it logically fits (e.g., punchlines, awkward moments, physical comedy)

Constraints:
- Write a single complete scene (no scene cuts or multiple locations)
- Aim for approximately 50 to 70 lines total (dialogue, directions, and laugh tracks)
- Maintain continuity with previous scenes (tone, character dynamics, plot)
- The new scene should logically flow from the last scene provided, as if continuing the episode without abrupt jumps
- Use [LAUGH TRACK] no more than 4 to 5 times in the entire scene, placed only where it makes logical comedic sense
- End the scene cleanly — don’t cut off mid-conversation

Only output the script.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating baseline scene script: {str(e)}")
