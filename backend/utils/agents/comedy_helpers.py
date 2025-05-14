
from typing import Dict, List, Tuple

def analyze_and_verify_comedic_consistency(
    client,
    prior_scene_metadata,
    scene_description,
    max_scenes=3
) -> Tuple[bool, str]:
    """
    Analyze comedic tone, verify consistency with prior scenes, and check for overused jokes,
    from the perspective of a professional comedy writer who specializes in punch-up work.

    Args:
        client: OpenAI client instance.
        prior_scene_metadata (List[Dict]): List of scene metadata including summary and running jokes.
        scene_description (str): Description of the current scene.
        max_scenes (int): Number of prior scenes to consider (default = 3).

    Returns:
        Tuple[bool, str]:
            - is_consistent (bool): Whether the new scene aligns with prior comedic tone and jokes.
            - full_analysis_text (str): Structured explanation of tone, consistency, and joke usage.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general runtime or API-related issues.
    """
    try:
        # Pull prior summaries and recurring jokes
        relevant_summaries = [meta["summary"] for meta in prior_scene_metadata][-max_scenes:]
        prior_running_gags = []
        for meta in prior_scene_metadata[-max_scenes:]:
            prior_running_gags.extend(meta.get("recurring_joke", []))

        prior_summary_text = "\n".join(relevant_summaries)
        prior_gags_text = ", ".join(prior_running_gags) if prior_running_gags else "None"

        prompt = f"""
You are a professional comedy writer who specializes in punch-up work for sitcoms.

Your job is to ensure that the comedic tone remains consistent across scenes and that recurring jokes are used effectively without becoming stale.

Previous Scenes Summaries:
{prior_summary_text}

Previous Running Jokes:
{prior_gags_text}

Current Scene Description:
{scene_description}

Tasks:
1. Identify the dominant comedic tone in the new scene.
2. Verify if the tone and humor are consistent with prior scenes.
3. Check if any running jokes are being overused (appearing too often without variation).
4. If there are inconsistencies or overuse issues, explain clearly and suggest how to fix it.

Respond exactly in this format:
1. Detected Tone: [tone]
2. Consistency Verdict (Yes/No)
3. Short Explanation (max 5 lines)
4. Overuse Check: [None / Overused Joke(s): list]
5. Specific Suggestions if inconsistencies or overuse exist
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        result = response.choices[0].message.content.strip()
        is_consistent = "yes" in result.lower().split("\n")[1].lower()

        return is_consistent, result

    except Exception as e:
        raise Exception(f"Error analyzing comedic consistency: {str(e)}")


def recommend_comedic_improvements(
    client,
    scene_description,
    is_consistent=True,
    consistency_result=""
) -> str:
    """
    Suggests two ways to enhance humor naturally for a given scene.
    If the scene is flagged as tonally inconsistent, suggestions may focus on fixing tone issues.

    Args:
        client: OpenAI client instance.
        scene_description (str): The full description of the scene to improve.
        is_consistent (bool): Whether the scene passed the comedic tone check.
        consistency_result (str): Explanation of tonal inconsistency, if any.

    Returns:
        str: Recommended comedic improvements formatted as two brief suggestions.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general runtime or API-related errors.
    """
    try:
        # Include critique context if the scene was flagged as inconsistent
        consistency_context = (
            f"\n\nNote: The comedic tone in this scene was flagged as inconsistent.\n"
            f"Critique:\n{consistency_result.strip()}\n\n"
            f"Your task is to revise the humor to better align with the prior scenes' tone, while preserving the scene’s intent."
            if not is_consistent else ""
        )

        prompt = f"""
You are the Co-Executive Producer in charge of comedic punch-up for a sitcom writing team.

Your job is to improve scenes by adding natural, grounded humor that fits the characters and tone of the show.
{consistency_context}

Current Scene Description:
{scene_description}

Tasks:
- Suggest 2 realistic, grounded comedic improvements.
- Build on any humorous situations, dialogue quirks, or character behaviors.
- Reinforce light running jokes if appropriate, but avoid overusing them.
- If the scene has tonal issues, your suggestions should help realign it with the intended comedic style.
- Keep suggestions short, sitcom-appropriate (2–3 min scene).

Format:
1. — (justification referencing prior scene(s))
2. — (justification referencing prior scene(s))
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error generating comedic improvement suggestions: {str(e)}")
