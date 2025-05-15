from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os
from utils.outline_generation import generate_sitcom_pitch, generate_pilot_episode_outline
from utils.script_review import validate_episode_outline
from utils.screen_writing import generate_scene_1_script, generate_scene
from utils.text_utils import extract_scene, extract_title
from utils.vector_db_utils import summarize_scene, add_scene_to_vector_db
from sentence_transformers import SentenceTransformer
import faiss
from utils.agents.character_agent import CharacterAgent
from utils.agents.comedy_agent import ComedicAgent
from utils.agents.environment_agent import EnvironmentAgent
from utils.agents.scene_planner_agent import ScenePlannerAgent

app = Flask(__name__)
CORS(app)
load_dotenv()

# Initialize embedding model and FAISS index once (global)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = embedding_model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)
scene_metadata = []  # In-memory metadata list

def setup_openai(api_key):
    openai.api_key = api_key
    return openai.OpenAI(api_key=api_key)

@app.route('/api/generate-concept', methods=['POST'])
def generate_concept():
    data = request.json
    api_key = data.get('apiKey')
    keywords = data.get('keywords')
    
    # Handle both dict and list for keywords
    if isinstance(keywords, list):
        keywords = {"keywords": keywords}
    if not isinstance(keywords, dict):
        return jsonify({'error': 'Keywords must be a dictionary or list'}), 400
    
    if not api_key:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Flatten keywords dict to a list
        keywords_dict = {}
        for category, words in keywords.items():
            if isinstance(words, list):
                keywords_dict[category] = [w.strip() for w in words if w.strip()]
            elif isinstance(words, str):
                keywords_dict[category] = [w.strip() for w in words.split(',') if w.strip()]
            else:
                keywords_dict[category] = []

        # Pass None if all lists are empty
        if not any(keywords_dict.values()):
            keywords_dict = None

        sitcom_pitch = generate_sitcom_pitch(client, keywords_dict)
        return jsonify({'concept': sitcom_pitch})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-outline', methods=['POST'])
def generate_outline():
    data = request.json
    api_key = data.get('apiKey')
    concept = data.get('concept')
    
    if not api_key or not concept:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        outline = generate_pilot_episode_outline(client, concept)
        return jsonify({'outline': outline})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-outline', methods=['POST'])
def validate_outline():
    data = request.json
    api_key = data.get('apiKey')
    concept = data.get('concept')
    outline = data.get('outline')
    
    if not api_key or not concept or not outline:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        client = openai.OpenAI(api_key=api_key)
        validation = validate_episode_outline(client, concept, outline)
        return jsonify({'validation': validation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-scene-1', methods=['POST'])
def generate_scene_1():
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    if not api_key or not outline:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        client = openai.OpenAI(api_key=api_key)
        scene_1_desc = extract_scene(outline, 1)
        script_title = extract_title(outline)
        scene1 = generate_scene_1_script(
            client=client,
            sitcom_title=script_title,
            scene_description=scene_1_desc,
            scene_index=0
        )
        return jsonify({'scene1': scene1})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-scene/<int:scene_number>', methods=['POST'])
def generate_scene_route(scene_number):
    # Validate scene number
    if scene_number < 2 or scene_number > 20:
        return jsonify({'error': 'Scene number must be between 2 and 20'}), 400
    
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    previous_scene = data.get('previousScene')
    writers_room_results = data.get('writersRoomResults')
    
    if not api_key or not outline or not previous_scene or not writers_room_results:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # Initialize scene planner agent
        scene_planner_agent = ScenePlannerAgent(client=client)
        
        # Use the recommendations from writer's room
        scene_plan = scene_planner_agent.plan_next_scene(
            character_recommendations=writers_room_results['character']['recommendations'],
            comedic_recommendations=writers_room_results['comedic']['recommendations'],
            environment_recommendations=writers_room_results['environment']['details_suggestions'],
            scene_number=scene_number
        )
        
        # Generate the scene using the scene plan
        scene = generate_scene(
            client=client,
            scene_plan=scene_plan,
            scene_number=scene_number
        )
        
        return jsonify({f'scene{scene_number}': scene})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scene-vector-info/<int:scene_number>', methods=['POST'])
def scene_vector_info(scene_number):
    # Validate scene number
    if scene_number < 1 or scene_number > 20:
        return jsonify({'error': 'Scene number must be between 1 and 20'}), 400
    
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    scene_script = data.get('sceneScript')
    
    if not api_key or not outline or not scene_script:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        script_title = extract_title(outline)
        scene_summary = summarize_scene(client, script_title, scene_script)
        
        # Add to vector DB with real model and index
        add_scene_to_vector_db(
            scene_summary,
            full_script=scene_script,
            embedding_model=embedding_model,
            index=index,
            vector_metadata=scene_metadata
        )
        
        # Return the info for the scene
        info = scene_metadata[-1]  # Use the last added scene
        return jsonify({
            'summary': info.get('summary', ''),
            'characters': ', '.join(info.get('characters', [])),
            'location': info.get('location', ''),
            'recurring_joke': info.get('recurring_joke', ''),
            'emotional_tone': info.get('emotional_tone', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scene-writers-room/<int:scene_number>', methods=['POST'])
def scene_writers_room(scene_number):
    # Validate scene number
    if scene_number < 1 or scene_number > 20:
        return jsonify({'error': 'Scene number must be between 1 and 20'}), 400
    
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    
    if not api_key or not outline:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Extract scene description
        scene_desc = extract_scene(outline, scene_number + 1)  # Get next scene's description
        # Character Agent
        character_agent = CharacterAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=3
        )
        character_histories, char_is_consistent, char_explanation, char_recommendations, char_thoughts = character_agent.run(
            scene_description=scene_desc,
            scene_number=scene_number + 1
        )        
        # Comedic Agent
        comedic_agent = ComedicAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=3
        )
        com_context, com_is_consistent, com_analysis_text, com_recommendations, com_thoughts = comedic_agent.run(
            scene_description=scene_desc,
            scene_number=scene_number + 1
        )
        
        # Environment Agent
        environment_agent = EnvironmentAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=3
        )
        context, env_is_consistent, env_explanation, env_recommendations, env_thoughts = environment_agent.run(
            scene_description=scene_desc,
            scene_number=scene_number + 1
        )
        return jsonify({
            'character': {
                'is_consistent': char_is_consistent,
                'explanation': char_explanation,
                'recommendations': char_recommendations,
                'thoughts': char_thoughts
            },
            'comedic': {
                'is_consistent': com_is_consistent,
                'analysis': com_analysis_text,
                'recommendations': com_recommendations,
                'thoughts': com_thoughts
            },
            'environment': {
                'is_consistent': env_is_consistent,
                'explanation': env_explanation,
                'details_suggestions': env_recommendations,
                'thoughts': env_thoughts
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scene-1-writers-room', methods=['POST'])
def scene_1_writers_room():
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    
    if not api_key or not outline:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Extract scene 2 description since we're planning scene 2
        scene_desc = extract_scene(outline, 2)
        
        # Character Agent
        character_agent = CharacterAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=1  # Only look at scene 1 since it's the first scene
        )
        character_histories, char_is_consistent, char_explanation, char_recommendations, char_thoughts = character_agent.run(
            scene_description=scene_desc,
            scene_number=2  # Planning scene 2
        )
        
        # Comedic Agent
        comedic_agent = ComedicAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=1
        )
        com_context, com_is_consistent, com_analysis_text, com_recommendations, com_thoughts = comedic_agent.run(
            scene_description=scene_desc,
            scene_number=2  # Planning scene 2
        )
        
        # Environment Agent
        environment_agent = EnvironmentAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=1  # Only look at scene 1 since it's the first scene
        )
        context, env_is_consistent, env_explanation, env_recommendations, env_thoughts = environment_agent.run(
            scene_description=scene_desc,
            scene_number=2  # Planning scene 2
        )
        
        return jsonify({
            'character': {
                'is_consistent': char_is_consistent,
                'explanation': char_explanation,
                'recommendations': char_recommendations,
                'thoughts': char_thoughts
            },
            'comedic': {
                'is_consistent': com_is_consistent,
                'analysis': com_analysis_text,
                'recommendations': com_recommendations,
                'thoughts': com_thoughts
            },
            'environment': {
                'is_consistent': env_is_consistent,
                'explanation': env_explanation,
                'details_suggestions': env_recommendations,
                'thoughts': env_thoughts
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 