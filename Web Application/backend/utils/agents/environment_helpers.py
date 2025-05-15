
from typing import List, Tuple
import time

def analyze_environment(
    client,
    scene_description,
    scene_number
) -> str:
    """
    Analyzes the environment and visual context of a sitcom scene description,
    identifying the primary location and key scenery or prop elements.

    This function prompts the model to extract:
    1. A concise name for the scene's main environment or location.
    2. A comma-separated list of important props, features, or visual details
       that support the scene’s tone, humor, or character interaction.

    The result is returned in a structured format and can be used for production
    design, continuity checking, or worldbuilding agents.

    Includes retry logic (up to 3 attempts with exponential backoff) to handle transient failures.

    Args:
        client: OpenAI client instance.
        scene_description (str): Natural-language description of the scene.
        scene_number (int): Index number of the scene being analyzed.

    Returns:
        str: Structured output in the following format:

            Environment: <concise location name>
            Key Details: <comma-separated list of props or features>

            Example:
            Environment: Locksmith shop
            Key Details: cluttered counter, neon sign, key display wall, squeaky stool

    Raises:
        ValueError: If the API response is empty or malformed.
        Exception: After 3 failed retry attempts or other runtime issues.
    """
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

    for attempt in range(3):
        try:
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
            if attempt == 2:
                raise Exception(f"Error analyzing environment for Scene {scene_number}: {str(e)}")
            time.sleep(2 ** attempt)  # Retry delay: 1s, 2s


def verify_environment_transition(
    client,
    prior_environments,
    current_environment,
    num_scenes
) -> Tuple[bool, str, str]:
    """
    Verifies whether the transition into the current scene's environment is logical
    given the locations used in prior scenes.

    This function prompts the model to assess if the new scene’s setting aligns
    naturally with the recent environmental progression. It flags jarring or
    unexplained transitions and suggests minimal linking setups when needed.

    This is useful for:
    - Ensuring smooth visual and narrative continuity
    - Supporting directing, blocking, or agent-based scene validation
    - Catching unnatural location jumps or scene disconnection

    Includes retry logic (up to 3 attempts with exponential backoff) to ensure robustness.

    Args:
        client: OpenAI client instance.
        prior_environments (List[str]): List of environments from recent scenes.
        current_environment (str): Name of the environment for the current scene.
        num_scenes (int): Number of previous environments to consider for transition logic.

    Returns:
        Tuple[bool, str, str]:
            - is_consistent (bool): True if the transition is logical or appropriately motivated.
            - explanation (str): Short rationale or suggestion, extracted from model response.
            - formatted_output (str): Full structured output from the model, which includes:
                - Logical Transition? (Yes/No)
                - Short Explanation
                - Suggested Transition Setup (if applicable)

    Raises:
        ValueError: If the API response is empty or malformed.
        Exception: After 3 failed retry attempts or other runtime issues.
    """
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

    for attempt in range(3):
        try:
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
            if attempt == 2:
                raise Exception(f"Error verifying environment transition: {str(e)}")
            time.sleep(2 ** attempt)


def suggest_environment_details(
    client,
    environment_analysis,
    transition_check,
    is_consistent
) -> str:
    """
    Suggests small environmental or sensory details to naturally enhance the next scene's setting,
    using analysis of the current location and the logic of the prior environment transition.

    This function prompts the model to generate two grounded, sitcom-appropriate suggestions
    that add depth to the scene through subtle props, background actions, or sensory cues
    (e.g., sound, light, smell). If the transition between scenes is jarring, the suggestions
    aim to smooth that transition; otherwise, they enhance tone and continuity.

    Includes retry logic (up to 3 attempts with exponential backoff) to handle transient failures.

    Args:
        client: OpenAI client instance.
        environment_analysis (str): Structured analysis of the scene’s current environment and features.
        transition_check (str): Full LLM output evaluating whether the environment transition is logical.
        is_consistent (bool): Whether the transition was deemed logical (True) or jarring (False).

    Returns:
        str: A formatted string listing two suggested environmental enhancements in this format:

            Environment Details Suggestions:
            - Suggestion 1
            - Suggestion 2

    Raises:
        ValueError: If the API response is malformed or empty.
        Exception: After 3 failed retry attempts or other runtime issues.
    """
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
Environment Details Suggestions:
- [Suggestion 1]
- [Suggestion 2]
"""

    for attempt in range(3):
        try:
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
            if attempt == 2:
                raise Exception(f"Error generating environment detail suggestions: {str(e)}")
            time.sleep(2 ** attempt)
