
def explain_rag_usage(client, sitcom_title, scene_script, rag_context, scene_index, used_context_summaries, context_method="semantic retrieval"):
    """
    Asks the LLM to explain how retrieved context influenced the current scene.
    Includes metadata about which scenes were retrieved and why.
    """
    if not rag_context:
        return "No RAG context was used for this scene."

    used_scene_info = "\n".join(
        f"- Scene {item['scene_number']} (similarity: {item['similarity']}): {item['summary'][:100]}..."
        for item in used_context_summaries
    )

    prompt = f"""
You are a sitcom script evaluator.

The following is Scene {scene_index + 1} from a sitcom titled "{sitcom_title}". It was written using prior scene context via **{context_method}**.

The following prior scenes were selected based on semantic similarity:
{used_scene_info}

Your task:
1. Explain why each selected prior scene may have been chosen based on its summary and similarity score.
2. Describe how each scene appears to have influenced the current scene.
3. Identify any callbacks, continuity of character arcs, or tone/style preservation.

Prior Context:
{rag_context}

Generated Scene {scene_index + 1}:
{scene_script}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content.strip()
