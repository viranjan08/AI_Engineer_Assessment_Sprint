import pandas as pd
from sklearn.ensemble import IsolationForest
from app.database.duckdb_manager import execute_read_only_query

def detect_anomalies():
    """Runs rule-based and ML-based anomaly detection on the tickets table."""
    try:
        df = execute_read_only_query("SELECT * FROM tickets")
    except Exception as e:
        return {"error": str(e)}

    if df.empty:
        return []

    anomalies = []

    # --- 1. Rule-Based Anomalies ---
    
    # Rule A: Unresolved high-priority ticket older than 24 hours
    rule_a_df = df[
        (df['is_resolved'] == False) & 
        (df['is_high_priority'] == True) & 
        (df['is_over_24h'] == True)
    ]
    for _, row in rule_a_df.iterrows():
        anomalies.append({
            "ticket_id": row['ticket_id'],
            "anomaly_type": "overdue_high_priority",
            "severity": "Critical",
            "reason": f"Ticket is unresolved, has {row['priority']} priority, and has been open for {row['ticket_age_hours']:.1f} hours."
        })
        
    # Rule B: Unusually long resolution time (statistical)
    if 'resolution_time_hrs' in df.columns:
        resolved_df = df[df['is_resolved'] == True].copy()
        if not resolved_df.empty:
            mean_res = resolved_df['resolution_time_hrs'].mean()
            std_res = resolved_df['resolution_time_hrs'].std()
            threshold = mean_res + 2 * std_res
            
            rule_b_df = resolved_df[resolved_df['resolution_time_hrs'] > threshold]
            for _, row in rule_b_df.iterrows():
                anomalies.append({
                    "ticket_id": row['ticket_id'],
                    "anomaly_type": "long_resolution_time",
                    "severity": "High",
                    "reason": f"Resolution time ({row['resolution_time_hrs']} hrs) is unusually high compared to the dataset mean ({mean_res:.1f} hrs)."
                })

    # --- 2. ML-Based Anomalies (Isolation Forest) ---
    # We will use resolution_time_hrs and response_time_hrs. We must handle nulls.
    features_df = df[['ticket_id', 'response_time_hrs', 'resolution_time_hrs']].copy()
    features_df.fillna(-1, inplace=True) # Fill NaNs for the model
    
    X = features_df[['response_time_hrs', 'resolution_time_hrs']]
    
    if len(X) > 50: # Only run ML if we have enough data
        iso_forest = IsolationForest(contamination=0.02, random_state=42) # 2% contamination
        features_df['anomaly_score'] = iso_forest.fit_predict(X)
        
        # -1 indicates anomaly
        ml_anomalies = features_df[features_df['anomaly_score'] == -1]
        
        # Avoid duplicating rule-based anomalies if possible, but for simplicity we append them
        for _, row in ml_anomalies.iterrows():
            # Check if we already flagged this ticket
            if not any(a['ticket_id'] == row['ticket_id'] for a in anomalies):
                anomalies.append({
                    "ticket_id": row['ticket_id'],
                    "anomaly_type": "ml_isolation_forest",
                    "severity": "Medium",
                    "reason": "Flagged by Isolation Forest due to abnormal response/resolution time combination."
                })

    return anomalies
