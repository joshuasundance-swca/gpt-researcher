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


async def tuple_generator(task: dict):
    output_dir = "/usr/src/app/multi_agents/outputs"
    chain = init_research_team_from_args(task, output_dir)
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
                # yield str(output) + "\n"
                # yield json chunk
                chunk = dumps(output) + "\n"
                yield chunk.encode()
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
    # yield "EOF\n"
    eof = dumps({"event": "EOF"}) + "\n"
    yield eof.encode()


class Req(BaseModel):
    query: str


@app.post("/stream-tuples")
async def stream_tuples(query: Req):
    task = query_to_task(query.query)
    return StreamingResponse(tuple_generator(task), media_type="application/json")



# import requests
# import json
# from pprint import pprint
#
# url = "http://127.0.0.1:8001/stream-tuples"
# query = "indigenous history of Chuluota, FL"
# data2 = []
#
# with requests.post(url, json=dict(query=query), stream=True) as response:
#     for idx, line in enumerate(response.iter_lines()):
#         data = json.loads(line)
#         event = data.get("event", "")
#         if event == "EOF":
#             break
#         # if line.strip() == "EOF":
#         #     break
#         # print(idx, line)
#         print(event)
#         pprint(event)
#         print("\n\n-----\n\n")
#         data2.append(data)


# import requests
#
# p = {
#   "query": "increased flooding risks due to climate change in Astor, FL",
#   "max_sections": 3,
#   "follow_guidelines": False,
#   "model": "gpt-4o",
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

#browser dict_keys(['task', 'initial_research'])
#planner dict_keys(['title', 'date', 'sections'])
#publisher dict_keys(['report'])
#researcher dict_keys(['draft'])
#researcher dict_keys(['research_data'])
#reviewer dict_keys(['review'])
#writer dict_keys(['table_of_contents', 'introduction', 'conclusion', 'sources', 'headers'])



dd = {
    'browser': ['task', 'initial_research'],
    'planner': ['title', 'date', 'sections'],
    'researcher': ['draft', 'research_data'],
    'reviewer': ['review'],
    'writer': ['table_of_contents', 'introduction', 'conclusion', 'sources', 'headers'],
    'publisher': ['report'],
}

data4 = []
for d in data3:
    n = d.get("name")
    keys = dd.get(n, [])
    if keys:
        print(f"# {n}")
        print()
        o = d['data']['output']
        # data4.append(
        #     {
        #         "name": n,
        #         "data": d,
        #     }
        # )
        for k in keys:
            kd = o.get(k, {})
            if kd:
                data4.append(
                    {
                        "name": n,
                        "key": k,
                        "data": kd,
                    }
                )
                print(f"## {k}")
                pprint(kd)
        print("\n\n\n---------------------\n\n\n")


# recursively go through dict and print keys and types to infer schema
def infer_schema(data, prefix=""):
    print(data.get("name"))
    for k, v in data.items():
        if isinstance(v, dict):
            infer_schema(v, prefix + k + "_")
        else:
            print(f"{prefix}{k}: {type(v)}")
    print("\n\n")

# infer schema from list of dicts
def infer_schema_list(data):
    for d in data:
        infer_schema(d)



from typing import List, Union

"""browser
	name: <class 'str'>
	key: <class 'str'>
	data: <class 'str'>, dict, list
	data
		query: <class 'str'>
		max_sections: <class 'int'>
		follow_guidelines: <class 'bool'>
		model: <class 'str'>
		guidelines: <class 'list'>
		verbose: <class 'bool'>

		publish_formats
			docx: <class 'bool'>
			markdown: <class 'bool'>
			pdf: <class 'bool'>


planner
	name: <class 'str'>
	key: <class 'str'>
	data: <class 'str'>, <class 'list'>, dict

researcher
	name: <class 'str'>
	key: <class 'str'>
	data: <class 'list'>, str, dict
	researcher.data
		(arbitrary str key) Chuluota's Indigenous Legacy: <class 'str'>
		data_Early Indigenous Inhabitants: <class 'str'>
		data_European Contact and Its Impact: <class 'str'>


writer
	name: <class 'str'>
	key: <class 'str'>
	data: <class 'str'>, <class 'list'>, dict

	data_title: <class 'str'>
	data_date: <class 'str'>
	data_introduction: <class 'str'>
	data_table_of_contents: <class 'str'>
	data_conclusion: <class 'str'>
	data_references: <class 'str'>

publisher
	name: <class 'str'>
	key: <class 'str'>
	data: <class 'str'>
"""

for d in data4:
    n = d.get("name")
    if n == "browser":
        print("# browser")
        print()
        data = d.get("data")
        for k, v in data.items():
            print(f"## {k}")
            print(f"Type: {type(v)}")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"### {kk}")
                    print(f"Type: {type(vv)}")
            print("\n\n")
    elif n == "planner":
        print("# planner")
        print()
        data = d.get("data")
        for k, v in data.items():
            print(f"## {k}")
            print(f"Type: {type(v)}")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"### {kk}")
                    print(f"Type: {type(vv)}")
            print("\n\n")
    elif n == "researcher":
        print("# researcher")
        print()
        data = d.get("data")
        for k, v in data.items():
            print(f"## {k}")
            print(f"Type: {type(v)}")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"### {kk}")
                    print(f"Type: {type(vv)}")
            print("\n\n")
    elif n == "writer":
        print("# writer")
        print()
        data = d.get("data")
        for k, v in data.items():
            print(f"## {k}")
            print(f"Type: {type(v)}")
            if isinstance(v, dict):
                for kk, vv in v.items():
                    print(f"### {kk}")
                    print(f"Type: {type(vv)}")
            print("\n\n")
    elif n == "publisher":
        print("# publisher")
        print()
        data = d.get("data")
        print(f"Type: {type(data)}")
        print("\n\n")
    print("\n\n\n---------------------\n\n\n")




for d in data4:
    n = d.get("name")
    if n in ["writer", "publisher"]:
        continue
    print("# " + n)
    k = d.get("key")
    print("## "+ k)
    data = d.get("data")
    if isinstance(data, str):
        # print(data[:40])
        pass
    else:
        pprint(data)


def print_browser(data):
    task = data.get("task")
    initial_research = data.get("initial_research")
    if task:
        pprint(task)
    print()
    print(initial_research)

def print_planner(data):
    title = data.get("title")
    date = data.get("date")
    sections = data.get("sections")
    print(title)
    print(date)
    pprint(sections)

def print_researcher(data):
    draft = data.get("draft", {})
    for k,v in draft.items():
        print(k)
        print(v)
    research_data = data.get("research_data", {})
    for k,v in research_data.items():
        print(k)
        print(v)

for d in data3:
    n = d.get("name")
    if n == "browser":
        print_browser(d["data"]["output"])
    elif n == "planner":
        print_browser(d["data"]["output"])
    elif n == "researcher":
        print_browser(d["data"]["output"])
    elif n == "writer":
        pass
    elif n == "publisher":
        pass

data5 = []
for d in data3:
    n = d.get("name")
    covered = [
        "browser",
        "planner",
        "researcher",
        "LangGraph",
    ]
    if n not in covered:
        continue
    output = d["data"]["output"]
    data5.append((n, output))
    keys = dd.get(n, [])
    if keys:
        print(f"# {n}")
        print()
        o = d['data']['output']
        for k in keys:
            kd = o.get(k, {})
            if kd:
                data4.append(
                    {
                        "name": n,
                        "key": k,
                        "data": kd,
                    }
                )
                print(f"## {k}")
                pprint(kd)
        print("\n\n\n---------------------\n\n\n")

for d in data5:
    n, data = d
    if n == "browser":
        print(f"# {n}\n")
        task = data.get("task")
        if task:
            print(f"## task\n{task}\n")
        initial_research = data.get("initial_research")
        if initial_research:
            print(f"### initial research\n{initial_research}\n")
        print('\n\n\n---------------------\n\n\n')
    elif n == "planner":
        print(f"# {n}\n")
        title = data.get("title")
        date = data.get("date")
        sections = data.get("sections")
        print(f"## title\n{title}\n")
        print(f"## date\n{date}\n")
        print(f"## sections\n")
        for s in sections:
            print(f"- {s}")
        print()
        print('\n\n\n---------------------\n\n\n')
    elif n == "researcher":
        # key of d[1] may be 'draft' or 'research_data'
        # draft will be dict[str, str]
        # research data will be list[dict[str, str]]
        print(f"# {n}\n")
        draft = data.get("draft", {})
        for k,v in draft.items():
            print(f"## DRAFT {k}\n{v}\n")
        research_data = data.get("research_data", [])
        for rd in research_data:
            for k,v in rd.items():
                print(f"## RESEARCH DATA {k}\n{v}\n")
        print('\n\n\n---------------------\n\n\n')
    elif n == "LangGraph" and "publisher" in data.keys():
        report = data['publisher']['report']
        print("\n\n\n")
        print('FINAL REPORT')
        print('\n\n\n---------------------\n\n\n')
        print()
        print(report)
        print('\n\n\n---------------------\n\n\n')
