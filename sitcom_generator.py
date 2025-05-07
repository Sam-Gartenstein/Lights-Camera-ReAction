import os
import sys
from getpass import getpass
from dotenv import load_dotenv
import openai
from sentence_transformers import SentenceTransformer
import faiss

# Import all the necessary modules
from utils.agents.character_agent import CharacterAgent
from utils.agents.comedy_agent import ComedicAgent
from utils.agents.environment_agents import EnvironmentReActAgent
from utils.agents.scene_planner_agent import ScenePlannerAgent

from utils.text_utils import (
    display_markdown_output,
    extract_scene,
    extract_title,
)

from utils.outline_generation import (
    generate_sitcom_pitch,
    generate_pilot_episode_outline
)

from utils.script_review import (
    validate_episode_outline,
)

from utils.screen_writing import (
    generate_scene_1_script,
    generate_scene
)

from utils.vector_db_utils import (
    summarize_scene,
    add_scene_to_vector_db
)

def wait_for_confirmation(message="Press Enter to continue..."):
    """Wait for user confirmation before proceeding."""
    input(f"\n{message}")

def setup_api_key():
    """Set up the OpenAI API key either from environment or user input."""
    # First try to load from .env file
    load_dotenv()
    
    # Check if API key exists in environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("OpenAI API key not found in environment variables.")
        api_key = getpass("Please enter your OpenAI API key: ")
        
        # Save to .env file
        with open('.env', 'w') as f:
            f.write(f'OPENAI_API_KEY={api_key}')
        
        # Set environment variable
        os.environ['OPENAI_API_KEY'] = api_key
    
    return api_key

def main():
    """Main function to run the sitcom generation pipeline."""
    # Setup API key
    api_key = setup_api_key()
    print("API key configured successfully!")
    wait_for_confirmation("Ready to start generating your sitcom?")
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Initialize scene metadata list
    scene_metadata = []
    
    # Initialize embedding model and vector database
    print("\nInitializing embedding model and vector database...")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    dimension = embedding_model.get_sentence_embedding_dimension()
    index = faiss.IndexFlatL2(dimension)
    print("Vector database initialized successfully!")
    
    # Initialize agents
    print("\nInitializing AI agents...")
    character_agent = CharacterAgent(client=client, vector_metadata=scene_metadata)
    comedy_agent = ComedicAgent(client=client, vector_metadata=scene_metadata)
    environment_agent = EnvironmentReActAgent(client=client, vector_metadata=scene_metadata)
    scene_planner = ScenePlannerAgent(client=client)
    print("Agents initialized successfully!")
    wait_for_confirmation()
    
    # Generate sitcom concept
    print("\nGenerating sitcom concept...")
    
    # Define categories for keywords
    categories = {
        "setting": "Enter settings/locations (comma-separated): ",
        "characters": "Enter main characters (comma-separated): ",
        "themes": "Enter themes/ideas (comma-separated): ",
        "tone_genre": "Enter tone or genre (comma-separated): "
    }
    
    # Collect keywords from user for each category
    keywords = {}
    print("\nLet's create your sitcom concept! For each category, enter keywords separated by commas.")
    print("Example: 'coffee shop, New York City' for settings\n")
    
    for category, prompt in categories.items():
        user_input = input(prompt)
        # Split by comma and strip whitespace from each keyword
        keywords[category] = [word.strip() for word in user_input.split(',') if word.strip()]
    
    # Convert dictionary to flat list of keywords
    keyword_list = []
    for category, words in keywords.items():
        keyword_list.extend(words)
    
    print("\nYour keywords:")
    for category, words in keywords.items():
        print(f"{category.title()}: {', '.join(words)}")
    
    wait_for_confirmation("Ready to generate the sitcom concept with these keywords?")
    
    sitcom_pitch = generate_sitcom_pitch(client, keyword_list)
    print("\nGenerated Sitcom Concept:")
    print(sitcom_pitch)
    wait_for_confirmation("Review the sitcom concept above. Ready to generate the pilot outline?")
    
    # Generate pilot episode outline
    print("\nGenerating pilot episode outline...")
    outline = generate_pilot_episode_outline(client, sitcom_pitch)
    print("\nGenerated Outline:")
    print(outline)
    wait_for_confirmation("Review the outline above. Ready to validate it?")
    
    # Validate outline
    print("\nValidating outline...")
    validation_result = validate_episode_outline(client, sitcom_pitch, outline)
    print(validation_result)
    print("Outline validation successful!")
    wait_for_confirmation("Ready to start generating scenes?")
    
    # Generate scenes
    print("\nGenerating scenes...")
    scenes = []
    
    # Generate Scene 1
    print("\nGenerating Scene 1...")
    scene_1_desc = extract_scene(outline, 1)
    print("\nScene 1 Description:")
    print(scene_1_desc)
    script_title = extract_title(outline)
    scene1 = generate_scene_1_script(
        client=client,
        sitcom_title=script_title,
        scene_description=scene_1_desc,
        scene_index=0
    )
    print("\nGenerated Scene 1:")
    print(scene1)
    scenes.append(scene1)
    
    # Summarize Scene 1 and add to vector database
    print("\nSummarizing Scene 1...")
    scene_1_summary = summarize_scene(client, script_title, scene1)
    
    # Add Scene 1 to vector database
    print("\nAdding Scene 1 to vector database...")
    add_scene_to_vector_db(
        scene_1_summary,
        full_script=scene1,
        embedding_model=embedding_model,
        index=index,
        vector_metadata=scene_metadata
    )
    
    # Display vector database status
    print("\nTotal scenes stored in vector DB:", len(scene_metadata))
    print("\nScene 1 Metadata:")
    print("Summary:", scene_metadata[0]["summary"])
    print("Characters:", scene_metadata[0]["characters"])
    print("Location:", scene_metadata[0]["location"])
    print("Recurring Joke:", scene_metadata[0]["recurring_joke"])
    print("Emotional Tone:", scene_metadata[0]["emotional_tone"])
    
    wait_for_confirmation("Review Scene 1 above. Ready to generate additional scenes?")
    
    # Generate remaining scenes
    num_scenes = int(input("\nHow many additional scenes would you like to generate? "))
    
    for i in range(num_scenes):
        scene_desc = extract_scene(outline, i+2)
        print(f"\nDescription of {scene_desc}")
        
        character_agent = CharacterAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=1  # optional — defaults to 1
        )

        character_histories, is_consistent, explanation, char_recommendations, thoughts = character_agent.run(
            scene_description=scene_desc,
            scene_number=i+2
        )

        print(f"\nScene {i+2} Character Evaluation:")
        
        print(f"\nConsistency: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}")

        print("\nExplanation:\n", explanation)

        print("\nInteraction Improvement Recommendations:\n", char_recommendations)

        print("\nAgent's Internal Thoughts:")
        for thought in thoughts:
            print("-", thought)

        comedic_agent = ComedicAgent(
            client=client,
            vector_metadata=scene_metadata
        )

        # Run the full ReAct loop
        is_consistent, analysis_text, com_recommendations, thoughts = comedic_agent.run(
            scene_description=scene_desc,
            scene_number=i+2
        )

        # Print formatted output
        print(f"\nScene {i+2} Comedic Evaluation")

        print(f"\nScene {i+2} — Comedic Tone: {'✅ Consistent' if is_consistent else '❌ Inconsistent'}")

        print("\nComedic Tone Analysis:\n", analysis_text)

        print("\nComedic Improvement Recommendations:\n", com_recommendations)

        print("\nComedic Agent's Internal Thoughts:")
        for thought in thoughts:
            print("-", thought)

        # Initialize the environment agent
        environment_agent = EnvironmentReActAgent(
            client=client,
            vector_metadata=scene_metadata,  # prior scene metadata
            num_scenes=3  # how many scenes to look back
        )

        # Run the ReAct cycle for scene 2
        environment_analysis, transition_check, environment_details_suggestions, env_thoughts = environment_agent.run(
            scene_description=scene_desc,
            scene_number=i+2
        )

        # Display the results
        print(f"\nScene {i+2} Environment Evaluation")

        print(f"\nScene {i+2} — Environment Analysis:")
        print(environment_analysis)

        print(f"\nScene {i+2} — Environment Transition:")
        print(transition_check)

        print("\nEnvironment Detail Suggestions:\n", environment_details_suggestions)

        print("\nEnvironment Agent's Internal Thoughts:")
        for thought in env_thoughts:
            print("-", thought)

        scene_planner_agent = ScenePlannerAgent(client=client)

        scene_plan = scene_planner_agent.plan_next_scene_explicit(
            character_recommendations=char_recommendations,
            comedic_recommendations=com_recommendations,
            environment_details_suggestions=environment_details_suggestions,
            scene_number=i+2
        )

        print(scene_plan)

        scene_script = generate_scene(
            client=client,
            scene_plan=scene_plan,
            scene_number= 2
        )

        print(scene_script)

        scene_metadata_next = summarize_scene(
            client=client,
            sitcom_title=script_title,
            scene_script=scene_script
        )

        add_scene_to_vector_db(
            scene_metadata_next,
            full_script=scene_script,
            embedding_model=embedding_model,
            index=index,
            vector_metadata=scene_metadata
        )

        print("Total scenes stored in vector DB:", index.ntotal, "\n")

        print(f"\nScene {i+2}")
        print("Summary:", scene_metadata_next["summary"])
        print("Characters:", scene_metadata_next["characters"])
        print("Location:", scene_metadata_next["location"])
        print("Recurring Joke:", scene_metadata_next["recurring_joke"])
        print("Emotional Tone:", scene_metadata_next["emotional_tone"])

        
        '''
        if i < num_scenes - 1:  # Don't wait after the last scene
            wait_for_confirmation(f"Review Scene {i+2} above. Ready to generate the next scene?") '''
    
    # Save the complete script
    script_title = extract_title(outline)
    print(f"\nSaving complete script to {script_title}.txt...")
    with open(f"{script_title}.txt", 'w') as f:
        f.write("\n\n".join(scenes))
    
    print(f"\nScript has been saved to {script_title}.txt")
    print("\nThank you for using the Sitcom Generator!")

if __name__ == "__main__":
    main() 