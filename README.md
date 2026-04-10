StatBot Pro 📊
Enterprise CSV Intelligence Agent

StatBot Pro is a full-stack, AI-powered reasoning agent designed to act as an autonomous data analyst. By leveraging Large Language Models (LLMs) and advanced data manipulation libraries, it allows users to upload raw CSV datasets and query them using natural language. The agent can calculate statistics, extract insights, handle complex datetime logic, and autonomously write/execute Matplotlib code to generate and stream visual graphs directly to the user interface.

🚀 Key Features
Natural Language Processing: Query complex datasets using conversational English.

Autonomous Code Execution: Uses LangChain's Pandas DataFrame Agent to dynamically write and execute Python code in the background based on user prompts.

Multi-Modal Streaming UI: Built with Server-Sent Events (SSE). The UI streams the agent's final reasoning in real-time and dynamically intercepts Python IMAGE_SAVED: commands to instantly render Matplotlib graphs.

Custom Async Callback Handler: Features a deeply integrated callback architecture that hides messy internal agent reasoning (Action/Observation loops) and only pushes clean, final human-readable outputs to the frontend.

Enterprise Error Handling: Gracefully catches API rate limits (HTTP 429) and upstream server overloads (HTTP 503) without breaking the application state.

Database Auditing: Logs every user query and its execution status to a SQLite database using SQLAlchemy for complete operational oversight.

🛠️ Technology Stack
Backend: Python, FastAPI, Uvicorn

AI Engine: Google Gemini API (gemini-2.5-flash / gemini-1.5-flash), LangChain (langchain-google-genai, langchain-experimental)

Data Processing: Pandas, Matplotlib

Database: SQLite, SQLAlchemy

Frontend: HTML5, CSS3 (Dark-mode UI), Vanilla JavaScript (Fetch API, Streams)

stat-pro/
├── app/
│   ├── main.py          # FastAPI application core & Agent logic
│   ├── database.py      # SQLAlchemy models and connection setup
├── data/
│   ├── uploads/         # Secure storage for uploaded CSV files
│   ├── charts/          # Temporary storage for dynamically generated graphs
├── templates/
│   └── index.html       # The streaming UI dashboard
├── .env                 # Environment variables (API keys)
├── .gitignore           # Git protection rules
└── requirements.txt     # Python dependencies

