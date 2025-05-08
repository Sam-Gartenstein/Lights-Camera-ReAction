from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os
from utils.outline_generation import generate_sitcom_pitch, generate_pilot_episode_outline
from utils.script_review import validate_episode_outline
from utils.screen_writing import generate_scene_1_script
from utils.text_utils import extract_scene, extract_title
from utils.vector_db_utils import summarize_scene, add_scene_to_vector_db
from sentence_transformers import SentenceTransformer
import faiss
from utils.agents.character_agent import CharacterAgent
from utils.agents.comedy_agent import ComedicAgent
from utils.agents.environment_agents import EnvironmentReActAgent

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
    
    if not api_key:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Flatten keywords dict to a list
        keyword_list = []
        for category, words in keywords.items():
            if isinstance(words, list):
                keyword_list.extend(words)
            elif isinstance(words, str):
                keyword_list.extend([w.strip() for w in words.split(',') if w.strip()])
        # Pass None if no keywords entered
        if not keyword_list:
            keyword_arg = None
        else:
            keyword_arg = keyword_list
        sitcom_pitch = generate_sitcom_pitch(client, keyword_arg)
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

@app.route('/api/generate-scene', methods=['POST'])
def generate_scene():
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    scene_number = data.get('sceneNumber')
    
    if not api_key or not outline or not scene_number:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        client = setup_openai(api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative sitcom writer."},
                {"role": "user", "content": f"Write scene {scene_number} for this pilot episode outline: {outline}"}
            ]
        )
        
        return jsonify({'scene': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scene-1-vector-info', methods=['POST'])
def scene_1_vector_info():
    data = request.json
    api_key = data.get('apiKey')
    outline = data.get('outline')
    scene1_script = data.get('scene1Script')
    if not api_key or not outline or not scene1_script:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        client = openai.OpenAI(api_key=api_key)
        script_title = extract_title(outline)
        scene_1_summary = summarize_scene(client, script_title, scene1_script)
        # Add to vector DB with real model and index
        add_scene_to_vector_db(
            scene_1_summary,
            full_script=scene1_script,
            embedding_model=embedding_model,
            index=index,
            vector_metadata=scene_metadata
        )
        # Return the info for Scene 1
        info = scene_metadata[-1]  # Use the last added scene
        return jsonify({
            'summary': info.get('summary', ''),
            'characters': info.get('characters', ''),
            'location': info.get('location', ''),
            'recurring_joke': info.get('recurring_joke', ''),
            'emotional_tone': info.get('emotional_tone', '')
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
        # Extract scene 2 description (since scene 1 is already generated)
        scene_desc = extract_scene(outline, 2)
        # Character Agent
        character_agent = CharacterAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=1
        )
        character_histories, is_consistent, explanation, char_recommendations, thoughts = character_agent.run(
            scene_description=scene_desc,
            scene_number=2
        )
        # Comedic Agent
        comedic_agent = ComedicAgent(
            client=client,
            vector_metadata=scene_metadata
        )
        com_is_consistent, analysis_text, com_recommendations, com_thoughts = comedic_agent.run(
            scene_description=scene_desc,
            scene_number=2
        )
        # Environment Agent
        environment_agent = EnvironmentReActAgent(
            client=client,
            vector_metadata=scene_metadata,
            num_scenes=3
        )
        environment_analysis, transition_check, environment_details_suggestions, env_thoughts = environment_agent.run(
            scene_description=scene_desc,
            scene_number=2
        )
        return jsonify({
            'character': {
                'is_consistent': is_consistent,
                'explanation': explanation,
                'recommendations': char_recommendations,
                'thoughts': thoughts
            },
            'comedic': {
                'is_consistent': com_is_consistent,
                'analysis': analysis_text,
                'recommendations': com_recommendations,
                'thoughts': com_thoughts
            },
            'environment': {
                'analysis': environment_analysis,
                'transition': transition_check,
                'details_suggestions': environment_details_suggestions,
                'thoughts': env_thoughts
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return 'Backend is working!'

if __name__ == '__main__':
    app.run(debug=True, port=5000) 