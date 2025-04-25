from .rag_utils import explain_rag_usage
from .character_management import (
    analyze_characters,
    retrieve_character_history,
    verify_character_consistency,
    plan_character_arcs
)
from datetime import timedelta
import numpy as np


def generate_scene_1_script(
    client,
    sitcom_title,
    scene_description,
    scene_index=None,
    rag_context=None,
    line_target=(50, 70),
    average_scene_minutes=2.5
):
    """
    Generates a sitcom scene script with logical laugh tracks, natural tone inferred from the description,
    and optional timestamp headings.
    """
    # Timestamp calculation
    if scene_index is not None:
        start_time = timedelta(minutes=scene_index * average_scene_minutes)
        end_time = timedelta(minutes=(scene_index + 1) * average_scene_minutes)
        timestamp_text = f"# Scene {scene_index + 1} — [{str(start_time)[:-3]}–{str(end_time)[:-3]}]\n"
    else:
        timestamp_text = ""

    # Context block if RAG is provided
    context_section = f"\nRelevant background information:\n{rag_context}" if rag_context else ""
    min_lines, max_lines = line_target

    # Prompt for LLM
    prompt = f"""
You are a professional sitcom scriptwriter.

Sitcom Title: {sitcom_title}
Scene Description: {scene_description}{context_section}

Write this scene as a formatted sitcom script.

Format:
- Scene heading (e.g., INT. EARL'S LOCKSMITH SHOP – DAY)
- Character names in ALL CAPS
- Dialogue written with natural flow and comedic timing
- Stage directions in parentheses
- Include [LAUGH TRACK] only where it makes logical sense based on the rhythm and tone of the scene (e.g., punchlines, awkward silences, physical comedy). Use sparingly.

Constraints:
- Write approximately {min_lines} to {max_lines} total lines (including stage directions, dialogue, and laugh tracks)
- Do not write more than one scene
- Let the tone and pacing emerge naturally from the scene description and context
- Focus on character dynamics and comedic flow

End the scene cleanly without cutting off mid-conversation.
"""

    # Call the API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        top_p=1,
    )

    # Post-processing (commented out for now)
    # raw_script = response.choices[0].message.content.strip()
    # lines = [line.strip() for line in raw_script.split("\n") if line.strip()]
    # numbered_script = "\n".join([f"{i+1:>3}. {line}" for i, line in enumerate(lines)])

    # return f"{timestamp_text}\n{numbered_script}"

    # Return raw output
    return f"{timestamp_text}\n{response.choices[0].message.content.strip()}"


def generate_scene_with_context(
    client,
    sitcom_title,
    scene_description,
    scene_index,
    vector_metadata,
    embedding_model,
    top_k=3,
    line_target=(50, 70),
    average_scene_minutes=2.5
):
    """
    Generates a sitcom scene using ReAct RAG for better character consistency.
    """
    print(f"\n[Scene {scene_index+1}] Starting ReAct RAG process...")

    # Step 1: Think - Analyze what characters are in the scene
    print("1. Analyzing characters in scene...")
    characters = analyze_characters(client, scene_description)
    print(f"   Identified characters: {', '.join(characters)}")

    # Step 2: Act - Retrieve character histories
    print("2. Retrieving character histories...")
    character_profiles = {}
    for character in characters:
        profile = retrieve_character_history(
            client,
            character,
            vector_metadata,
            embedding_model
        )
        character_profiles[character] = profile
        print(f"   Retrieved profile for {character}")

    # Step 3: Observe - Verify consistency
    print("3. Verifying character consistency...")
    is_consistent, consistency_report = verify_character_consistency(
        client,
        character_profiles,
        scene_description
    )
    print(f"   Consistency check: {'PASSED' if is_consistent else 'NEEDS REVISION'}")

    # Step 4: Think - Plan character arcs
    print("4. Planning character arcs...")
    arc_plan = plan_character_arcs(
        client,
        character_profiles,
        scene_description,
        scene_index + 1
    )
    print("   Character arcs planned")

    # Combine all context for scene generation
    rag_context = f"""
Character Profiles and History:
{chr(10).join(f'{char}:{profile["profile"]}' for char, profile in character_profiles.items())}

Character Arc Plan:
{arc_plan}

Consistency Requirements:
{consistency_report}
"""

    # Generate the scene with enhanced character context
    script = generate_scene_1_script(
        client=client,
        sitcom_title=sitcom_title,
        scene_description=scene_description,
        scene_index=scene_index,
        rag_context=rag_context,
        line_target=line_target,
        average_scene_minutes=average_scene_minutes
    )

    # Generate explanation of RAG usage
    explanation = explain_rag_usage(
        client=client,
        sitcom_title=sitcom_title,
        scene_script=script,
        rag_context=rag_context,
        scene_index=scene_index,
        used_context_summaries=[],  # We're using character profiles instead
        context_method="ReAct RAG with character consistency"
    )

    print(f"\n[Scene {scene_index+1}] ReAct RAG process complete.")
    print(f"[Scene {scene_index+1}] Explanation of character consistency:\n{explanation}\n")

    return script
