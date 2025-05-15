
from typing import Dict, List, Tuple
from comedy_helpers import (
    analyze_and_verify_comedic_consistency,
    recommend_comedic_improvements
)

class ComedicAgent:
    def __init__(self, client, vector_metadata, num_scenes: int = 3):
        """
        Initializes the ComedicAgent.

        Args:
            client: OpenAI client for prompting.
            vector_metadata: List of prior scene metadata (summaries, recurring jokes, etc.).
            num_scenes: Number of prior scenes to consider for tone checking.
        """
        self.client = client
        self.vector_metadata = vector_metadata
        self.num_scenes = num_scenes
        self.internal_thoughts = []

    def think(self, scene_description: str, scene_number: int) -> None:
        """
        Think step: Log the target scene and which prior scenes will be used for context.
        """
        start_scene = max(1, scene_number - self.num_scenes)
        scene_range = list(range(start_scene, scene_number))
        print(f"📚 Retrieving script metadata for scene(s): {scene_range}")
        self.internal_thoughts.append(f"Think: Will retrieve summaries and jokes from scene(s) {scene_range} for Scene {scene_number}.")

    def act(self, scene_number: int) -> Dict:
        """
        Act step: Retrieve summaries and running jokes from recent scenes.
        """
        prior_summaries = [meta["summary"] for meta in self.vector_metadata][-self.num_scenes:]
        prior_jokes = []
        for meta in self.vector_metadata[-self.num_scenes:]:
            prior_jokes.extend(meta.get("recurring_joke", []))

        self.internal_thoughts.append("Act: Retrieved summaries and jokes from prior scenes.")
        return {
            "summaries": prior_summaries,
            "recurring_jokes": prior_jokes
        }

    def observe(self, scene_description: str) -> Tuple[bool, str]:
        """
        Observe step: Verify comedic tone consistency and joke usage.
        """
        is_consistent, analysis_text = analyze_and_verify_comedic_consistency(
            client=self.client,
            prior_scene_metadata=self.vector_metadata,
            scene_description=scene_description,
            max_scenes=self.num_scenes
        )

        verdict = "consistent" if is_consistent else "inconsistent"
        self.internal_thoughts.append(f"Observe: Scene is {verdict} with prior comedic tone.")
        return is_consistent, analysis_text

    def recommend(self, scene_description: str, is_consistent: bool, analysis_text: str) -> str:
        """
        Recommend step: Suggest comedic punch-ups or tonal fixes.
        """
        recommendations = recommend_comedic_improvements(
            client=self.client,
            scene_description=scene_description,
            is_consistent=is_consistent,
            consistency_result=analysis_text
        )
        self.internal_thoughts.append("Recommend: Provided comedic improvements.")
        return recommendations

    def run(self, scene_description: str, scene_number: int) -> Tuple[Dict, bool, str, str, List[str]]:
        """
        Full ReAct cycle: Think ➔ Act ➔ Observe ➔ Recommend

        This method coordinates the comedy evaluation steps:
        - Think: Logs what context will be used.
        - Act: Gathers summaries and running jokes from prior scenes.
        - Observe: Uses `analyze_and_verify_comedic_consistency` to evaluate tone and gag usage.
        - Recommend: Uses `recommend_comedic_improvements` to suggest grounded humor or tonal fixes.

        Returns:
            A tuple containing:
            - context (dict): summaries and recurring jokes
            - is_consistent (bool): whether the scene aligns with prior tone
            - analysis_text (str): structured explanation
            - recommendations (str): suggested comedic revisions
            - internal_thoughts (list of str): agent reasoning trace
        """
        self.think(scene_description, scene_number)
        context = self.act(scene_number)
        is_consistent, analysis_text = self.observe(scene_description)
        recommendations = self.recommend(scene_description, is_consistent, analysis_text)
        return context, is_consistent, analysis_text, recommendations, self.internal_thoughts
