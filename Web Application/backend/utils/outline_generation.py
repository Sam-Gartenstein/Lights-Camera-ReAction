
import time

def generate_sitcom_pitch(client, keywords_dict=None, model="gpt-4", temperature=0.7, top_p=0.9):
    """
    Generates an original sitcom pitch in paragraph form, optionally guided by
    user-provided keywords in categories such as setting, characters, and tone.

    The function sends a structured prompt to the OpenAI API and returns a sitcom
    concept formatted with a title and single-paragraph description. Includes retry
    logic (up to 3 attempts) to handle temporary API failures.

    Args:
        client: OpenAI client instance.
        keywords_dict (dict of str -> list of str, optional): Optional categorized keywords
            to guide generation (e.g., {'setting': [...], 'characters': [...], 'themes': [...]}).
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature for creativity (default: 0.7).
        top_p (float): Nucleus sampling parameter (default: 0.9).

    Returns:
        str: Sitcom pitch in the format:
             Title: "<sitcom title>"
             <1-paragraph description>

    Raises:
        ValueError: If the API response is empty or not formatted correctly.
        Exception: After 3 failed retry attempts or for any runtime error.
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

    max_retries = 3
    for attempt in range(max_retries):
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
            if attempt == max_retries - 1:
                raise Exception(f"Error generating sitcom pitch: {str(e)}")
            time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s


def generate_pilot_episode_outline(client, sitcom_pitch, num_scenes=20, model="gpt-4", temperature=0.7, top_p=0.9):
    """
    Generates a structured pilot episode outline for a sitcom, based on the provided pitch.

    The model is prompted to write a brief episode concept followed by a breakdown
    of approximately `num_scenes` scenes. Each scene includes a title and a concise
    1–2 sentence summary. The function uses retry logic to handle transient API failures.

    Args:
        client: OpenAI client instance.
        sitcom_pitch (str): Full sitcom pitch, including title and paragraph description.
        num_scenes (int): Number of scenes to include in the outline (default: 20).
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature for creative variation (default: 0.7).
        top_p (float): Nucleus sampling parameter (default: 0.9).

    Returns:
        str: The complete episode outline, with the following format:
            - Episode Concept (1–2 sentences)
            - Scene-by-scene breakdown using:
              Scene <number>: "<Title>" <summary>

    Raises:
        ValueError: If the API response is empty or improperly formatted.
        Exception: If all retries fail or another API-related issue occurs.
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

    max_retries = 3
    for attempt in range(max_retries):
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
            if attempt == max_retries - 1:
                raise Exception(f"Error generating pilot episode outline: {str(e)}")
            time.sleep(2 ** attempt)  # Waits 1s, then 2s, then 4s on retries
