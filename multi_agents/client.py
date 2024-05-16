import json

import websockets


async def stream_via_websocket(query: str) -> list[bytes]:
    data = []
    uri = "ws://localhost:8001/ws"  # Adjust the URL/port as necessary
    async with websockets.connect(uri) as websocket:
        # Prepare the data to send, must match the expected format by the server
        data_to_send = {"query": query}
        # Send JSON data
        await websocket.send(json.dumps(data_to_send))
        print("Sent:", data_to_send)
        try:
            # Keep receiving messages until the connection is closed by the server
            while True:
                response = await websocket.recv()
                print("Received:", response)
                print("\n\n\n-------------\n\n\n")
                data.append(response)
        except websockets.ConnectionClosed:
            print("Connection closed by the server.")
    return data


def extract_report(data: list[bytes]) -> str:
    last_bytes = data[-1]
    last_dict = json.loads(last_bytes.decode())
    name = last_dict.get("name")
    if name != "LangGraph":
        raise ValueError("Expected last message to be from LangGraph")
    try:
        report = last_dict["data"]["output"]["publisher"]["report"]
    except KeyError as e:
        raise RuntimeError(
            "failed to extract chunk.data.output.publisher.report"
        ) from e
    return report


## Run the client
# import asyncio
#
# query: str = "natural history of Georgia's Tallulah Gorge"
# data: list[bytes] = asyncio.run(stream_via_websocket(query))
# report: str = extract_report(data)


# url = "http://127.0.0.1:8001/stream-tuples"
# query = "history of Central Florida's Vietnamese population"
#
#
# def print_event_data(name: str, output_data: dict) -> None:
#     if name == "browser":
#         print(f"# {name}\n")
#         task = output_data.get("task")
#         if task:
#             print(f"## task\n{task}\n")
#         initial_research = output_data.get("initial_research")
#         if initial_research:
#             print(f"### initial research\n{initial_research}\n")
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "planner":
#         print(f"# {name}\n")
#         title = output_data.get("title")
#         date = output_data.get("date")
#         sections = output_data.get("sections")
#         print(f"## title\n{title}\n")
#         print(f"## date\n{date}\n")
#         print(f"## sections\n")
#         for s in sections:
#             print(f"- {s}")
#         print()
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "researcher":
#         # key of d[1] may be 'draft' or 'research_data'
#         # draft will be dict[str, str]
#         # research data will be list[dict[str, str]]
#         print(f"# {name}\n")
#         draft = output_data.get("draft", {})
#         for k, v in draft.items():
#             print(f"## DRAFT {k}\n{v}\n")
#         research_data = output_data.get("research_data", [])
#         for rd in research_data:
#             for k, v in rd.items():
#                 print(f"## RESEARCH DATA {k}\n{v}\n")
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "LangGraph" and "publisher" in output_data.keys():
#         report = output_data['publisher']['report']
#         print("\n\n\n")
#         print('FINAL REPORT')
#         print('\n\n\n---------------------\n\n\n')
#         print()
#         print(report)
#         print('\n\n\n---------------------\n\n\n')
#
#
# event_data = []
#
# try:
#     with requests.post(url, json=dict(query=query), stream=True) as response:
#         for idx, line in enumerate(response.iter_lines()):
#             # print(line)
#             if line:
#                 try:
#                     line_data = json.loads(line)
#                     event = line_data.get("event", "")
#                     name = line_data.get("name")
#                     if event == "EOF":
#                         print("End of Stream.")
#                         break
#                     print(event, name)
#                     print(line_data)
#                     output_data = line_data['data']['output']
#                     print(output_data)
#                     print()
#                     print_event_data(name, output_data)
#                     print("\n\n\n")
#                     event_data.append(line_data)
#                     # print(event)
#                     # pprint(event)
#                     # print("\n\n-----\n\n")
#                     # data2.append(data)
#                 except json.JSONDecodeError as e:
#                     print(f"Error decoding JSON: {e}")
#                     # continue  # Optionally skip this line or handle the error differently
#                     raise e
# except KeyboardInterrupt:
#     print("KeyboardInterrupt")


# # p = {
# #   "query": "increased flooding risks due to climate change in Astor, FL",
# #   "max_sections": 3,
# #   "follow_guidelines": False,
# #   "model": "gpt-4o",
# #   "guidelines": [],
# #   "verbose": True,
# #   "output_file_format": "docx"
# # }
# #
# # url = "http://localhost:8001"
# #
# # response = requests.post(url + "/run_research_task", json=p)
# #
# # with open("output.docx", "wb") as f:
# #     f.write(response.content)
#
#
# # browser dict_keys(['task', 'initial_research'])
# # planner dict_keys(['title', 'date', 'sections'])
# # publisher dict_keys(['report'])
# # researcher dict_keys(['draft'])
# # researcher dict_keys(['research_data'])
# # reviewer dict_keys(['review'])
# # writer dict_keys(['table_of_contents', 'introduction', 'conclusion', 'sources', 'headers'])
#
#
#
# # dd = {
# #     'browser': ['task', 'initial_research'],
# #     'planner': ['title', 'date', 'sections'],
# #     'researcher': ['draft', 'research_data'],
# #     'reviewer': ['review'],
# #     'writer': ['table_of_contents', 'introduction', 'conclusion', 'sources', 'headers'],
# #     'publisher': ['report'],
# # }
#
# data4 = []
# for d in data3:
#     name = d.get("name")
#     keys = dd.get(name, [])
#     if keys:
#         print(f"# {name}")
#         print()
#         o = d['data']['output']
#         # data4.append(
#         #     {
#         #         "name": n,
#         #         "data": d,
#         #     }
#         # )
#         for k in keys:
#             kd = o.get(k, {})
#             if kd:
#                 data4.append(
#                     {
#                         "name": name,
#                         "key": k,
#                         "data": kd,
#                     }
#                 )
#                 print(f"## {k}")
#                 pprint(kd)
#         print("\n\n\n---------------------\n\n\n")
#
#
# # """browser
# # 	name: <class 'str'>
# # 	key: <class 'str'>
# # 	data: <class 'str'>, dict, list
# # 	data
# # 		query: <class 'str'>
# # 		max_sections: <class 'int'>
# # 		follow_guidelines: <class 'bool'>
# # 		model: <class 'str'>
# # 		guidelines: <class 'list'>
# # 		verbose: <class 'bool'>
# #
# # 		publish_formats
# # 			docx: <class 'bool'>
# # 			markdown: <class 'bool'>
# # 			pdf: <class 'bool'>
# #
# #
# # planner
# # 	name: <class 'str'>
# # 	key: <class 'str'>
# # 	data: <class 'str'>, <class 'list'>, dict
# #
# # researcher
# # 	name: <class 'str'>
# # 	key: <class 'str'>
# # 	data: <class 'list'>, str, dict
# # 	researcher.data
# # 		(arbitrary str key) Chuluota's Indigenous Legacy: <class 'str'>
# # 		data_Early Indigenous Inhabitants: <class 'str'>
# # 		data_European Contact and Its Impact: <class 'str'>
# #
# #
# # writer
# # 	name: <class 'str'>
# # 	key: <class 'str'>
# # 	data: <class 'str'>, <class 'list'>, dict
# #
# # 	data_title: <class 'str'>
# # 	data_date: <class 'str'>
# # 	data_introduction: <class 'str'>
# # 	data_table_of_contents: <class 'str'>
# # 	data_conclusion: <class 'str'>
# # 	data_references: <class 'str'>
# #
# # publisher
# # 	name: <class 'str'>
# # 	key: <class 'str'>
# # 	data: <class 'str'>
# # """
#
#
# for d in data4:
#     name = d.get("name")
#     if name == "browser":
#         print("# browser")
#         print()
#         line_data = d.get("data")
#         for k, v in line_data.items():
#             print(f"## {k}")
#             print(f"Type: {type(v)}")
#             if isinstance(v, dict):
#                 for kk, vv in v.items():
#                     print(f"### {kk}")
#                     print(f"Type: {type(vv)}")
#             print("\n\n")
#     elif name == "planner":
#         print("# planner")
#         print()
#         line_data = d.get("data")
#         for k, v in line_data.items():
#             print(f"## {k}")
#             print(f"Type: {type(v)}")
#             if isinstance(v, dict):
#                 for kk, vv in v.items():
#                     print(f"### {kk}")
#                     print(f"Type: {type(vv)}")
#             print("\n\n")
#     elif name == "researcher":
#         print("# researcher")
#         print()
#         line_data = d.get("data")
#         for k, v in line_data.items():
#             print(f"## {k}")
#             print(f"Type: {type(v)}")
#             if isinstance(v, dict):
#                 for kk, vv in v.items():
#                     print(f"### {kk}")
#                     print(f"Type: {type(vv)}")
#             print("\n\n")
#     elif name == "writer":
#         print("# writer")
#         print()
#         line_data = d.get("data")
#         for k, v in line_data.items():
#             print(f"## {k}")
#             print(f"Type: {type(v)}")
#             if isinstance(v, dict):
#                 for kk, vv in v.items():
#                     print(f"### {kk}")
#                     print(f"Type: {type(vv)}")
#             print("\n\n")
#     elif name == "publisher":
#         print("# publisher")
#         print()
#         line_data = d.get("data")
#         print(f"Type: {type(line_data)}")
#         print("\n\n")
#     print("\n\n\n---------------------\n\n\n")
#
#
#
#
# for d in data4:
#     name = d.get("name")
#     if name in ["writer", "publisher"]:
#         continue
#     print("# " + name)
#     k = d.get("key")
#     print("## "+ k)
#     line_data = d.get("data")
#     if isinstance(line_data, str):
#         # print(data[:40])
#         pass
#     else:
#         pprint(line_data)
#
#
# for d in data3:
#     name = d.get("name")
#     if name == "browser":
#         print_browser(d["data"]["output"])
#     elif name == "planner":
#         print_browser(d["data"]["output"])
#     elif name == "researcher":
#         print_browser(d["data"]["output"])
#     elif name == "writer":
#         pass
#     elif name == "publisher":
#         pass
#
# data5 = []
# for d in data3:
#     name = d.get("name")
#     covered = [
#         "browser",
#         "planner",
#         "researcher",
#         "LangGraph",
#     ]
#     if name not in covered:
#         continue
#     output = d["data"]["output"]
#     data5.append((name, output))
#     keys = dd.get(name, [])
#     if keys:
#         print(f"# {name}")
#         print()
#         o = d['data']['output']
#         for k in keys:
#             kd = o.get(k, {})
#             if kd:
#                 data4.append(
#                     {
#                         "name": name,
#                         "key": k,
#                         "data": kd,
#                     }
#                 )
#                 print(f"## {k}")
#                 pprint(kd)
#         print("\n\n\n---------------------\n\n\n")
#
#
# for d in data5:
#     name, line_data = d
#     if name == "browser":
#         print(f"# {name}\n")
#         task = line_data.get("task")
#         if task:
#             print(f"## task\n{task}\n")
#         initial_research = line_data.get("initial_research")
#         if initial_research:
#             print(f"### initial research\n{initial_research}\n")
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "planner":
#         print(f"# {name}\n")
#         title = line_data.get("title")
#         date = line_data.get("date")
#         sections = line_data.get("sections")
#         print(f"## title\n{title}\n")
#         print(f"## date\n{date}\n")
#         print(f"## sections\n")
#         for s in sections:
#             print(f"- {s}")
#         print()
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "researcher":
#         # key of d[1] may be 'draft' or 'research_data'
#         # draft will be dict[str, str]
#         # research data will be list[dict[str, str]]
#         print(f"# {name}\n")
#         draft = line_data.get("draft", {})
#         for k,v in draft.items():
#             print(f"## DRAFT {k}\n{v}\n")
#         research_data = line_data.get("research_data", [])
#         for rd in research_data:
#             for k,v in rd.items():
#                 print(f"## RESEARCH DATA {k}\n{v}\n")
#         print('\n\n\n---------------------\n\n\n')
#     elif name == "LangGraph" and "publisher" in line_data.keys():
#         report = line_data['publisher']['report']
#         print("\n\n\n")
#         print('FINAL REPORT')
#         print('\n\n\n---------------------\n\n\n')
#         print()
#         print(report)
#         print('\n\n\n---------------------\n\n\n')
