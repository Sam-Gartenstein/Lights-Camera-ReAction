import os
import sys
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Import utility functions
from utils.outline_generation import generate_sitcom_pitch, generate_pilot_episode_outline
from utils.screen_writing import generate_scene_1_script
from utils.script_review import validate_episode_outline
from utils.vector_db_utils import summarize_scene, add_scene_to_vector_db
from utils.text_utils import extract_scene, extract_title
# Import character management functions
from utils.character_management import (
    analyze_characters,
    retrieve_character_history,
    verify_character_consistency,
    plan_character_arcs
)

def main():
    api_key = input("Please enter your OpenAI API key: ")
    client = OpenAI(api_key=api_key)

    # Initialize vector database
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    dimension = embedding_model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatL2(dimension)
    vector_metadata = []

    # Test keywords
    keywords = [
        "urban locksmith shop",
        "ex-con protagonist",
        "estranged daughter",
        "quirky parole officer",
        "second chances",
        "buddy comedy",
        "New York City",
        "heartfelt absurdism",
        "odd couple dynamic"
    ]

    print("1. Generating Sitcom Pitch...")
    sitcom_pitch = generate_sitcom_pitch(client, keywords)
    print(f"\nSitcom Pitch:\n{sitcom_pitch}\n")

    print("2. Generating Episode Outline...")
    outline = generate_pilot_episode_outline(client, sitcom_pitch)
    print(f"\nEpisode Outline:\n{outline}\n")

    print("3. Validating Episode Coherence...")
    validation = validate_episode_outline(client, sitcom_pitch, outline)
    print(f"\nValidation Results:\n{validation}\n")

    print("4. Generating First Scene...")
    scene_1_desc = extract_scene(outline, 1)
    sitcom_title = extract_title(sitcom_pitch)
    
    scene_1_script = generate_scene_1_script(
        client=client,
        sitcom_title=sitcom_title,
        scene_description=scene_1_desc,
        rag_context=None,
        line_target=(55, 75)
    )
    print(f"\nScene 1 Script:\n{scene_1_script}\n")

    print("5. Summarizing Scene and Adding to Vector Database...")
    scene_metadata = summarize_scene(
        client=client,
        sitcom_title=sitcom_title,
        scene_script=scene_1_script
    )
    
    add_scene_to_vector_db(
        scene_metadata,
        full_script=scene_1_script,
        embedding_model=embedding_model,
        index=index,
        vector_metadata=vector_metadata
    )
    
    print("\nScene Metadata:")
    print(f"Summary: {scene_metadata['summary']}")
    print(f"Characters: {scene_metadata['characters']}")
    print(f"Location: {scene_metadata['location']}")
    print(f"Recurring Joke: {scene_metadata['recurring_joke']}")
    print(f"Emotional Tone: {scene_metadata['emotional_tone']}")
    
    # New section: Character Management
    print("\n6. Character Management...")
    
    # 6.1 Analyze characters in the scene
    print("\n6.1 Analyzing Characters in Scene 1...")
    characters = analyze_characters(client, scene_1_desc)
    print(f"Characters identified: {characters}")
    
    # 6.2 Retrieve character history for each character
    print("\n6.2 Retrieving Character History...")
    character_profiles = {}
    for character in characters:
        print(f"\nRetrieving history for {character}...")
        profile = retrieve_character_history(
            client=client,
            character=character,
            vector_metadata=vector_metadata,
            embedding_model=embedding_model
        )
        character_profiles[character] = profile
        print(f"Profile: {profile['profile'][:100]}...")
    
    # 6.3 Verify character consistency
    print("\n6.3 Verifying Character Consistency...")
    # Ensure scene description is properly formatted
    formatted_scene_desc = f"""
    Scene Description:
    {scene_1_desc}
    
    Scene Summary:
    {scene_metadata['summary']}
    """
    
    is_consistent, explanation = verify_character_consistency(
        client=client,
        character_profiles=character_profiles,
        scene_description=formatted_scene_desc
    )
    print(f"Consistency: {'Yes' if is_consistent else 'No'}")
    print(f"Explanation: {explanation}")
    
    # 6.4 Plan character arcs
    print("\n6.4 Planning Character Arcs...")
    arc_plan = plan_character_arcs(
        client=client,
        character_profiles=character_profiles,
        scene_description=scene_1_desc,
        scene_number=1,
        total_scenes=5  # Assuming a 5-scene episode
    )
    print(f"Character Arc Plan:\n{arc_plan}")
    
    # New section: Using Character Management for Next Scene
    print("\n7. Using Character Management for Next Scene...")
    
    # 7.1 Extract the next scene description from the outline
    print("\n7.1 Extracting Scene 2 Description...")
    scene_2_desc = extract_scene(outline, 2)
    print(f"Scene 2 Description: {scene_2_desc}")
    
    # 7.2 Create a RAG context from character profiles and arc plan
    print("\n7.2 Creating RAG Context from Character Management...")
    rag_context = f"""
    CHARACTER PROFILES:
    {chr(10).join([f"{char}: {profile['profile']}" for char, profile in character_profiles.items()])}
    
    CHARACTER ARC PLAN:
    {arc_plan}
    
    PREVIOUS SCENE SUMMARY:
    {scene_metadata['summary']}
    """
    
    # 7.3 Generate the next scene using character management information
    print("\n7.3 Generating Scene 2 with Character Management Context...")
    scene_2_script = generate_scene_1_script(
        client=client,
        sitcom_title=sitcom_title,
        scene_description=scene_2_desc,
        rag_context=rag_context,
        line_target=(55, 75)
    )
    print(f"\nScene 2 Script:\n{scene_2_script}\n")
    
    # 7.4 Summarize the new scene and add to vector database
    print("\n7.4 Summarizing Scene 2 and Adding to Vector Database...")
    scene_2_metadata = summarize_scene(
        client=client,
        sitcom_title=sitcom_title,
        scene_script=scene_2_script
    )
    
    add_scene_to_vector_db(
        scene_2_metadata,
        full_script=scene_2_script,
        embedding_model=embedding_model,
        index=index,
        vector_metadata=vector_metadata
    )
    
    print("\nScene 2 Metadata:")
    print(f"Summary: {scene_2_metadata['summary']}")
    print(f"Characters: {scene_2_metadata['characters']}")
    print(f"Location: {scene_2_metadata['location']}")
    print(f"Recurring Joke: {scene_2_metadata['recurring_joke']}")
    print(f"Emotional Tone: {scene_2_metadata['emotional_tone']}")

if __name__ == "__main__":
    main() 