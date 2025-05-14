
from typing import List, Tuple

def analyze_environment(
    client,
    scene_description,
    scene_number
) -> str:
    """
    Analyze the environment and key scenery features from the scene description.

    Args:
        client: OpenAI client instance.
        scene_description (str): Text description of the scene.
        scene_number (int): The index of the scene (for context).

    Returns:
        str: Structured environment analysis including location and key visual/prop elements.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general runtime or API-related errors.
    """
    try:
        prompt = f"""
You are the Writers' Assistant on the sitcom writing team.

Your job is to extract key environmental elements from Scene {scene_number}.

Given the following scene description, identify:
1. The **main environment or location** where the scene takes place.
2. A **comma-separated list of key props, scenery, or environmental features** that are important for the tone, humor, or character action.

Scene Description:
{scene_description}

Respond in this exact format:
Environment: [concise location name]
Key Details: [comma-separated list of props or features]
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError(f"Received an empty or malformed environment response for Scene {scene_number}.")

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"Error analyzing environment for Scene {scene_number}: {str(e)}")


def verify_environment_transition(
    client,
    prior_environments,
    current_environment,
    num_scenes
) -> Tuple[bool, str, str]:
    """
    Verifies whether the transition to the current scene's environment is logical and natural,
    and returns a consistency verdict, explanation, and the original formatted evaluation.

    Args:
        client: OpenAI client instance.
        prior_environments (List[str]): Previously used environments.
        current_environment (str): Environment of the current scene.
        num_scenes (int): Number of prior scenes to consider.

    Returns:
        Tuple:
            - is_consistent (bool): Whether the transition is logical.
            - explanation (str): Brief rationale or suggestion.
            - formatted_output (str): Full text response from the LLM.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general API or runtime errors.
    """
    try:
        prior_env_text = ", ".join(prior_environments[-num_scenes:]) if prior_environments else "None"

        prompt = f"""
You are the Head Writer on the sitcom writing team.

Your task is to evaluate whether the environment change into the current scene makes sense.

Previous Locations (last {num_scenes} scenes):
{prior_env_text}

Current Scene Environment:
{current_environment}

Tasks:
1. Determine whether this transition is logical and believable within the context of the show.
2. If it's not, suggest a short setup or linking action that could help the audience accept the change.

Respond in the following format:

Transition Check:
- Logical Transition? (Yes/No)
- Short Explanation (max 5 lines)
- Suggested Transition Setup (optional)
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            top_p=1
        )

        if not response or not response.choices or not response.choices[0].message.content:
            raise ValueError("Received an empty or malformed response from the API.")

        output = response.choices[0].message.content.strip()

        # Parse consistency verdict
        verdict_line = next((line for line in output.splitlines() if "Logical Transition?" in line), "").lower()
        is_consistent = "yes" in verdict_line

        # Extract explanation
        explanation_start = output.find("Short Explanation:")
        if explanation_start != -1:
            explanation = output[explanation_start:].strip()
        else:
            explanation = "Explanation not found."

        return is_consistent, explanation, output

    except Exception as e:
        raise Exception(f"Error verifying environment transition: {str(e)}")


def suggest_environment_details(
    client,
    environment_analysis,
    transition_check,
    is_consistent
) -> str:
    """
    Suggest small environment and setting details to naturally enhance the next scene.

    Focus on sensory details, props, small setting beats, and smooth transition setups.

    Args:
        client: OpenAI client instance.
        environment_analysis (str): Analysis of the current scene's environment.
        transition_check (str): Evaluation of whether the environment transition makes sense.
        is_consistent (bool): Whether the transition was deemed logical.

    Returns:
        str: Two recommended sensory/environmental enhancements.

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: For general API or runtime errors.
    """
    try:
        consistency_note = (
            "The transition is smooth, so these details should support continuity and tone."
            if is_consistent else
            "The transition is jarring, so use details that subtly reinforce the new setting and ease the audience into it."
        )

        prompt = f"""
You are the Co-Executive Producer on the sitcom writing team.

Environment Analysis:
{environment_analysis}

Transition Check:
{transition_check}

Notes:
{consistency_note}

Tasks:
- Suggest 2 small environment or sensory details that would naturally enhance the next scene.
- Examples: sights, sounds, smells, small props, background actions.
- Focus on realistic, sitcom-appropriate moments (not big changes).
- Keep suggestions light, natural, and funny where appropriate.

Format:
- [Suggestion 1]
- [Suggestion 2]
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
        raise Exception(f"Error generating environment detail suggestions: {str(e)}")
