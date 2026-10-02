from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import asyncio
from blade import create_agent, tools_name

from langchain_core.output_parsers import StrOutputParser
from blade.tools import *
from langchain_core.messages import HumanMessage, ToolMessage
from blade.prompts import system_message

MAX_TOOL_USE = int(os.getenv("MAX_TOOL_USE"))

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="SomeBody New"
    )

    await bot.change_presence(
        activity=activity,
        status=discord.Status.dnd
    )

    print(f"Bot is ready as {bot.user}")





class ToolView(discord.ui.View):
    def __init__(self, tool_count: int, tools_used: list[str]):
        super().__init__(timeout=120)

        self.tools_used = tools_used

        # Informational button
        self.add_item(
            discord.ui.Button(
                label=f"Tools used: {tool_count}",
                style=discord.ButtonStyle.secondary,
                disabled=True
            )
        )

        # Tool list button
        button = discord.ui.Button(
            label="Tool list",
            emoji="🛠️",
            style=discord.ButtonStyle.primary
        )

        button.callback = self.show_tools
        self.add_item(button)

    async def show_tools(self, interaction: discord.Interaction):
        if self.tools_used:
            tools = "\n".join(
                f"• `{tool}`"
                for tool in self.tools_used
            )
        else:
            tools = "No tools were used."

        embed = discord.Embed(
            title="Tools used",
            description=tools,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

@bot.command()
async def chat(ctx):

    if ctx.author == bot.user:
        return

    msg = ctx.message.content

    response, tool_count, tools_used = get_response_from_agent(
        query=str(msg)
    )

    await ctx.send(
        response,
        view=ToolView(tool_count, tools_used)
    )



def get_response_from_agent(query : str):
    agent = create_agent()

    message = []
    message.append(system_message) # Adding system Message
    parser = StrOutputParser()

    message.append(HumanMessage(content=query))

    result = agent.invoke(message)
    message.append(result)

    tool_used = 0
    tools_used = []
    while result.tool_calls:
        
        if tool_used > MAX_TOOL_USE:
            print("Error: Too Many Tools Called, set MAX_TOOL_USE more than 10.")
            break

        tool_call_info = result.tool_calls[0]

        chosen_tool = tools_name[tool_call_info["name"]]
        tools_used.append(tool_call_info["name"])

        tool_result = chosen_tool.invoke(
            tool_call_info["args"]
        )

        tool_message = ToolMessage(
            content=str(tool_result),
            tool_call_id=tool_call_info["id"],
        )

        message.append(tool_message)
        
        result = agent.invoke(message)
        
        message.append(result)
        tool_used += 1

    response = parser.invoke(result)
    return response, tool_used, tools_used

    
bot.run(TOKEN)