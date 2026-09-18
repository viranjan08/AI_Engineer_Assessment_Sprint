from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class QueryIntent(BaseModel):
    intent: str = Field(description="The type of query: 'count', 'average', 'top', 'filter'")
    metric: Optional[str] = Field(None, description="The column to aggregate or rank by (e.g., 'customer_rating', 'resolution_time_hrs')")
    timeframe: Optional[str] = Field("all_time", description="'this_week', 'this_month', or 'all_time'")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dictionary of exact match filters (e.g., {'status': 'Open', 'priority': 'Critical'})")
    complex_filter: Optional[str] = Field(None, description="Raw SQL for complex OR conditions")
    group_by: Optional[str] = Field(None, description="Column to group by (e.g., 'agent_id', 'category')")
    order_by: Optional[str] = Field(None, description="Column to order by")
    order_desc: Optional[bool] = Field(True, description="Whether to order descending")
    limit: Optional[int] = Field(None, description="Limit the number of results")

class QueryResponse(BaseModel):
    success: bool
    question: str
    answer: str
    query_type: str
    sql: Optional[str] = None
    data: Optional[list] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
