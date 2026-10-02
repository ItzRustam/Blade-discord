from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from blade.tools import *
import os
from langchain_core.messages import HumanMessage, ToolMessage
from blade.prompts import system_message
from rich import print as rprint

load_dotenv()

MAX_TOOL_USE = int(os.getenv("MAX_TOOL_USE"))

tools_name = {
    "get_text_length": get_text_length,
    "web_search": web_search,
    "create_file": create_file,
    "read_file": read_file,
    'search_wikipedia':search_wikipedia,
    'find_file': find_file,
}

def create_agent():

    llm = ChatGoogleGenerativeAI(model=os.getenv("MODEL"))

    tools = [get_text_length, web_search, create_file, read_file, search_wikipedia, find_file]

    # Agent
    Agent = llm.bind_tools(tools=tools)

    return Agent

# Custom ReAct Architecture
def run_agent():
    rprint("[red]Blade is Here[/red]")
    # memory
    message = []
    message.append(system_message) # Adding system Message

    llm_with_tool = create_agent() # Initlizing Agent
    parser = StrOutputParser()

    while True:
        userInput = input("You: ")
        if userInput.lower() == "exit":
            break

        query = HumanMessage(content=userInput)
        message.append(query)

        result = llm_with_tool.invoke(message)

        message.append(result)

        tool_used = 0

        while result.tool_calls:
            if tool_used > MAX_TOOL_USE:
                print("Error: Too Many Tools Called, set MAX_TOOL_USE more than 10.")
                break

            tool_call_info = result.tool_calls[0]
            rprint("Current Tool: ", tool_call_info)

            chosen_tool = tools_name[tool_call_info["name"]]

            tool_result = chosen_tool.invoke(
                tool_call_info["args"]
            )

            tool_message = ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call_info["id"],
            )

            message.append(tool_message)

            result = llm_with_tool.invoke(message)

            message.append(result)
            tool_used += 1

        response = parser.invoke(result)
        rprint(response)
        rprint(f"Called: {tool_used} tools. ")

    rprint("Thanks for Using.")