
import time
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

    def plan_next_scene(
        self,
        character_recommendations: str,
        comedic_recommendations: str,
        environment_recommendations: str,
        scene_number: int
    ) -> str:
        """
        Synthesizes a next-scene plan by combining recommendations from character, comedy,
        and environment agents into a cohesive and sitcom-appropriate plan.

        The scene plan includes:
        - Two specific character goals
        - One focused comedic beat
        - One environmental detail that supports story or humor
        - One creative narrative suggestion to guide progression

        This function is structured to simulate the reasoning of an Executive Producer who is
        filtering and rephrasing agent feedback into actionable direction for a writers' room.

        Includes retry logic (up to 3 attempts with exponential backoff) to handle transient failures.

        Args:
            character_recommendations (str): Feedback from the Character Agent.
            comedic_recommendations (str): Feedback from the Comedic Agent.
            environment_recommendations (str): Feedback from the Environment Agent.
            scene_number (int): The index of the scene to be planned.

        Returns:
            str: A formatted scene plan with clearly labeled goals and a creative suggestion.

        Raises:
            ValueError: If the API response is empty or malformed.
            Exception: After 3 failed retry attempts or other runtime issues.
        """
        prompt = f"""
You are the Executive Producer of a sitcom. Your agents have just provided feedback on Scene {scene_number}.

They offered targeted **recommendations** in three categories: character, comedy, and environment.

Your job is to **synthesize** these inputs — don't just repeat them. Instead, extract the most relevant themes and rewrite them as clear, concise next-scene objectives.

Character Recommendations:
{character_recommendations}

Comedic Recommendations:
{comedic_recommendations}

Environment Recommendations:
{environment_recommendations}

Tasks:
- Write **2 Character Goals** based on the above character recommendations.
- Write **1 Comedic Goal** inspired by the tone, running gags, or humor critiques above.
- Write **1 Environment Detail** that builds on the suggestions without repeating them verbatim.
- Propose **1 Creative Suggestion** for how the scene could naturally progress, integrating the above goals.

Each should be specific, natural, and sitcom-appropriate for a 2–3 minute scene.

Format:
Scene Plan:
Character Goals:
- [Goal 1]
- [Goal 2]

Comedic Goal:
- [Goal]

Environment Detail:
- [Detail]

Creative Suggestion:
- [Suggestion]
"""

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    top_p=0.9
                )

                if not response or not response.choices or not response.choices[0].message.content:
                    raise ValueError("Received an empty or malformed scene plan response.")

                scene_plan = response.choices[0].message.content.strip()
                self.internal_thoughts.append(f"✅ Scene {scene_number} plan generated successfully.")
                return scene_plan

            except Exception as e:
                if attempt == 2:
                    error_msg = f"❌ Failed to generate scene plan for Scene {scene_number}: {str(e)}"
                    self.internal_thoughts.append(error_msg)
                    raise Exception(error_msg)
                time.sleep(2 ** attempt)
