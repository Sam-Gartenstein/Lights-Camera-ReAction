
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
