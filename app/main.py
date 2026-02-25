from fastapi import FastAPI, UploadFile, File
import os
import shutil
import pandas as pd

app = FastAPI()

# Directory where CSV files will be stored
UPLOAD_DIR = "data/uploads"


# -------------------------
# POST: Upload CSV file
# -------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }


# -------------------------
# GET: Query CSV file
# -------------------------
@app.get("/query")
def query_file(filename: str, column: str, value: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Check file exists
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    # Read CSV
    df = pd.read_csv(file_path)

    # Check column exists
    if column not in df.columns:
        return {
            "error": f"Column '{column}' not found",
            "available_columns": list(df.columns)
        }

    # Filter rows
    result = df[df[column].astype(str) == value]

    return {
        "filename": filename,
        "total_rows": len(result),
        "results": result.to_dict(orient="records")
    }