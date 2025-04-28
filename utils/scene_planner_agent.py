
from typing import List

class ScenePlannerAgent:
    def __init__(self, client):
        """
        Initializes the ScenePlannerAgent.

        Args:
            client: OpenAI client for prompting.
        """
        self.client = client
        self.internal_thoughts = []

    def plan_next_scene_explicit(
        self,
        character_recommendations: str,
        comedic_recommendations: str,
        environment_details_suggestions: str,
        scene_number: int
    ) -> str:
        """
        Creates a scene plan based on agent outputs, with explicit structure:
        - 2 goals from CharacterAgent
        - 1 goal from ComedicAgent
        - 1 environment detail from EnvironmentAgent
        - 1 creative suggestion

        Returns:
            - scene_plan (str)
        """
        prompt = f"""
You are a sitcom scene planning assistant.

You have just reviewed Scene {scene_number}.

Character Improvement Suggestions:
{character_recommendations}

Comedic Improvement Suggestions:
{comedic_recommendations}

Environment Details Suggestions:
{environment_details_suggestions}

Tasks:
- Select exactly **2** goals from the Character Improvement Suggestions.
- Select exactly **1** goal from the Comedic Improvement Suggestions.
- Select exactly **1** environment detail from the Environment Details Suggestions.
- Propose exactly **1** creative suggestion for how the next scene could naturally progress, reinforcing these goals.
- Keep the plan grounded, character-driven, environment-aware, and sitcom-appropriate (2–3 minute scene).

Format:
Scene Plan:
Character Goals:
- [Goal 1]
- [Goal 2]

Comedic Goal:
- [Goal 1]

Environment Detail:
- [Detail]

Creative Suggestion:
- [Suggestion]
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        scene_plan = response.choices[0].message.content.strip()
        self.internal_thoughts.append(f"Generated explicit structured scene plan for Scene {scene_number}.")
        return scene_plan
