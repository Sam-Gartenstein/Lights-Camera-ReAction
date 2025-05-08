
from typing import Dict, List, Tuple
from utils.agents.comedy_helpers import (
    analyze_and_verify_comedic_consistency,
    recommend_comedic_improvements
)

class ComedicAgent:
    def __init__(self, client, vector_metadata):
        """
        Initializes the ComedicAgent.

        Args:
            client: OpenAI client for prompting.
            vector_metadata: List of prior scene metadata (summaries, recurring jokes, etc.).
        """
        self.client = client
        self.vector_metadata = vector_metadata
        self.internal_thoughts = []

    def analyze_and_verify(self, scene_description: str, scene_number: int) -> Tuple[bool, str]:
        """
        Think + Observe: Analyze comedic tone and verify consistency with prior scenes.

        Returns:
            - is_consistent (bool)
            - analysis_text (str)
        """
        is_consistent, analysis_text = analyze_and_verify_comedic_consistency(
            client=self.client,
            prior_scene_metadata=self.vector_metadata,
            scene_description=scene_description
        )
        self.internal_thoughts.append(f"Analyzed and verified comedic consistency for Scene {scene_number}.")
        return is_consistent, analysis_text

    def recommend(self, scene_description: str) -> str:
        """
        Recommend: Suggest comedic improvements for the scene.

        Returns:
            - recommendations (str)
        """
        recommendations = recommend_comedic_improvements(
            client=self.client,
            scene_description=scene_description
        )
        self.internal_thoughts.append("Provided comedic enhancement suggestions.")
        return recommendations

    def run(self, scene_description: str, scene_number: int) -> Tuple[bool, str, str, List[str]]:
        """
        Full ReAct cycle: Analyze/Verify ➔ Recommend.

        Returns:
            - is_consistent (bool)
            - analysis_text (str)
            - recommendations (str)
            - internal_thoughts (List[str])
        """
        is_consistent, analysis_text = self.analyze_and_verify(scene_description, scene_number)
        recommendations = self.recommend(scene_description)
        return is_consistent, analysis_text, recommendations, self.internal_thoughts
