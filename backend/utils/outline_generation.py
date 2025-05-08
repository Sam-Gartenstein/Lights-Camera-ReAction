
def generate_sitcom_pitch(client, keywords=None):
    """
    Generates an original sitcom pitch using optional user-provided keywords.

    Args:
        client: OpenAI client instance.
        keywords (list of str, optional): Themes, settings, or elements to include in the pitch.

    Returns:
        str: A 1-paragraph sitcom pitch in the format:
             Title: <sitcom title>
             <description>
    """
    idea_string = ""
    if keywords:
        idea_string = "\n\nIncorporate the following themes, ideas, or settings if relevant:\n" + ", ".join(keywords)

    prompt = f"""
    You are a creative comedy screenwriter.

    Generate an original sitcom concept in 1 paragraph.
    Be specific about the premise, the main characters and their dynamics,
    and the general tone of the show.{idea_string}

    The sitcom should be original and feel like it could exist on a major streaming platform.
    Avoid copying existing shows directly.

    Always follow this structure:
    Title: <title of the sitcom>
    Description <1-paragraph description>
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content.strip()


def generate_pilot_episode_outline(client, sitcom_pitch, num_scenes=20):
    """
    Generates a pilot episode outline from a sitcom pitch. The model decides the episode concept and scenes.

    Args:
        client: OpenAI client
        sitcom_pitch (str): Full sitcom pitch, including the title and description.
        num_scenes (int): Approximate number of scenes to include (default = 20)

    Returns:
        str: A formatted pilot episode outline with scene titles and summaries.
    """
    prompt = f"""
You are a professional sitcom writer.

Here is the pitch for a new sitcom:
{sitcom_pitch}

Write a detailed outline for the **pilot episode** of this sitcom.

First, write a short **Episode Concept** in 1–2 sentences.

Then break the episode into approximately {num_scenes} scenes.

For each scene, use the following format exactly:

Scene <number>: "<Scene Title>" <1–2 sentence description>

Guidelines:
- The scene title should be in quotation marks.
- Each description should include what happens, who is involved, and the tone (e.g., funny, awkward, heartfelt).
- Return only the full pilot episode outline, formatted clearly and consistently as shown.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
