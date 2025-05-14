

from agents.character_agent import CharacterAgent
from agents.comedy_agent import ComedicAgent
from agents.environment_agent import EnvironmentAgent
from typing import Tuple, Dict, List

def evaluate_character_agent_scene(
    agent: CharacterAgent,
    scene_description: str,
    scene_number: int
) -> Tuple[Dict[str, Dict], bool, str, str, List[str]]:
    """
    Runs the CharacterAgent on a given scene and prints a cleaned summary of results:
    - Consistency verdict
    - Short explanation
    - 2 recommended interactions
    - Agent's internal thoughts

    Args:
        agent (CharacterAgent): The CharacterAgent instance.
        scene_description (str): The current scene's description.
        scene_number (int): The scene number being evaluated.

    Returns:
        Tuple of:
            - character_histories (dict)
            - is_consistent (bool)
            - explanation (str)
            - recommendations (str)
            - internal_thoughts (list of str)
    """
    print(f"🔁 Agent will consider the last {agent.num_scenes} scene(s) for context.\n")

    character_histories, is_consistent, explanation, recommendations, thoughts = agent.run(
        scene_description=scene_description,
        scene_number=scene_number
    )

    # Extract short explanation only
    short_explanation = ""
    for line in explanation.split("\n"):
        if line.strip().startswith("2. Short Explanation Why:"):
            short_explanation = line.strip()
            break

    # Only keep the two interaction suggestions (strip label)
    clean_recommendations = "\n".join([
        line for line in recommendations.split("\n")
        if line.strip().startswith("1.") or line.strip().startswith("2.")
    ])

    print(f"Scene {scene_number} — Consistency: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}\n")
    print("Explanation:")
    print(short_explanation if short_explanation else explanation.strip())
    print("\nInteraction Improvement Recommendations:")
    print(clean_recommendations.strip())
    print("\nAgent's Internal Thoughts:")
    for thought in thoughts:
        print("-", thought)

    return character_histories, is_consistent, explanation, recommendations, thoughts


def evaluate_comedic_agent_scene(
    agent: ComedicAgent,
    scene_description: str,
    scene_number: int
) -> Tuple[Dict, bool, str, str, List[str]]:
    """
    Runs the ComedicAgent on a given scene and prints a cleaned summary of results:
    - Comedic tone consistency verdict
    - Short explanation
    - 2 recommended comedic improvements
    - Agent's internal thoughts

    Args:
        agent (ComedicAgent): The ComedicAgent instance.
        scene_description (str): The current scene’s description.
        scene_number (int): Scene number for tracking/logging.

    Returns:
        Tuple of:
            - context (dict)
            - is_consistent (bool)
            - analysis_text (str)
            - recommendations (str)
            - internal_thoughts (list of str)
    """
    print(f"🔁 Agent will consider the last {agent.num_scenes} scene(s) for context.\n")

    context, is_consistent, analysis_text, recommendations, thoughts = agent.run(
        scene_description=scene_description,
        scene_number=scene_number
    )

    # Extract short explanation line (line starting with 3.)
    short_explanation = ""
    for line in analysis_text.split("\n"):
        if line.strip().startswith("3. Short Explanation"):
            short_explanation = line.strip()
            break

    # Keep only the two recommendation lines
    clean_recommendations = "\n".join([
        line for line in recommendations.split("\n")
        if line.strip().startswith("1.") or line.strip().startswith("2.")
    ])

    print(f"Scene {scene_number} — Comedic Tone: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}\n")
    print("Comedic Tone Analysis:")
    print(short_explanation if short_explanation else analysis_text.strip())
    print("\nComedic Improvement Recommendations:")
    print(clean_recommendations.strip())
    print("\nComedic Agent's Internal Thoughts:")
    for thought in thoughts:
        print("-", thought)

    return context, is_consistent, analysis_text, recommendations, thoughts


def evaluate_environment_agent_scene(
    agent: EnvironmentAgent,
    scene_description: str,
    scene_number: int
) -> Tuple[Dict, bool, str, str, List[str]]:
    """
    Runs the EnvironmentReActAgent on a given scene and prints a structured summary:
    - Whether the environment transition is logical
    - Explanation or critique
    - Suggested environment detail enhancements
    - Internal reasoning trace from the agent

    Args:
        agent: An initialized EnvironmentReActAgent
        scene_description (str): Description of the current scene
        scene_number (int): Scene number (for indexing and logging)

    Returns:
        Tuple containing:
            - context (dict): Location and analysis metadata
            - is_consistent (bool): Whether the transition is logical
            - explanation (str): The model's explanation
            - suggestions (str): Proposed environment enhancements
            - internal_thoughts (list): Agent's reasoning log
    """
    print(f"🔁 Environment Agent will consider the last {agent.num_scenes} scene(s) for context.\n")

    context, is_consistent, explanation, suggestions, thoughts = agent.run(
        scene_description=scene_description,
        scene_number=scene_number
    )

    print(f"Scene {scene_number} — Environment Transition: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}\n")

    print("Explanation:")
    print(explanation.strip())

    print("\nEnvironment Detail Suggestions:")
    print(suggestions.strip())

    print("\nEnvironment Agent's Internal Thoughts:")
    for thought in thoughts:
        print("-", thought)

    return context, is_consistent, explanation, suggestions, thoughts
