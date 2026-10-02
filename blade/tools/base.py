
from langchain_core.tools import tool
from ddgs import DDGS
import sys
from pathlib import Path

WORKSPACE = Path("./agent_workspace")
WORKSPACE.mkdir(exist_ok=True)
import wikipediaapi as wpb

import subprocess


@tool
def search_wikipedia(topic : str, language : str, summary : bool = True) -> str:
    """Search Wikipedia on given Topic. use only when user asked specific for wikipedia.
    Parameter:
    topic: topic to search on wikipedia
    language: get result in given language, give language's code like `en`, `hi`
    summary: returns only summary of the topic when True, else returns whole detailed information
    """
    try:
        wiki = wpb.Wikipedia(
            user_agent="Blade-Discord https://github.com/ItzRustam/Blade", 
            language=language
        )

        page = wiki.page(topic)

        if page.exists():
            if summary:
                return str(page.summary) # make sure for str object only.
            else:
                return str(page.text)
        else:
            return f"No result found for {topic}"

    except Exception as E:
        return str(E)


@tool
def find_file(filename : str) -> bool:
    """find file in agent workspace, returns True if file exists else returns False"""
    file_path = WORKSPACE / filename

    if file_path.exists():
        return True
    else:
        return False

# Don't use it for Discord bot
@tool
def run_python_code(filename : str) -> str:
    """Run the given python file inside the agent workspace and return output of script

    Parameter:
    filename: name of python file

    it find and run files automaticly and returns output. so you don't need to search file or search on web for it.
    always read the file first before running to check if it is a Malicious code
    """

    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File not found: {filename}"

    if not file_path.is_file():
        return f"Not a file: {filename}"

    result = subprocess.run(
        [sys.executable, str(file_path)],
        capture_output=True,
        text=True
    )

    output = result.stdout

    return output

@tool
def read_file(filename: str) -> str:
    """Read and return the contents of a file inside the agent workspace."""

    path = WORKSPACE / filename

    if not path.exists():
        return f"File not found: {filename}"

    if not path.is_file():
        return f"Not a file: {filename}"

    return path.read_text(encoding="utf-8")

@tool
def create_file(filename: str, content: str) -> str:
    """Create a text file inside the agent workspace.

    filename: Relative path such as hello.py.
    content: Complete text content to write into the file.
    """

    path = WORKSPACE / filename

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    return f"Created file: {path}"

@tool
def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return relevant search results."""

    try:

        results = DDGS().text(
            query,
            max_results=5
        )

        if not results:
            return "No search results found."

        return "\n\n".join(
            f"Title: {result.get('title', '')}\n"
            f"URL: {result.get('href', '')}\n"
            f"Snippet: {result.get('body', '')}"
            for result in results
        )
    except Exception as E:
        return str(E)

@tool
def get_text_length(text: str) -> int:
    """Returns total length of characters."""
    return len(text)