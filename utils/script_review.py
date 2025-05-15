
import time

def validate_episode_outline(client, sitcom_pitch, outline_text, model="gpt-4", temperature=0.5, top_p=1.0):
    """
    Evaluates whether a sitcom pilot episode outline is coherent based on the provided show pitch.

    This function uses a structured prompt to assess whether the episode outline fits the tone,
    structure, and premise of the sitcom. It returns a verdict and reasoning formatted as a checklist.
    Includes retry logic to handle temporary API failures.

    Args:
        client: OpenAI client instance.
        sitcom_pitch (str): Sitcom concept including the title and description.
        outline_text (str): The full 20-scene episode outline.
        model (str): OpenAI model to use (default: "gpt-4").
        temperature (float): Sampling temperature for variability (default: 0.5).
        top_p (float): Nucleus sampling cutoff (default: 1.0).

    Returns:
        str: A formatted evaluation with:
            - Coherence verdict ("Yes"/"No")
            - 2–4 bullet points of explanation
            - Optional suggestions if coherence is lacking

    Raises:
        ValueError: If the API response is empty or malformed.
        Exception: If the API fails after 3 attempts or another runtime error occurs.
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
                raise Exception(f"Error validating episode outline: {str(e)}")
            time.sleep(2 ** attempt)
