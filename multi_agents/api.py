import logging
import os
from glob import glob

import fastapi
from fastapi.responses import FileResponse

from agents import ChiefEditorAgent
from task import TaskModel, TaskRequest

app = fastapi.FastAPI()
logger = logging.getLogger(__name__)


@app.post("/run_research_task")
async def run_research_task(task: TaskRequest) -> FileResponse:
    _task = TaskModel.from_task_request(task).dict()

    chief_editor = ChiefEditorAgent(_task)

    _ = await chief_editor.run_research_task()

    output_files = glob(
        os.path.join(chief_editor.output_dir, "**", "*"), recursive=True
    )
    if len(output_files) == 0:
        raise FileNotFoundError("No output files found")
    elif len(output_files) > 1:
        logger.warning(
            f"Multiple output files found: {output_files}. "
            f"Returning the first file: {output_files[0]}"
        )
    return FileResponse(
        path=output_files[0],
    )


# import requests
#
# p = {
#   "query": "increased flooding risks due to climate change in Astor, FL",
#   "max_sections": 3,
#   "follow_guidelines": False,
#   "model": "gpt-4-turbo",
#   "guidelines": [],
#   "verbose": True,
#   "output_file_format": "docx"
# }
#
# url = "http://localhost:8001"
#
# response = requests.post(url + "/run_research_task", json=p)
#
# with open("output.docx", "wb") as f:
#     f.write(response.content)
#
