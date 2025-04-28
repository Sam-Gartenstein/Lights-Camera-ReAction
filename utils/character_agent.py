
from character_helpers import (
    analyze_characters,
    retrieve_character_history,
    verify_character_consistency,
    recommend_character_interactions
)

from typing import Dict, List, Tuple

class CharacterAgent:
    def __init__(self, client, vector_metadata):
        self.client = client
        self.vector_metadata = vector_metadata
        self.internal_thoughts = []  # Tracks internal reasoning

    def think(self, scene_description: str, scene_number: int) -> Dict:
        """
        Think step: Analyze the scene to detect characters.
        """
        character_info = analyze_characters(
            client=self.client,
            scene_description=scene_description,
            prior_scene_metadata=self.vector_metadata,
            scene_number=scene_number
        )
        self.internal_thoughts.append(f"Think: Identified characters {character_info['current_scene_characters']} in Scene {scene_number}.")
        return character_info

    def act(self, character_info: Dict, scene_description: str) -> Dict[str, Dict]:
        """
        Act step: Retrieve character histories from previous scenes.
        """
        character_histories = {}
        for character in character_info["current_scene_characters"]:
            profile = retrieve_character_history(
                client=self.client,
                character=character,
                vector_metadata=self.vector_metadata,
                current_scene_description=scene_description,
                max_scenes=3
            )
            character_histories[character] = profile
        self.internal_thoughts.append(f"Act: Retrieved profiles for {list(character_histories.keys())}.")
        return character_histories

    def observe(self, character_histories: Dict[str, Dict], scene_description: str) -> Tuple[bool, str]:
        """
        Observe step: Verify if characters are consistent with their profiles.
        """
        is_consistent, explanation = verify_character_consistency(
            client=self.client,
            character_profiles=character_histories,
            scene_description=scene_description
        )
        verdict = "consistent" if is_consistent else "inconsistent"
        self.internal_thoughts.append(f"Observe: Scene is {verdict}.")
        return is_consistent, explanation

    def recommend(self, character_histories: Dict[str, Dict], scene_description: str) -> str:
        """
        Recommend step: Suggest how to maximize character interactions.
        """
        recommendation = recommend_character_interactions(
            client=self.client,
            character_profiles=character_histories,
            scene_description=scene_description
        )
        self.internal_thoughts.append("Recommend: Provided suggestions for enhancing character dynamics.")
        return recommendation

    def run(self, scene_description: str, scene_number: int) -> Tuple[Dict[str, Dict], bool, str, str, List[str]]:
        """
        Full ReAct cycle: Think ➔ Act ➔ Observe ➔ Recommend
        """
        character_info = self.think(scene_description, scene_number)
        character_histories = self.act(character_info, scene_description)
        is_consistent, explanation = self.observe(character_histories, scene_description)
        recommendations = self.recommend(character_histories, scene_description)
        return character_histories, is_consistent, explanation, recommendations, self.internal_thoughts

