import logging
import os
from glob import glob
from langchain.load.dump import dumps
import fastapi
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langserve import add_routes
from agents import ChiefEditorAgent, init_research_team_from_args
from simple_wrapper import query_to_task, custom_chain
from task import TaskModel, TaskRequest

app = fastapi.FastAPI()
logger = logging.getLogger(__name__)


add_routes(app, custom_chain, path="/run_research_query")


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


async def tuple_generator(task: dict, websocket=None):
    chief_editor = ChiefEditorAgent(task, websocket)
    output_dir = chief_editor.output_dir
    chain = init_research_team_from_args(output_dir, websocket)
    chain_input = {"task": task}
    chain_stream = chain.astream_events(
        chain_input,
        version="v1",
    )
    try:
        async for output in chain_stream:
            include_types = [
                "on_chain_end",
                "on_chat_model_end",
                "on_llm_end",
                # 'on_tool_end',
                # 'on_retriever_end',
                "on_prompt_end",
            ]
            if output.get("event", "") in include_types:
                print(str(output))
                chunk = dumps(output) + "\n"
                yield chunk.encode()
    except Exception as e:
        print(f"Error: {str(e)}")
        error_message = dumps({"error": str(e)}) + "\n"
        yield error_message.encode()
        raise e


class Req(BaseModel):
    query: str


@app.post("/stream-tuples")
async def stream_tuples(query: Req):
    task = query_to_task(query.query)
    return StreamingResponse(tuple_generator(task), media_type="application/json")


@app.websocket("/ws")
async def ws_tuples(websocket: fastapi.WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()  # Receive JSON data
            print(f"Received data: {data}")
            query = data.get("query", "")
            task = query_to_task(query)
            if not query:
                error_data = dumps({"message": "Query not found"}) + "\n"
                await websocket.send_bytes(error_data.encode())
                break
            async for chunk in tuple_generator(task, websocket):
                await websocket.send_bytes(chunk)
            break
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
    finally:
        await websocket.close()
