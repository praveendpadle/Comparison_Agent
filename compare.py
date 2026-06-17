from rapidfuzz import fuzz


def compare_batch(rows):

    results = []

    for r in rows:

        score = fuzz.ratio(
            str(r["Address"]),
            str(r["AI_Address"])
        )

        results.append({

            **r,

            "Address_Result":
            (
                "Match"
                if score > 90
                else "Mismatch"
            )
        })

    return results