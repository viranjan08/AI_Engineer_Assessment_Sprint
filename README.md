# AI Support Ticket Analytics System

## 1. Overview
This is a comprehensive, production-ready AI system built to analyze customer support tickets. It handles natural language queries via a local LLM, flags anomalies using a hybrid rules/ML approach, and provides a full REST API + Streamlit dashboard.

## 2. Problem Statement
Given a dataset of 500 support tickets, the goal is to:
- Make the CSV queryable.
- Support natural language questions natively using a free/local LLM.
- Identify anomalies (e.g., abnormally long resolution times, overdue high-priority tickets).
- Expose the capabilities through a REST API and a user interface.

## 3. Features
- **SQL Safety Engine**: Natural language isn't fed directly into SQL execution. The LLM generates a structured JSON intent, which is validated and converted into read-only SQL.
- **Hybrid Anomaly Detection**: Combines business rules with an Isolation Forest model to catch statistical outliers in resolution/response times.
- **Interactive UI**: Streamlit provides a Dashboard, an "Ask AI" chat interface, an Anomalies table, and a Ticket Explorer.

## 4. Architecture
![Architecture](https://via.placeholder.com/800x400.png?text=Ollama+%E2%86%94+FastAPI+%E2%86%94+DuckDB)
*Data moves from Pandas -> DuckDB. Queries move from Streamlit -> FastAPI -> Ollama (Intent) -> DuckDB (SQL).*

## 5. Technology Stack
- **Database**: DuckDB (Fast, analytical, file-based SQL)
- **LLM**: Grok (Cloud LLM API)
- **Backend API**: FastAPI + Pydantic
- **Frontend**: Streamlit
- **Machine Learning**: Scikit-learn (Isolation Forest)
- **Testing**: Pytest

## 6. Project Structure
```
app/          # Core backend logic (API routes, DuckDB manager, LLM/Anomaly services)
ui/           # Streamlit frontend application
data/         # Database and dataset storage
tests/        # Pytest test suites
```

## 7. Setup & Running the Application

1. **Launch everything** via the batch script (Windows):
   ```cmd
   run.bat
   ```
2. **Access**:
   - UI: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 8. Natural Language Query Examples
Try these in the UI's **Ask AI** tab:
- *"How many tickets are currently open?"*
- *"Which agent resolved the most tickets this month?"*
- *"Show me all Critical tickets not resolved within 12 hours."*
- *"What is the average customer rating for Technical category tickets?"*

## 9. Security / Query Safety
**Can the LLM execute arbitrary SQL?** No. 
The system forces the LLM to output a strictly typed JSON payload (an "intent"). The backend parses this JSON, sanitizes the inputs, and manually constructs only `SELECT` operations. Commands like `DROP`, `DELETE`, or `UPDATE` are structurally impossible to generate through this pipeline.

## 10. Known Limitations
- The LLM intent engine relies on Ollama's ability to output valid JSON. Very complex conversational queries might confuse the Llama 3 8B model.
- "Current Time" for ticket aging is statically calculated from the maximum date in the CSV to account for older datasets.
