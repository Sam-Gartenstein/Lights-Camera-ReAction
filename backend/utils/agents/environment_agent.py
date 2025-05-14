
from typing import List, Tuple, Dict
from .environment_helpers import (
    analyze_environment,
    verify_environment_transition,
    suggest_environment_details
)

class EnvironmentAgent:
    """
    A ReAct agent specialized for maintaining environment and setting continuity across scenes.
    """

    def __init__(self, client, vector_metadata, num_scenes: int = 3):
        """
        Initializes the EnvironmentAgent.

        Args:
            client: OpenAI client for prompting.
            vector_metadata: List of prior scene metadata (summaries, locations, etc.).
            num_scenes: Number of prior scenes to use for checking transitions.
        """
        self.client = client
        self.vector_metadata = vector_metadata
        self.num_scenes = num_scenes
        self.internal_thoughts = []

    def think(self, scene_description: str, scene_number: int) -> Dict:
        """
        Think step: Determine the range of relevant scenes for analysis.
        """
        start_scene = max(1, scene_number - self.num_scenes)
        scene_range = list(range(start_scene, scene_number))
        print(f"📚 Retrieving script metadata for scene(s): {scene_range}")
        self.internal_thoughts.append(
            f"Think: Retrieved summaries and environment context from scene(s) {scene_range} for Scene {scene_number}."
        )
        return {"scene_range": scene_range}

    def act(self, scene_description: str, scene_number: int) -> Dict:
        """
        Act step: Analyze the environment and identify key features.
        """
        environment_analysis = analyze_environment(
            client=self.client,
            scene_description=scene_description,
            scene_number=scene_number
        )
        self.internal_thoughts.append(f"Act: Analyzed environment features for Scene {scene_number}.")

        current_environment = ""
        for line in environment_analysis.split("\n"):
            if line.strip().startswith("Environment:"):
                current_environment = line.split(":", 1)[1].strip()

        return {
            "analysis": environment_analysis,
            "environment": current_environment
        }

    def observe(self, current_environment: str) -> Tuple[bool, str, str]:
        """
        Observe step: Evaluate if the environment transition is logical and natural.
        """
        prior_environments = [meta.get("location", "Unknown") for meta in self.vector_metadata]
        print("prior_environments:", prior_environments)
        print("current_environment:", current_environment)

        is_consistent, explanation, formatted_output = verify_environment_transition(
            client=self.client,
            prior_environments=prior_environments,
            current_environment=current_environment,
            num_scenes=self.num_scenes
        )

        verdict = "consistent" if is_consistent else "inconsistent"
        self.internal_thoughts.append(f"Observe: Scene transition is {verdict}.")
        return is_consistent, explanation, formatted_output

    def recommend(self, environment_analysis: str, transition_check: str, is_consistent: bool) -> str:
        """
        Recommend step: Suggest small sensory/environmental details to reinforce the setting.
        """
        suggestions = suggest_environment_details(
            client=self.client,
            environment_analysis=environment_analysis,
            transition_check=transition_check,
            is_consistent=is_consistent
        )
        self.internal_thoughts.append("Recommend: Provided environmental enhancement suggestions.")
        return suggestions

    def run(self, scene_description: str, scene_number: int) -> Tuple[Dict, bool, str, str, List[str]]:
        """
        Full ReAct cycle: Think ➔ Act ➔ Observe ➔ Recommend

        Returns:
            - context (Dict): Includes analysis and identified environment
            - is_consistent (bool): Whether the transition was logical
            - explanation (str): Explanation or critique of transition
            - suggestions (str): Environmental enhancement ideas
            - internal_thoughts (List[str]): Agent's reasoning steps
        """
        _ = self.think(scene_description, scene_number)
        context = self.act(scene_description, scene_number)
        is_consistent, explanation, full_transition_text = self.observe(context["environment"])
        suggestions = self.recommend(context["analysis"], full_transition_text, is_consistent)
        return context, is_consistent, explanation, suggestions, self.internal_thoughts
