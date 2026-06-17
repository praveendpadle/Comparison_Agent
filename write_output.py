import pandas as pd
import os


def save_batch(
    rows,
    output_file
):

    df = pd.DataFrame(rows)

    if os.path.exists(
        output_file
    ):

        existing = pd.read_excel(
            output_file
        )

        df = pd.concat(
            [
                existing,
                df
            ]
        )

    df.to_excel(
        output_file,
        index=False
    )

    return output_file