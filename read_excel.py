import pandas as pd
from pathlib import Path

def read_batch(
    start=0,
    batch_size=200
):

    INPUT = (

    Path(__file__).parent

    / "input"

    / "sample_dataset_compare.xlsx"

)
    df = pd.read_excel(INPUT)

    data = (
        df
        .iloc[
            start:
            start + batch_size
        ]
        .to_dict(
            "records"
        )
    )

    return {
        "rows": data,
        "next_start":
        start + batch_size,
        "count":
        len(data)
    }