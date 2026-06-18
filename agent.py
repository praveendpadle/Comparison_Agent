from google.adk.agents import LlmAgent

from .tools.read_excel import read_batch
from .tools.compare import compare_batch
from .tools.write_output import save_batch


root_agent = LlmAgent(

    name="dataset_validation_agent",

    model="gemini-2.5-pro",

    description="Excel comparison agent",

    instruction="""
Process excel incrementally.

Workflow:

1 Read batch
2 Compare rows
3 Save output
4 Continue

Never load all rows.

Store:
current_batch
processed_count

Stop when completed.
""",

    tools=[
        read_batch,
        compare_batch,
        save_batch
    ]
)