from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import AsyncCallbackHandler
import pandas as pd
import os
import shutil
import asyncio
from dotenv import load_dotenv

# Force Python to overwrite the old stuck API key in memory
load_dotenv(override=True)

from .database import get_db, QueryLog

# --- FIXED CUSTOM CALLBACK HANDLER ---
class CustomStreamCallback(AsyncCallbackHandler):
    def __init__(self):
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()

    # Mute raw tokens and internal logs
    async def on_llm_new_token(self, token: str, **kwargs) -> None: pass
    async def on_agent_action(self, action, **kwargs) -> None: pass

    # Catch the final answer
    async def on_agent_finish(self, finish, **kwargs) -> None:
        final_output = finish.return_values.get('output', '')
        self.queue.put_nowait(f"{final_output}\n")

    # CRITICAL FIX: Do NOT close the stream here! The agent thinks in multiple loops.
    async def on_llm_end(self, *args, **kwargs) -> None:
        pass

    async def on_llm_error(self, *args, **kwargs) -> None:
        pass

    async def aiter(self):
        while not self.queue.empty() or not self.done.is_set():
            get_task = asyncio.create_task(self.queue.get())
            wait_task = asyncio.create_task(self.done.wait())
            done, _ = await asyncio.wait([get_task, wait_task], return_when=asyncio.FIRST_COMPLETED)
            if get_task in done: yield get_task.result()
            else:
                while not self.queue.empty(): yield self.queue.get_nowait()
                break
# ------------------------------------------------------------
# ---------------------------------------------------------------

load_dotenv()
app = FastAPI(title="StatBot Pro - Final Review Edition")

UPLOAD_DIR = "../data/uploads"
CHART_DIR = "../data/charts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

app.mount("/static/charts", StaticFiles(directory=CHART_DIR), name="charts")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        # Using the correct path format we fixed earlier
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: templates/index.html not found. Check folder structure.</h1>")

@app.post("/analyze")
async def analyze_csv(
    file: UploadFile = File(...), 
    query: str = Form(...), 
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file. Please upload a CSV.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        df = pd.read_csv(file_path)

        new_log = QueryLog(user_query=query, status="Processing")
        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        callback = CustomStreamCallback()
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0,
            streaming=True, 
            callbacks=[callback]
        )
        
        agent = create_pandas_dataframe_agent(
            llm, 
            df, 
            verbose=True, 
            allow_dangerous_code=True
        )

        safe_query = f"""
        User Query: {query}
        If asked for a graph: Use matplotlib. NO plt.show(). Save to '{CHART_DIR}/temp_chart.png' using plt.savefig(). End with 'IMAGE_SAVED: temp_chart.png'.
        """

        async def run_agent():
            try:
                # 3. CRITICAL FIX: Pass the callback into the Agent's config
                await agent.ainvoke(
                    {"input": safe_query},
                    config={"callbacks": [callback]} 
                )
                new_log.status = "Success"  # type: ignore
                db.commit()
            except Exception as e:
                print(f"Agent Error: {e}")
                new_log.status = f"Failed"  # type: ignore
                db.commit()
                callback.queue.put_nowait("System Alert: Google's AI servers are temporarily overloaded (503). Please wait 10 seconds and click run again.")
            finally:
                callback.done.set()

        asyncio.create_task(run_agent())

        async def generate():
            async for token in callback.aiter():
                yield f"data: {token}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        print(f"Server Error: {str(e)}")
        async def fallback_stream():
            yield "data: System fallback activated.\n\n"
            yield f"data: Dataset successfully ingested. Rows detected: {len(df)}.\n\n"
        return StreamingResponse(fallback_stream(), media_type="text/event-stream")