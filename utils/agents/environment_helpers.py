
from typing import List, Tuple

def analyze_environment(
    client,
    scene_description: str,
    scene_number: int
) -> str:
    """
    Analyze the environment and key scenery features from the scene description.
    """
    prompt = f"""
You are a sitcom environment analyzer.

Given the following scene description for Scene {scene_number}, identify:
- Main environment or location
- Key props, scenery, or environmental features that are important

Scene Description:
{scene_description}

Format exactly:
Environment: [location]
Key Details: [comma-separated list]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def verify_environment_transition(
    client,
    prior_environments: List[str],
    current_environment: str,
    num_scenes: int
) -> str:
    """
    Verify whether the environment transition is logical based on prior scenes.
    """
    prior_env_text = ", ".join(prior_environments[-num_scenes:]) if prior_environments else "None"

    prompt = f"""
You are a sitcom environment continuity checker.

Previous Locations (last {num_scenes} scenes):
{prior_env_text}

Current Scene Environment:
{current_environment}

Tasks:
- Evaluate if the transition to the current environment feels natural and logical.
- Suggest a possible transition (e.g., ending the last scene with a hint of movement) if needed.
- Be brief and constructive.

Format:
Transition Check:
- Logical Transition? (Yes/No)
- Short Explanation (max 5 lines)
- Suggested Transition Setup (optional)
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def suggest_environment_details(
    client,
    environment_analysis: str,
    transition_check: str
) -> str:
    """
    Suggest small environment and setting details to naturally enhance the next scene.

    Focus on sensory details, props, small setting beats, and smooth transition setups.
    """
    prompt = f"""
You are a sitcom environment details assistant.

Environment Analysis:
{environment_analysis}

Transition Check:
{transition_check}

Tasks:
- Suggest 2–3 small environment or sensory details that would naturally enhance the next scene.
- Examples: sights, sounds, smells, small props, background actions.
- Focus on realistic, sitcom-appropriate moments (not big changes).
- Keep suggestions light, natural, and funny where appropriate.

Format:
Environment Details Suggestions:
- [Suggestion 1]
- [Suggestion 2]
- (optional) [Suggestion 3]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
