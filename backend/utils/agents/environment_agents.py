
from typing import List, Tuple
from utils.agents.environment_helpers import (
    analyze_environment,
    verify_environment_transition,
    suggest_environment_details
)


class EnvironmentReActAgent:
    """
    A ReAct agent specialized for maintaining environment and setting continuity across scenes.
    """

    def __init__(self, client, vector_metadata, num_scenes: int = 3):
        """
        Initializes the EnvironmentReActAgent.

        Args:
            client: OpenAI client for prompting.
            vector_metadata: List of prior scene metadata (summaries, locations, etc.).
            num_scenes: How many prior scenes to use for checking transitions.
        """
        self.client = client
        self.vector_metadata = vector_metadata
        self.num_scenes = num_scenes
        self.internal_thoughts = []

    def run(self, scene_description: str, scene_number: int) -> Tuple[str, str, str, List[str]]:
        """
        Full ReAct cycle: Analyze ➔ Verify ➔ Recommend

        Returns:
            - environment_analysis (str)
            - transition_check (str)
            - environment_details_suggestions (str)
            - internal_thoughts (List[str])
        """
        # Analyze environment
        environment_analysis = analyze_environment(
            client=self.client,
            scene_description=scene_description,
            scene_number=scene_number
        )
        self.internal_thoughts.append(f"Analyzed environment features for Scene {scene_number}.")

        # Extract environment name
        current_environment = ""
        for line in environment_analysis.split("\n"):
            if line.strip().startswith("Environment:"):
                current_environment = line.split(":", 1)[1].strip()

        # Get prior environments
        prior_environments = [meta.get("location", "Unknown") for meta in self.vector_metadata]

        # Verify transition
        transition_check = verify_environment_transition(
            client=self.client,
            prior_environments=prior_environments,
            current_environment=current_environment,
            num_scenes=self.num_scenes
        )
        self.internal_thoughts.append(f"Verified environment transition based on last {self.num_scenes} scenes.")

        # Suggest environment details
        environment_details_suggestions = suggest_environment_details(
            client=self.client,
            environment_analysis=environment_analysis,
            transition_check=transition_check
        )
        self.internal_thoughts.append("Suggested environment and sensory details for next scene.")

        return environment_analysis, transition_check, environment_details_suggestions, self.internal_thoughts
