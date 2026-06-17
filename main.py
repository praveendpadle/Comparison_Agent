import asyncio
import pandas as pd
import json
import re
import os

from pathlib import Path

from dotenv import load_dotenv

from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


# ------------------------
# ENV
# ------------------------

env_path = (
    Path(__file__).parent
    / "comparision_agent"
    / ".env"
)

load_dotenv(env_path)


# Load after env
from comparision_agent.agent import root_agent


# ------------------------
# CONFIG
# ------------------------

INPUT = (
    "input/sample_dataset_compare.xlsx"
)

OUTPUT = (
    "output/comparison_result.xlsx"
)

BATCH = 50


# ------------------------
# JSON CLEANER
# ------------------------

def extract_json(text):

    text = text.strip()

    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.MULTILINE
    )

    text = re.sub(
        r"```$",
        "",
        text,
        flags=re.MULTILINE
    )

    text = text.strip()

    match = re.search(
        r"(\[.*\]|\{.*\})",
        text,
        re.DOTALL
    )

    if not match:

        raise Exception(
            "No JSON found"
        )

    return json.loads(
        match.group(1)
    )


# ------------------------
# NORMALIZE KEYS
# ------------------------

def normalize_output(data):

    normalized = []

    for row in data:

        normalized.append({

            "ID":
                row.get("ID"),

            "Phone":
                row.get("Phone"),

            "AI_Phone":
                row.get("AI_Phone"),

            "Address":
                row.get("Address"),

            "AI_Address":
                row.get("AI_Address"),

            "OperatingHours":
                row.get("OperatingHours"),

            "AI_OperatingHours":
                row.get("AI_OperatingHours"),

            "Phone_Result":
                row.get(
                    "Phone_Result"
                )
                or
                row.get(
                    "phone_result"
                ),

            "Address_Result":
                row.get(
                    "Address_Result"
                )
                or
                row.get(
                    "address_result"
                ),

            "Hours_Result":
                row.get(
                    "Hours_Result"
                )
                or
                row.get(
                    "hours_result"
                ),

            "Overall_Result":
                row.get(
                    "Overall_Result"
                )
                or
                row.get(
                    "overall_result"
                )
        })

    return normalized

# ------------------------
# SAVE EXCEL
# ------------------------

def append_excel(data):

    Path(
        OUTPUT
    ).parent.mkdir(
        exist_ok=True
    )

    df = pd.DataFrame(
        data
    )

    columns = [

        "ID",

        "Phone",
        "AI_Phone",

        "Address",
        "AI_Address",

        "OperatingHours",
        "AI_OperatingHours",

        "Phone_Result",
        "Address_Result",
        "Hours_Result",

        "Overall_Result"
    ]

    for c in columns:

        if c not in df.columns:

            df[c] = ""

    df = df[
        columns
    ]

    if Path(
        OUTPUT
    ).exists():

        old = pd.read_excel(
            OUTPUT
        )

        df = pd.concat(
            [
                old,
                df
            ],
            ignore_index=True
        )

    df.to_excel(
        OUTPUT,
        index=False
    )

    print(
        "\nSaved rows:"
    )

    print(
        df.tail()
    )

# ------------------------
# BATCH
# ------------------------

def get_batches():

    df = pd.read_excel(
        INPUT
    )

    if "ID" not in df.columns:

        df.insert(
            0,
            "ID",
            range(
                1,
                len(df)+1
            )
        )

    for i in range(
        0,
        len(df),
        BATCH
    ):

        yield (
            i,
            df.iloc[
                i:i+BATCH
            ]
        )


# ------------------------
# EXECUTE
# ------------------------

async def execute():

    service = (
        InMemorySessionService()
    )

    await service.create_session(

        app_name="compare",

        user_id="u1",

        session_id="s1"
    )

    runner = Runner(

        agent=root_agent,

        app_name="compare",

        session_service=service
    )

    for start, batch in get_batches():

        rows = (
            batch
            .to_json(
                orient="records"
            )
        )

        message = types.Content(

            role="user",

            parts=[

                types.Part(

                    text=f"""
Compare rows.

Return JSON only.

Keep original values.

Output:

ID
Phone
AI_Phone
Address
AI_Address
OperatingHours
AI_OperatingHours
Phone_Result
Address_Result
Hours_Result
Overall_Result

DATA:

{rows}
"""
                )
            ]
        )

        response = ""

        async for event in runner.run_async(

            user_id="u1",

            session_id="s1",

            new_message=message
        ):

            try:

                if hasattr(
                    event,
                    "content"
                ):

                    for p in (
                        event.content.parts
                    ):

                        if hasattr(
                            p,
                            "text"
                        ):

                            response += (
                                p.text
                            )

            except:
                pass

        try:

            print(
                f"\nBatch {start}"
            )

            parsed = extract_json(
                response
            )

            parsed = normalize_output(
                parsed
            )

            append_excel(
                parsed
            )

            print(
                "Saved"
            )

        except Exception as ex:

            print(
                "\nERROR:"
            )

            print(ex)

            print(
                "\nRAW RESPONSE:\n"
            )

            print(
                response
            )


asyncio.run(
    execute()
)