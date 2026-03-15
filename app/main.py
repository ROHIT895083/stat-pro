from fastapi import FastAPI, UploadFile, File, HTTPException
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
    try:
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File uploaded successfully",
            "filename": file.filename
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


# -------------------------
# GET: Query CSV file
# -------------------------
@app.get("/query")
def query_file(filename: str, name: str):
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        df = pd.read_csv(file_path)

        # Create Full Name column
        df["Full Name"] = df["First Name"] + " " + df["Last Name"]

        # Search by full name
        result = df[df["Full Name"].str.contains(name, case=False, na=False)]

        return {
            "filename": filename,
            "total_rows": len(result),
            "results": result.to_dict(orient="records")
        }

    except HTTPException as e:
        raise e

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Error parsing CSV file")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )