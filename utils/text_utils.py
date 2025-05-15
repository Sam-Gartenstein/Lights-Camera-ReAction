import re
from IPython.display import display, Markdown


def display_markdown_output(text):
    """Displays Markdown text in a Jupyter/Colab notebook."""
    display(Markdown(text))


def extract_scene(outline_text, scene_number):
    """Extracts a specific scene from a multi-scene outline based on scene number."""
    pattern = rf"(Scene {scene_number}:(.*?))(?=\nScene {scene_number + 1}:|\Z)"
    match = re.search(pattern, outline_text, re.DOTALL)
    return match.group(1).strip() if match else None


def extract_title(text):
    """Extracts the sitcom title from a string that starts with 'Title: "Your Title"'."""
    for line in text.splitlines():
        if line.startswith("Title:"):
            start_quote = line.find('"')
            end_quote = line.rfind('"')
            if start_quote != -1 and end_quote != -1 and end_quote > start_quote:
                return line[start_quote + 1:end_quote]
    return None


def get_episode_concept(outline_text):
    """
    Extracts the episode concept from a pilot episode outline.

    This utility is used in the **evaluation notebook** to isolate the episode's premise from
    the rest of the scene breakdown. It assumes that the concept is labeled with the header
    'Episode Concept:' and ends at the beginning of the first scene summary (e.g., 'Scene 1').

    Args:
        outline_text (str): Full text of the pilot episode outline, including the concept and scenes.

    Returns:
        str: The episode concept extracted from the outline. If not found, returns a fallback message.
    """
    marker = "Episode Concept:"
    if marker in outline_text:
        start = outline_text.find(marker) + len(marker)
        end = outline_text.find("Scene", start)
        concept = outline_text[start:end].strip()
        return concept
    else:
        return "Episode concept not found."


def get_scene_description_block(outline_text, block_size=4):
    """
    Parses a full sitcom episode outline and returns scene descriptions organized into sequential blocks.

    This utility is commonly used in the **evaluation notebook** to split a 20-scene outline
    into smaller groups (e.g., blocks of 4) for structured analysis or model evaluation.
    Each scene is extracted with its number, title, and description.

    Scene format must follow:
        Scene <number>: "<Scene Title>" <description>

    Args:
        outline_text (str): Full pilot episode outline including all numbered scenes.
        block_size (int): Number of scenes to include in each block (default = 4).

    Returns:
        List[List[Dict]]: A list of scene blocks. Each block is a list of dictionaries with:
            - 'scene_number' (int)
            - 'scene_title' (str)
            - 'scene_description' (str)
    """
    scene_pattern = re.compile(r"Scene (\d+): \"(.+?)\"\s+(.+?)(?=Scene \d+:|$)", re.DOTALL)
    scenes = scene_pattern.findall(outline_text)

    # Convert to list of dicts
    scene_list = [
        {
            "scene_number": int(num),
            "scene_title": title.strip(),
            "scene_description": desc.strip()
        }
        for num, title, desc in scenes
    ]

    # Break into blocks
    blocks = [
        scene_list[i:i+block_size]
        for i in range(0, len(scene_list), block_size)
    ]

    return blocks


def extract_and_partition_scenes(text, block_size=5):
    """
    Extracts and partitions full sitcom scenes from a single text blob using custom scene headers.

    This utility is typically used to break down long-form sitcom scripts into smaller, manageable
    blocks for batch evaluation. It assumes that each scene starts with a markdown-style header
    in the format: '### Scene <number> ###'.

    The function:
    - Splits scenes based on those headers.
    - Reconstructs scene chunks with their headers and body text.
    - Sorts the scenes by scene number.
    - Returns a dictionary where each key is a scene block label (e.g., 'block_1') and each value is a list of scenes.

    Args:
        text (str): Full text containing multiple scenes, separated by '### Scene X ###' headers.
        block_size (int): Number of scenes per block (default = 5).

    Returns:
        Dict[str, List[str]]: Dictionary with keys like 'block_1', each mapping to a list of scene strings.

    Raises:
        ValueError: If scene headers are not properly formatted or no scenes are found.
    """
    # Split using headers and retain them
    raw_scenes = re.split(r'(### Scene \d+ ###)', text)

    # Combine headers and content
    scenes = []
    for i in range(1, len(raw_scenes), 2):
        header = raw_scenes[i].strip()
        body = raw_scenes[i + 1].strip() if i + 1 < len(raw_scenes) else ''
        scenes.append(f"{header}\n{body}")

    # Sort by scene number
    scenes.sort(key=lambda s: int(re.search(r'Scene (\d+)', s).group(1)))

    # Build dictionary of blocks
    blocks = {}
    for i in range(0, len(scenes), block_size):
        block_num = i // block_size + 1
        blocks[f"block_{block_num}"] = scenes[i:i + block_size]

    return blocks
