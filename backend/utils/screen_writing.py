
import time

def generate_scene_1_script(client, sitcom_title, scene_description, scene_index, rag_context=None,
                            model="gpt-4", temperature=0.7, top_p=0.9):
    """
    Generates the first scene of a sitcom pilot episode using a scene description
    and optional background context (RAG). Returns a fully formatted script with
    consistent tone, pacing, and comedic rhythm.

    This function constructs a scene specifically for the opening of the episode,
    introducing characters, tone, and premise. It includes retry logic to handle
    transient API failures up to 3 times.

    Args:
        client: OpenAI client instance.
        sitcom_title (str): Title of the sitcom.
        scene_description (str): Short summary of the first scene.
        scene_index (int): Zero-based index of the scene (used to derive scene number).
        rag_context (str, optional): Background information to integrate into the scene.
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature to control creativity (default: 0.7).
        top_p (float): Nucleus sampling parameter for generation (default: 0.9).

    Returns:
        str: Formatted script of the opening scene, prepended with a numbered heading (e.g., "# Scene 1").

    Raises:
        ValueError: If the API response is empty or improperly structured.
        Exception: After 3 failed attempts or other runtime errors.
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

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
            )

            if not response or not response.choices or not response.choices[0].message.content:
                raise ValueError("Received an empty or malformed response from the API.")

            return f"{scene_header}\n{response.choices[0].message.content.strip()}"

        except Exception as e:
            if attempt == 2:
                raise Exception(f"Error generating Scene {scene_number} script: {str(e)}")
            time.sleep(2 ** attempt)


def generate_scene(client, scene_plan, scene_number, model="gpt-4", temperature=0.7, top_p=0.9):
    """
    Generates a sitcom scene script based on a structured scene plan and scene number.

    This function prompts the OpenAI API to produce a formatted scene using only the
    content provided in the scene plan. It includes retry logic to handle transient
    errors and adheres to specific formatting and content constraints to ensure
    sitcom-appropriate structure and tone.

    Args:
        client: OpenAI client instance.
        scene_plan (str): A structured plan outlining the objectives and content of the scene.
        scene_number (int): The numerical index of the scene in the episode (used for labeling).
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature to control creativity (default: 0.7).
        top_p (float): Nucleus sampling parameter (default: 0.9).

    Returns:
        str: A formatted sitcom script for the specified scene.

    Raises:
        ValueError: If the API response is empty or malformed.
        Exception: After 3 failed attempts to complete the request.
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

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
            )

            if not response or not response.choices or not response.choices[0].message.content:
                raise ValueError("Received an empty or malformed response from the API.")

            return response.choices[0].message.content.strip()

        except Exception as e:
            if attempt == 2:
                raise Exception(f"Error generating Scene {scene_number} script: {str(e)}")
            time.sleep(2 ** attempt)


def generate_scene_baseline(client, sitcom_title, scene_description, previous_scenes=None,
                            model="gpt-4", temperature=0.7, top_p=0.9):
    """
    Generates a sitcom scene script using only a description and optional prior scenes
    as context, without the aid of multi-agent prompting.

    This function sends a single structured prompt to the OpenAI API and returns a
    formatted sitcom script that continues the tone and dynamics from previous scenes,
    if provided. Includes retry logic for robust error handling.

    Args:
        client: OpenAI client instance.
        sitcom_title (str): Title of the sitcom.
        scene_description (str): Short description of the scene to be generated.
        previous_scenes (list of str, optional): Prior scene scripts for continuity.
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature (default: 0.7).
        top_p (float): Nucleus sampling parameter (default: 0.9).

    Returns:
        str: Formatted sitcom script for the current scene.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: If the API fails after 3 retry attempts or another runtime error occurs.
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

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=top_p,
            )

            if not response or not response.choices or not response.choices[0].message.content:
                raise ValueError("Received an empty or malformed response from the API.")

            return response.choices[0].message.content.strip()

        except Exception as e:
            if attempt == 2:
                raise Exception(f"Error generating baseline scene script: {str(e)}")
            time.sleep(2 ** attempt)
