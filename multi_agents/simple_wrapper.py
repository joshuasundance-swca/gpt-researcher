import logging

from langchain_core.runnables import chain

from agents import ChiefEditorAgent
from agents.utils.views import print_agent_output
from task import TaskModel, TaskRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")


def query_to_task(query: str) -> dict:
    logger.info(f"query_to_task: {query}")
    r = TaskRequest(
        query=query,
        max_sections=3,
        follow_guidelines=False,
        model="gpt-4-turbo",
        guidelines=[],
        verbose=True,
        output_file_format="docx",
    )
    logger.info("got r")
    m = TaskModel.from_task_request(r)
    logger.info("got m")
    d = m.dict()
    logger.info(d)
    return d


@chain
async def custom_chain(query: str):
    task_d = query_to_task(query)
    print_agent_output(
        f"Starting the research process for query '{task_d.get('query')}'...", "MASTER"
    )
    chief_editor = ChiefEditorAgent(task_d)
    return await chief_editor.run_research_task()
