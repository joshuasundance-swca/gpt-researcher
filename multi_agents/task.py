import json
from argparse import ArgumentParser

from pydantic import BaseModel, Field, field_validator

available_formats = {"markdown", "pdf", "docx"}

default_model = "gpt-4-turbo"

default_publish_formats = {"markdown": True, "pdf": True, "docx": True}

default_guidelines = [
    "The report MUST be written in APA format",
    "Each sub section MUST include supporting sources using hyperlinks. If none exist, erase the sub section or rewrite it to be a part of the previous section",
    "The report MUST be written in spanish",
]


def task_from_file(task_json_file: str = "task.json") -> dict:
    with open(task_json_file, "r") as f:
        task = json.load(f)

    if not task:
        raise Exception(
            "No task provided. Please include a task.json file in the root directory."
        )

    return task


class _TaskModel(BaseModel):
    query: str = Field(..., title="The research query")
    max_sections: int = Field(3, title="The maximum number of sections in the report")
    follow_guidelines: bool = Field(False, title="Whether to follow the guidelines")
    model: str = Field(default_model, title="The model to use")
    guidelines: list[str] = Field(default_guidelines, title="The guidelines")
    verbose: bool = Field(True, title="Whether to print verbose output")

    @field_validator("max_sections")
    def validate_max_sections(cls, v):
        if v < 1:
            raise ValueError("max_sections must be at least 1")
        return v


class TaskRequest(_TaskModel):
    output_file_format: str = Field(
        "markdown", title="The format to output the report in"
    )

    @field_validator("output_file_format")
    def validate_output_file_format(cls, v):
        if v not in available_formats:
            raise ValueError(
                f"Invalid format requested. Available formats: {', '.join(available_formats)}"
            )
        return v


class TaskModel(_TaskModel):
    publish_formats: dict[str, bool] = Field(
        default_publish_formats, title="The formats to publish the report in"
    )

    @field_validator("publish_formats")
    def validate_publish_formats(cls, v):
        if not set(v.keys()).issubset(available_formats):
            raise ValueError(
                f"Invalid format(s) requested. Available formats: {', '.join(available_formats)}"
            )
        return v

    @classmethod
    def from_task_request(cls, task_request: TaskRequest):
        output_format = task_request.output_file_format
        if output_format not in available_formats:
            raise ValueError(
                f"Invalid format requested. Available formats: {', '.join(available_formats)}"
            )
        publish_formats = {task_request.output_file_format: True}
        for f in available_formats:
            if f != task_request.output_file_format:
                publish_formats[f] = False
        return cls(
            query=task_request.query,
            max_sections=task_request.max_sections,
            follow_guidelines=task_request.follow_guidelines,
            model=task_request.model,
            guidelines=task_request.guidelines,
            verbose=task_request.verbose,
            publish_formats=publish_formats,
        )


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--max_sections",
        type=int,
        default=3,
        help="The maximum number of sections in the report",
    )
    parser.add_argument(
        "-o",
        "--publish_formats",
        type=str,
        default="markdown,pdf,docx",
        help="The formats to publish the report in",
    )
    parser.add_argument(
        "-m", "--model", type=str, default=default_model, help="The model to use"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Whether to print verbose output",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "-g", "--guidelines", nargs="+", help="The guidelines", metavar="GUIDELINE"
    )
    parser.add_argument(
        "-q", "--query", type=str, required=False, help="The research query"
    )
    parser.add_argument("-f", "--file", type=str, required=False, help="The task file")
    return parser.parse_args()


def args_to_task(args) -> TaskModel:
    if args.file:
        task = task_from_file(args.file)
        return TaskModel(**task)
    elif not args.query:
        raise ValueError("No query provided. Please provide a query or a task file.")
    requested_formats = set(args.publish_formats.split(","))
    if not requested_formats.issubset(available_formats):
        raise ValueError(
            f"Invalid format(s) requested. Available formats: {', '.join(available_formats)}"
        )
    publish_formats = {
        f: (True if f in requested_formats else False) for f in available_formats
    }
    return TaskModel(
        query=args.query,
        max_sections=args.max_sections,
        publish_formats=publish_formats,
        follow_guidelines=True if args.guidelines else False,
        model=args.model,
        guidelines=args.guidelines or [],
        verbose=args.verbose,
    )


# class ResearchOutput(BaseModel):
#     task: dict
#     initial_research: str
#     sections: list[str]
#     research_data: list[dict[str, str]]
#     title: str
#     headers: dict[str, str]
#     date: str
#     table_of_contents: str
#     introduction: str
#     conclusion: str
#     sources: list[str]
#     report: str
#     markdown: Optional[bytes]
#     docx: Optional[bytes]
#     pdf: Optional[bytes]
