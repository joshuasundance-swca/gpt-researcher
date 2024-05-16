from gpt_researcher.master.functions import stream_output
from langchain.load.dump import dumps
from colorama import Fore, Style
from enum import Enum


class AgentColor(Enum):
    RESEARCHER = Fore.LIGHTBLUE_EX
    EDITOR = Fore.YELLOW
    WRITER = Fore.LIGHTGREEN_EX
    PUBLISHER = Fore.MAGENTA
    REVIEWER = Fore.CYAN
    REVISOR = Fore.LIGHTWHITE_EX
    MASTER = Fore.LIGHTYELLOW_EX


def print_agent_output(output: str, agent: str="RESEARCHER"):
    print(f"{AgentColor[agent].value}{agent}: {output}{Style.RESET_ALL}")


async def stream_agent_output(websocket, output: str, agent: str="RESEARCHER"):
    data_dict = {
        "agent": agent,
        "output": output
    }
    data_json = dumps(data_dict) + "\n"
    data_bytes = data_json.encode()
    if websocket:
        await websocket.send_bytes(data_bytes)
    else:
        print_agent_output(output, agent)
# async def stream_output(type, output, websocket=None, logging=True):
