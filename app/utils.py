import pandas as pd

def load_dataframe(path: str):
    if path.endswith(".csv"):
        return pd.read_csv(path)

    elif path.endswith(".xlsx"):
        return pd.read_excel(path)

    else:
        raise ValueError("Unsupported file format")