import logging

from langchain_core.runnables import chain

from agents import ChiefEditorAgent
from task import TaskModel, TaskRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")


def query_to_task(query: str) -> dict:
    r = TaskRequest(
        query=query,
        max_sections=3,
        follow_guidelines=False,
        model="gpt-4o",
        guidelines=[],
        verbose=True,
        output_file_format="docx",
    )
    m = TaskModel.from_task_request(r)
    d = m.dict()
    return d


@chain
async def custom_chain(query: str):
    task_d = query_to_task(query)
    chief_editor = ChiefEditorAgent(task_d)
    return await chief_editor.run_research_task()
