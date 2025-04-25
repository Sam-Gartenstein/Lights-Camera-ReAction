
from datetime import timedelta

def validate_episode_outline(client, sitcom_pitch, outline_text):
    prompt = f"""
You are a veteran sitcom script editor.

Below is a sitcom concept and a 20-scene outline for the pilot episode. Your task is to determine whether the outline is coherent — meaning it fits the premise, has consistent tone, logical character/plot progression, and could realistically work as the structure of an episode.

Return your answer in the following format:

Coherence: [Yes/No]

Reasoning:
- [List 2–4 bullet points explaining your decision]
- If the answer is "No", include suggestions for improving coherence.

Sitcom Pitch:
{sitcom_pitch}

Episode Outline:
{outline_text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()


def edit_scene_script(
    client,
    original_script,
    sitcom_title,
    scene_index=None,
    average_scene_minutes=2.5
):
    """
    Automatically reviews and revises a sitcom scene, and returns both an explanation and the edited script.
    """
    # Scene index formatting
    scene_number = f"Scene {scene_index + 1}" if scene_index is not None else "Scene"

    # Timestamp
    if scene_index is not None:
        start_time = timedelta(minutes=scene_index * average_scene_minutes)
        end_time = timedelta(minutes=(scene_index + 1) * average_scene_minutes)
        timestamp_text = f"# {scene_number} — [{str(start_time)[:-3]}–{str(end_time)[:-3]}]\n"
    else:
        timestamp_text = ""

    # Prompt
    prompt = f"""
You are a sitcom script editor.

Sitcom Title: {sitcom_title}

Review the following scene for the following:
- Tone consistency
- Dialogue pacing and comedic timing
- [LAUGH TRACK] placement and overuse
- Character consistency
- Clarity and engagement

First, list your edits under the heading: **Explanation of Edits:**

Then, print the revised scene under the heading: **{scene_number}:**

Keep the script formatting intact. Revise only what's necessary.

Scene to review and revise:
{original_script}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=1,
    )

    # Final output
    return f"{timestamp_text}\n{response.choices[0].message.content.strip()}"
