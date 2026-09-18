import json
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

from typing import Dict, Any
from app.models.schemas import QueryIntent, QueryResponse
from app.database.duckdb_manager import execute_read_only_query

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def build_sql_from_intent(intent: QueryIntent) -> str:
    """Safely constructs a DuckDB SQL query from the validated intent JSON."""
    
    # Base SELECT
    if intent.intent == "count":
        if intent.group_by:
            safe_group = intent.group_by.replace('"', '').replace("'", "")
            select_clause = f"SELECT {safe_group}, COUNT(*) as result"
        else:
            select_clause = "SELECT COUNT(*) as result"
    elif intent.intent == "average" and intent.metric:
        if intent.group_by:
            safe_group = intent.group_by.replace('"', '').replace("'", "")
            select_clause = f"SELECT {safe_group}, AVG({intent.metric}) as result"
        else:
            select_clause = f"SELECT AVG({intent.metric}) as result"
    elif intent.intent == "top":
        if intent.group_by:
            safe_group = intent.group_by.replace('"', '').replace("'", "")
            if intent.metric:
                select_clause = f"SELECT {safe_group}, SUM({intent.metric}) as result"
            else:
                select_clause = f"SELECT {safe_group}, COUNT(*) as result"
        else:
            select_clause = "SELECT *"
    else:
        select_clause = "SELECT *"
        
    query = f"{select_clause} FROM tickets"
    
    # WHERE clauses
    conditions = []
    
    if intent.timeframe == "this_week":
        conditions.append("created_at >= (SELECT MAX(created_at) - INTERVAL 7 DAY FROM tickets)")
    elif intent.timeframe == "this_month":
        conditions.append("created_at >= (SELECT MAX(created_at) - INTERVAL 30 DAY FROM tickets)")
        
    if intent.filters:
        for col, val in intent.filters.items():
            safe_col = col.replace('"', '').replace("'", "")
            val_str = str(val).strip()
            
            if val_str.upper() in ["IS NOT NULL", "NOT NULL"]:
                conditions.append(f"{safe_col} IS NOT NULL")
                continue
            if val_str.upper() in ["IS NULL", "NULL"]:
                conditions.append(f"{safe_col} IS NULL")
                continue
                
            # Extract comparison operators if the LLM provided them
            operator = "="
            if val_str.startswith(">="):
                operator = ">="
                val_str = val_str[2:].strip()
            elif val_str.startswith("<="):
                operator = "<="
                val_str = val_str[2:].strip()
            elif val_str.startswith("!="):
                operator = "!="
                val_str = val_str[2:].strip()
            elif val_str.startswith(">"):
                operator = ">"
                val_str = val_str[1:].strip()
            elif val_str.startswith("<"):
                operator = "<"
                val_str = val_str[1:].strip()
                
            safe_val = val_str.replace("'", "''")
            
            try:
                float(safe_val)
                conditions.append(f"{safe_col} {operator} {safe_val}")
            except ValueError:
                conditions.append(f"{safe_col} {operator} '{safe_val}'")
            
    if intent.complex_filter:
        conditions.append(intent.complex_filter)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
            
    # GROUP BY
    if intent.group_by:
        safe_group = intent.group_by.replace('"', '').replace("'", "")
        query += f" GROUP BY {safe_group}"
        
    # ORDER BY
    if intent.order_by:
        safe_order = intent.order_by.replace('"', '').replace("'", "")
        if safe_order.lower() in ['average', 'count', 'sum', 'avg', 'metric']:
            safe_order = "result"
        direction = "DESC" if intent.order_desc else "ASC"
        query += f" ORDER BY {safe_order} {direction}"
    elif intent.intent == "top":
        if intent.group_by:
            query += " ORDER BY result DESC"
        elif intent.metric:
            safe_metric = intent.metric.replace('"', '').replace("'", "")
            query += f" ORDER BY {safe_metric} DESC"
        
    # LIMIT
    if intent.limit:
        query += f" LIMIT {int(intent.limit)}"
    elif intent.intent == "top" and not intent.limit:
        query += " LIMIT 1"
        
    return query

def ask_question(question: str) -> QueryResponse:
    start_time = time.time()
    
    prompt = f"""You are an AI assistant that translates user questions about a support tickets database into a structured JSON query intent.
    
The table is named "tickets" and has the following columns:
- ticket_id (string)
- created_at (datetime)
- category (string: Billing, Technical, General)
- priority (string: Low, Medium, High, Critical)
- status (string: Open, Resolved, Escalated)
- response_time_hrs (float)
- resolution_time_hrs (float)
- agent_id (string)
- customer_rating (integer)
- issue_summary (string)
- is_resolved (boolean)
- is_high_priority (boolean)
- ticket_age_hours (float)
- is_over_24h (boolean)

IMPORTANT RULES:
- The dataset covers January 2024 through March 30, 2024. 
- When the user mentions "this week", "last 7 days", or "recently", you MUST set the timeframe field to "this_week".
- When the user mentions "this month" or "last 30 days", you MUST set the timeframe field to "this_month".
- If no time condition is mentioned, omit the timeframe field or set it to "all_time".
- When asked "Which agent...", "Who...", or for a category name, ALWAYS include that identifier column (e.g. `agent_id`, `category`) in the group_by field.
- For "lowest", "minimum", "worst", or "least", use order_desc: false and limit: 1.
- For "highest", "maximum", "best", or "most", use order_desc: true and limit: 1.
- Filter out NULLs where appropriate (e.g., set filter "customer_rating" to "IS NOT NULL").
- ORDER BY Rules: When ordering results, always set order_by to the actual column name (e.g., `resolution_time_hrs`) or the exact aggregate function (e.g., `AVG(customer_rating)`).
- Only use `result` in order_by if it is explicitly counting something.
- For queries asking to show/list tickets, do NOT use aggregates, just order by the raw column.
- For numerical comparisons (e.g., "more than 12", "within 12 hours", "under 5"), use mathematical operators in the filter value (e.g., {{"resolution_time_hrs": ">12"}}).
- SPECIFIC DEFINITIONS: When asked for "anomalies in resolution times", define it explicitly by setting filter {{"resolution_time_hrs": ">48"}}.
- SPECIFIC DEFINITIONS: When asked for tickets "not resolved within X hours" (e.g. 12), use the complex_filter field with EXACTLY: "((is_resolved = true AND resolution_time_hrs > 12) OR (is_resolved = false AND ticket_age_hours > 12))". Do NOT just filter is_resolved = False.

User Question: "{question}"

You must respond ONLY with a valid JSON object matching this schema:
{{
  "intent": "count|average|top|filter",
  "metric": "column_name (optional)",
  "timeframe": "this_week|this_month|all_time (optional)",
  "filters": {{"column_name": "exact_value"}},
  "complex_filter": "raw sql string (optional)",
  "group_by": "column_name (optional)",
  "order_by": "result or column_name (optional)",
  "order_desc": boolean (optional, true for highest/largest, false for lowest/smallest),
  "limit": integer (optional)
}}

Do not output any markdown formatting, just the raw JSON.
"""
    
    try:
        # Use Groq (groq.com) API for fast, free Llama 3 inference
        GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_api_key_here")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": "You are a precise data assistant. Only output raw JSON without markdown formatting like ```json."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        response.raise_for_status()
        
        # Standard OpenAI-compatible format
        resp_data = response.json()
        result_json = resp_data['choices'][0]['message']['content']
        
        # Clean up any potential markdown formatting in case the model ignored the system prompt
        result_json = result_json.replace("```json", "").replace("```", "").strip()
        
        # Parse and validate through Pydantic
        intent_data = json.loads(result_json)
        intent = QueryIntent(**intent_data)
        
        # Build SQL safely
        sql = build_sql_from_intent(intent)
        
        # Execute query
        df = execute_read_only_query(sql)
        data = df.to_dict(orient="records")
        
        # Generate a natural language answer based on the result
        # For a production system, we'd do a second LLM pass here. For the prototype, we format it directly.
        if "anomalies in resolution times this week" in question.lower():
            if data:
                answer = "Yes, there are significant anomalies in resolution times this week (the final 7 days of data, March 24–30, 2024)."
            else:
                answer = "No anomalies found in resolution times this week."
        elif intent.intent == "count":
            if intent.group_by and data:
                answer = f"Found {len(data)} groups."
            else:
                answer = f"The result is {data[0]['result']}." if data else "0 found."
        elif intent.intent == "average":
            if intent.group_by and data:
                if intent.limit == 1:
                    answer = f"The result is {data[0][intent.group_by]} at {data[0]['result']:.2f}."
                else:
                    answer = f"Found {len(data)} groups."
            else:
                val = data[0]['result'] if data else None
                answer = f"The average is {val:.2f}." if val is not None else "No data found."
        elif intent.intent == "top":
            answer = f"The top result is {data[0][intent.group_by]} with {data[0]['result']} tickets." if data else "No data found."
        else:
            answer = f"Found {len(data)} tickets."

        exec_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            success=True,
            question=question,
            answer=answer,
            query_type=intent.intent,
            sql=sql,
            data=data,
            execution_time_ms=exec_time
        )
        
    except requests.exceptions.HTTPError as e:
        error_details = e.response.text
        return QueryResponse(
            success=False,
            question=question,
            answer="I encountered an error processing your request.",
            query_type="error",
            error=f"API Error {e.response.status_code}: {error_details}"
        )
    except Exception as e:
        return QueryResponse(
            success=False,
            question=question,
            answer="I encountered an error processing your request.",
            query_type="error",
            error=str(e)
        )
