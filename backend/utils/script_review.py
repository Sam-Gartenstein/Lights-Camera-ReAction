

def validate_episode_outline(client, sitcom_pitch, outline_text):
    """
    Evaluates whether a sitcom pilot episode outline is coherent based on the show pitch.

    Args:
        client: OpenAI client instance.
        sitcom_pitch (str): Sitcom concept including the title and description.
        outline_text (str): The full 20-scene episode outline.

    Returns:
        str: A structured response indicating coherence and a short rationale.

    Raises:
        ValueError: If the API response is empty or improperly formatted.
        Exception: For any other runtime or API-related issues.
    """
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

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            top_p=1,
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error validating episode outline: {str(e)}")
