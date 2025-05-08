
#from rag_utils import explain_rag_usage
from datetime import timedelta
import numpy as np


def generate_scene_1_script(
    client,
    sitcom_title,
    scene_description,
    scene_index=None,
    rag_context=None,
    line_target=(50, 70),
    average_scene_minutes=2.5
):
    """
    Generates a sitcom scene script with logical laugh tracks, natural tone inferred from the description,
    and optional timestamp headings.
    """
    # Timestamp calculation
    if scene_index is not None:
        start_time = timedelta(minutes=scene_index * average_scene_minutes)
        end_time = timedelta(minutes=(scene_index + 1) * average_scene_minutes)
        timestamp_text = f"# Scene {scene_index + 1} — [{str(start_time)[:-3]}–{str(end_time)[:-3]}]\n"
    else:
        timestamp_text = ""

    # Context block if RAG is provided
    context_section = f"\nRelevant background information:\n{rag_context}" if rag_context else ""
    min_lines, max_lines = line_target

    # Prompt for LLM
    prompt = f"""
You are a professional sitcom scriptwriter.

Sitcom Title: {sitcom_title}
Scene Description: {scene_description}{context_section}

Write this scene as a formatted sitcom script.

Format:
- Scene heading (e.g., INT. EARL'S LOCKSMITH SHOP – DAY)
- Character names in ALL CAPS
- Dialogue written with natural flow and comedic timing
- Stage directions in parentheses
- Include [LAUGH TRACK] only where it makes logical sense based on the rhythm and tone of the scene (e.g., punchlines, awkward silences, physical comedy). Use sparingly.

Constraints:
- Write approximately {min_lines} to {max_lines} total lines (including stage directions, dialogue, and laugh tracks)
- Do not write more than one scene
- Let the tone and pacing emerge naturally from the scene description and context
- Focus on character dynamics and comedic flow

End the scene cleanly without cutting off mid-conversation.
"""

    # Call the API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=1,
    )

    # Post-processing (commented out for now)
    # raw_script = response.choices[0].message.content.strip()
    # lines = [line.strip() for line in raw_script.split("\n") if line.strip()]
    # numbered_script = "\n".join([f"{i+1:>3}. {line}" for i, line in enumerate(lines)])

    # return f"{timestamp_text}\n{numbered_script}"

    # Return raw output
    return f"{timestamp_text}\n{response.choices[0].message.content.strip()}"


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
        - new_scene_description (str)
    """
    prompt = f"""
You are a sitcom scene writer.

Below is the Scene Plan for Scene {scene_number}:

{scene_plan}

Tasks:
- Write a 2–3 minute sitcom scene based on this plan.
- Make sure to hit the specified Character Goals and Comedic Goal.
- Implement the Creative Suggestion naturally in the scene.
- Keep the tone light, funny, and emotionally grounded.
- Focus on dialogue and natural actions between characters.
- Include character names clearly when they speak or act.
- Keep the pacing quick — no more than 50–70 lines.

Start writing the full scene now:
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    new_scene_description = response.choices[0].message.content.strip()
    return new_scene_description
