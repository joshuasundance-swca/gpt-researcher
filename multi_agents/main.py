import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from agents import ChiefEditorAgent
from task import task_from_file, args_to_task, get_args, TaskModel


load_dotenv()

# Run with LangSmith if API key is set
if os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = "true"


async def main(task: Optional[TaskModel] = None, task_json_file: str = "task.json"):
    task_d = task.model_dump() if task else task_from_file(task_json_file)

    chief_editor = ChiefEditorAgent(task_d)
    research_report = await chief_editor.run_research_task()

    return research_report


if __name__ == "__main__":
    args = get_args()
    task = args_to_task(args)
    _ = asyncio.run(main(task))
