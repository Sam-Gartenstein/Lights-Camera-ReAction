
def generate_sitcom_pitch(client, keywords_dict=None):
    """
    Generates an original sitcom pitch using optional user-provided keywords by category.

    Args:
        client: OpenAI client instance.
        keywords_dict (dict of str -> list of str, optional): A dictionary of categorized keywords
            (e.g., {'setting': [...], 'characters': [...], 'themes': [...], 'tone_genre': [...]}).

    Returns:
        str: A 1-paragraph sitcom pitch in the format:
             Title: "<sitcom title>"
             <description>

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For any other runtime or API-related errors.
    """
    idea_string = ""
    if keywords_dict:
        lines = ["\nIncorporate the following elements if relevant:"]
        for category, keywords in keywords_dict.items():
            if keywords:
                lines.append(f"- **{category.capitalize()}**: {', '.join([k.strip() for k in keywords])}")
        idea_string = "\n" + "\n".join(lines)

    prompt = f"""
You are a professional comedy screenwriter.

Generate an original sitcom concept in 1 paragraph.
Be specific about the premise, the main characters and their dynamics,
and the general tone of the show.{idea_string}

The sitcom should be original and feel like it could exist on a major streaming platform.
Avoid copying existing shows directly.

Always follow this exact structure:

Title: "<title of the sitcom in quotation marks>"
<1-paragraph description of the show>
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
        )

        # Validate response structure
        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating sitcom pitch: {str(e)}")


def generate_pilot_episode_outline(client, sitcom_pitch, num_scenes=20):
    """
    Generates a pilot episode outline from a sitcom pitch. The model decides the episode concept and scenes.

    Args:
        client: OpenAI client
        sitcom_pitch (str): Full sitcom pitch, including the title and description.
        num_scenes (int): Approximate number of scenes to include (default = 20)

    Returns:
        str: A formatted pilot episode outline with scene titles and summaries.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For any other runtime or API-related errors.
    """
    prompt = f"""
You are a professional sitcom writer, pitching a new sitcom to your network.

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

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9,
        )

        # Check that response is well-formed
        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating pilot episode outline: {str(e)}")
