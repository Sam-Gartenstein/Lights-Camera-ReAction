
import pandas as pd
import re

def evaluate_scene_block(
    client,
    scene_list,
    episode_concept,
    temperature=0.1,
    previous_scene_block=None,
    model="gpt-4"
):
    """
    Evaluates a block of sitcom scene scripts (as strings), with optional prior scene descriptions.

    Args:
        client: OpenAI client instance.
        scene_list (list of str): List of full formatted scene scripts.
        episode_concept (str): One-sentence episode premise.
        temperature (float): Sampling temperature.
        previous_scene_block (list of dict, optional): Prior scene descriptions, each with
            'scene_number' and 'scene_description'.
        model (str): The OpenAI model to use (default: "gpt-4").

    Returns:
        str: Evaluation from the model.
    """
    current_scenes = "\n\n".join(scene_list)

    # Format prior context
    if previous_scene_block:
        previous_description_block = "\n".join(
            [f"Scene {s['scene_number']}: {s['scene_description']}" for s in previous_scene_block]
        )
        context_note = f"""
To help you evaluate this scene block in context, here is a summary of the previous scenes:

{previous_description_block}
"""
    else:
        context_note = ""

    prompt = f"""
You are a sitcom development executive at a major streaming platform. You've just finished reviewing the pilot episode of a new sitcom.

Here is the core concept of the episode:

"{episode_concept}"
{context_note}

Below is a block of 5 full sitcom scenes. Your task is to evaluate the block on the following five criteria. For each, give a score from 1 to 10 and a short justification.

**Evaluation Criteria:**
1. Coherence – Does the scene block flow logically and maintain internal consistency?
2. Relevance – Do the scenes support the episode concept, character arcs, and prior developments?
3. Interestingness – Are the scenes original, engaging, and narratively dynamic?
4. Humor – Is the comedy well-timed, character-driven, and appropriately varied?
5. Overall Quality – Holistic rating based on structure, tone, genre fit, and writing polish.

---

Scenes:
{current_scenes}

---

Respond like this:

- Coherence: X – explanation
- Relevance: X – explanation
- Interestingness: X – explanation
- Humor: X – explanation
- Overall Quality: X – explanation
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )

    if not response or not response.choices or not response.choices[0].message.content:
        raise ValueError("API returned an empty or malformed response.")

    return response.choices[0].message.content.strip()


def evaluate_episode_blocks(
    client,
    episode_num,
    script_blocks,
    description_blocks,
    episode_concept,
    model="gpt-4"
):
    """
    Evaluates blocks of sitcom scenes for a given episode using provided scripts and scene descriptions.

    Args:
        client: OpenAI client instance.
        episode_num (int): The episode number (1–5).
        script_blocks (dict): Dictionary of scene blocks (full scripts) for the episode.
        description_blocks (dict): Dictionary of scene description blocks for context.
        episode_concept (str): The episode concept string.
        model (str): OpenAI model to use (default: "gpt-4").

    Returns:
        dict: Dictionary with evaluation results for each scene block.
    """
    evaluation_results = {}

    for block_index in range(1, len(script_blocks) + 1):
        scene_list = script_blocks[f"scene_block_{block_index}"]

        if block_index == 1:
            result = evaluate_scene_block(
                client=client,
                scene_list=scene_list,
                episode_concept=episode_concept,
                model=model
            )
        else:
            previous_desc_block = description_blocks[f"scene_block_{block_index - 1}"]
            result = evaluate_scene_block(
                client=client,
                scene_list=scene_list,
                episode_concept=episode_concept,
                previous_scene_block=previous_desc_block,
                model=model
            )

        evaluation_results[f"scene_block_{block_index}"] = result

    return evaluation_results


def extract_evaluation_scores(evaluation_dict, episode_number, version_label):
    """
    Extracts numerical evaluation scores from a dictionary of scene block evaluations and stores them in a DataFrame.

    Args:
        evaluation_dict (dict): Dictionary where keys are block names (e.g., "scene_block_1") and values are full text evaluations.
        episode_number (int): The episode number being evaluated.
        version_label (str): Label for version type (e.g., "ReAct", "Baseline").

    Returns:
        pd.DataFrame: DataFrame with columns:
            ['episode', 'version', 'scene_block', 'criterion', 'score', 'justification']
    """
    rows = []

    for block_name, eval_text in evaluation_dict.items():
        lines = eval_text.splitlines()
        for line in lines:
            match = re.match(r"- (\w[\w ]+): (\d+) – (.+)", line)
            if match:
                criterion = match.group(1).strip()
                score = int(match.group(2))
                explanation = match.group(3).strip()

                rows.append({
                    "episode": episode_number,
                    "version": version_label,
                    "scene_block": block_name,
                    "criterion": criterion,
                    "score": score,
                    "justification": explanation
                })
            else:
                # Optional: warning for unmatched lines
                if line.strip().startswith("-"):
                    print(f"⚠️ Skipped unmatched line in {block_name}: {line}")

    return pd.DataFrame(rows)
