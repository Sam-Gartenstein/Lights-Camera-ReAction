
from sentence_transformers import SentenceTransformer
import numpy as np


def summarize_scene(client, sitcom_title, scene_script):
    """
    Summarizes a sitcom scene and extracts structured metadata.

    Args:
        client: OpenAI client instance
        sitcom_title (str): Title of the sitcom
        scene_script (str): Full text of the generated scene

    Returns:
        dict with keys:
            - summary (str)
            - characters (list of str)
            - location (str or None)
            - recurring_joke (str or None)
            - emotional_tone (str)
    """
    prompt = f"""
You are the head writer of a sitcom called "{sitcom_title}".

Given the following scene script, extract:

1. A concise summary (100–150 words) describing:
   - Key actions and beats
   - Character relationships and development
   - Any important dialogue, props, or setups

2. A list of character names who appear or speak

3. The main location of the scene, if clearly stated (e.g., "locksmith shop", "kitchen", "car interior")

4. Any recurring joke or callback that appears in the scene (if applicable)

5. The emotional tone of the scene in one or two words (e.g., "hopeful", "awkward", "chaotic", "sweet")

Format your output as:

Summary:
<summary>

Characters:
- Character1
- Character2
*Note* THis is not capped at two

Location:
<location or "Unknown">

Recurring Joke:
<description or "None">

Emotional Tone:
<tone>

Scene:
{scene_script}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        top_p=1
    )

    output = response.choices[0].message.content.strip()

    # Basic parsing (relies on expected format)
    sections = output.split("\n\n")
    parsed = {
        "summary": "",
        "characters": [],
        "location": None,
        "recurring_joke": None,
        "emotional_tone": None
    }

    for section in sections:
        if section.startswith("Summary:"):
            parsed["summary"] = section.replace("Summary:", "").strip()
        elif section.startswith("Characters:"):
            parsed["characters"] = [line.strip("- ").strip() for line in section.splitlines()[1:] if line.strip()]
        elif section.startswith("Location:"):
            parsed["location"] = section.replace("Location:", "").strip()
        elif section.startswith("Recurring Joke:"):
            parsed["recurring_joke"] = section.replace("Recurring Joke:", "").strip()
        elif section.startswith("Emotional Tone:"):
            parsed["emotional_tone"] = section.replace("Emotional Tone:", "").strip()

    return parsed


def add_scene_to_vector_db(scene_metadata, full_script=None, embedding_model=None, index=None, vector_metadata=None):
    """
    Stores a scene's summary and metadata into the vector database.

    Args:
        scene_metadata (dict): Output of summarize_scene()
        full_script (str): (Optional) Raw script text
        embedding_model: Model to encode the summary
        index: FAISS index to store the vector
        vector_metadata: List to store metadata for retrieval
    """
    if embedding_model is None or index is None or vector_metadata is None:
        raise ValueError("embedding_model, index, and vector_metadata must all be provided.")

    summary = scene_metadata["summary"]
    embedding = embedding_model.encode(summary)

    index.add(np.array([embedding]))

    vector_metadata.append({
        "summary": summary,
        "characters": scene_metadata["characters"],
        "location": scene_metadata["location"],
        "recurring_joke": scene_metadata["recurring_joke"],
        "emotional_tone": scene_metadata["emotional_tone"],
        "script": full_script
    })


def store_scene_in_vector_db(
    client,
    sitcom_title,
    scene_script,
    embedding_model,
    index,
    vector_metadata
):
    """
    Summarizes a sitcom scene and adds it to a vector database.

    Args:
        client: The language model client used for summarization.
        sitcom_title (str): Title of the sitcom.
        scene_script (str): Full scene script.
        embedding_model: Embedding model used to encode the summary.
        index: FAISS or other vector index for similarity search.
        vector_metadata (list): List storing metadata for all stored scenes.

    Returns:
        None. Prints summary and updates the vector DB and metadata list.
    """
    # Summarize scene
    scene_summary = summarize_scene(
        client=client,
        sitcom_title=sitcom_title,
        scene_script=scene_script
    )

    # Add to vector database
    add_scene_to_vector_db(
        scene_summary,
        full_script=scene_script,
        embedding_model=embedding_model,
        index=index,
        vector_metadata=vector_metadata
    )

    # Print confirmation and metadata
    print("Total scenes stored in vector DB:", index.ntotal, "\n")

    for i, meta in enumerate(vector_metadata):
        print(f"\nScene {i + 1}")
        print("Summary:", meta["summary"])
        print("Characters:", meta["characters"])
        print("Location:", meta["location"])
        print("Recurring Joke:", meta["recurring_joke"])
        print("Emotional Tone:", meta["emotional_tone"])
