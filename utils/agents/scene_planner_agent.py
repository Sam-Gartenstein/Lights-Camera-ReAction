
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
        Synthesizes a concise next-scene plan based on the suggestions from all ReAct agents.

        Rather than copying existing recommendations, the Executive Producer role is to rephrase and
        distill feedback into 4 concrete, meaningful, and sitcom-appropriate objectives.

        Returns:
            - scene_plan (str)
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

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            top_p=0.9
        )

        scene_plan = response.choices[0].message.content.strip()
        self.internal_thoughts.append(f"Generated synthesized scene plan for Scene {scene_number}.")
        return scene_plan
