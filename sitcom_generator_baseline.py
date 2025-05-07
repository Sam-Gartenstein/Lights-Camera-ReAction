import os
import sys
from getpass import getpass
from dotenv import load_dotenv
import openai

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

def generate_with_gpt(prompt, system_message="You are a creative writing assistant."):
    """Generate text using GPT-4."""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_sitcom_pitch(keywords):
    """Generate a sitcom concept from keywords."""
    prompt = f"""Create a unique sitcom concept using these keywords: {', '.join(keywords)}.
    Include:
    1. Title
    2. Premise
    3. Main characters and their relationships
    4. Setting
    5. Core conflicts
    Make it funny and original!"""
    
    return generate_with_gpt(prompt, "You are a creative TV show developer.")

def generate_pilot_outline(sitcom_pitch):
    """Generate a pilot episode outline."""
    prompt = f"""Based on this sitcom concept:
    {sitcom_pitch}
    
    Create a detailed outline for the pilot episode. Include:
    1. Opening scene
    2. 3-4 key scenes
    3. Character introductions
    4. Main conflict setup
    5. Resolution
    
    Format it clearly with scene numbers and brief descriptions."""
    
    return generate_with_gpt(prompt, "You are a TV show writer specializing in sitcoms.")

def generate_scene(outline, scene_number, previous_scenes=None):
    """Generate a single scene."""
    context = ""
    if previous_scenes:
        context = "\nPrevious scenes:\n" + "\n".join(previous_scenes[-3:])
    
    prompt = f"""Based on this pilot outline:
    {outline}
    {context}
    
    Write Scene {scene_number} in proper screenplay format. Include:
    - Scene heading
    - Character actions
    - Dialogue
    - Scene transitions
    
    Make it funny and engaging!"""
    
    return generate_with_gpt(prompt, "You are a professional sitcom writer.")

def main():
    """Main function to run the baseline sitcom generation pipeline."""
    # Setup API key
    api_key = setup_api_key()
    print("API key configured successfully!")
    wait_for_confirmation("Ready to start generating your sitcom?")
    
    # Generate sitcom concept
    print("\nGenerating sitcom concept...")
    keywords = input("Enter some creative keywords for your sitcom (comma-separated): ")
    keywords = [k.strip() for k in keywords.split(',')]
    
    sitcom_pitch = generate_sitcom_pitch(keywords)
    print("\nGenerated Sitcom Concept:")
    print(sitcom_pitch)
    wait_for_confirmation("Review the sitcom concept above. Ready to generate the pilot outline?")
    
    # Generate pilot episode outline
    print("\nGenerating pilot episode outline...")
    outline = generate_pilot_outline(sitcom_pitch)
    print("\nGenerated Outline:")
    print(outline)
    wait_for_confirmation("Review the outline above. Ready to start generating scenes?")
    
    # Generate scenes
    print("\nGenerating scenes...")
    scenes = []
    
    # Generate Scene 1
    print("\nGenerating Scene 1...")
    scene1 = generate_scene(outline, 1)
    print("\nGenerated Scene 1:")
    print(scene1)
    scenes.append(scene1)
    wait_for_confirmation("Review Scene 1 above. Ready to generate additional scenes?")
    
    # Generate remaining scenes
    num_scenes = int(input("\nHow many additional scenes would you like to generate? "))
    
    for i in range(num_scenes):
        print(f"\nGenerating Scene {i+2}...")
        new_scene = generate_scene(outline, i+2, scenes)
        print(f"\nGenerated Scene {i+2}:")
        print(new_scene)
        scenes.append(new_scene)
        
        if i < num_scenes - 1:  # Don't wait after the last scene
            wait_for_confirmation(f"Review Scene {i+2} above. Ready to generate the next scene?")
    
    # Save the complete script
    script_title = sitcom_pitch.split('\n')[0].strip()  # Use first line as title
    print(f"\nSaving complete script to {script_title}.txt...")
    with open(f"{script_title}.txt", 'w') as f:
        f.write("\n\n".join(scenes))
    
    print(f"\nScript has been saved to {script_title}.txt")
    print("\nThank you for using the Baseline Sitcom Generator!")

if __name__ == "__main__":
    main() 