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
