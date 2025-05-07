
from typing import Dict, List, Tuple

def analyze_and_verify_comedic_consistency(
    client,
    prior_scene_metadata: List[Dict],
    scene_description: str,
    max_scenes: int = 3
) -> Tuple[bool, str]:
    """
    Analyze comedic tone, verify consistency with prior scenes, and check for overused jokes.

    Returns:
        - is_consistent (bool)
        - full_analysis_text (str)
    """
    # Pull prior summaries and recurring jokes
    relevant_summaries = [meta["summary"] for meta in prior_scene_metadata][-max_scenes:]
    prior_running_gags = []
    for meta in prior_scene_metadata[-max_scenes:]:
        prior_running_gags.extend(meta.get("recurring_joke", []))

    prior_summary_text = "\n".join(relevant_summaries)
    prior_gags_text = ", ".join(prior_running_gags) if prior_running_gags else "None"

    prompt = f"""
You are a sitcom comedic tone analyzer.

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
        temperature=0
    )

    result = response.choices[0].message.content.strip()

    is_consistent = "yes" in result.lower().split("\n")[1].lower()

    return is_consistent, result


def recommend_comedic_improvements(
    client,
    scene_description: str
) -> str:
    """
    Suggests ways to enhance humor naturally based only on the current scene.

    Returns:
        Recommendation text (str)
    """
    prompt = f"""
You are a sitcom humor enhancement assistant.

Current Scene Description:
{scene_description}

Tasks:
- Suggest 3–4 realistic, grounded comedic improvements.
- Build on any humorous situations, dialogue quirks, or character behaviors.
- Reinforce light running jokes if appropriate, but avoid overusing them.
- Keep suggestions short, sitcom-appropriate (2–3 min scene).

Format:
Interaction Recommendations:
- [Suggestion 1]
- [Suggestion 2]
- [Suggestion 3]
- [Suggestion 4] (optional)
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
