import pandas as pd
import numpy as np
from datetime import datetime


def calculate_confidence(transactions: list[dict]) -> dict:
    """
    Calculate confidence scores for each category based on:
    - Data volume (more transactions = higher confidence)
    - Data consistency (lower variance = higher confidence)
    - Time coverage (more days = higher confidence)
    
    Returns: dict of category -> confidence (0.0 to 1.0)
    """
    if not transactions:
        return {}
    
    df = pd.DataFrame(transactions)
    
    if 'amount' not in df.columns:
        return {}
    
    # Handle dates
    if 'date' not in df.columns:
        df['date'] = pd.to_datetime(range(len(df)), unit='D', origin='2024-01-01')
    else:
        try:
            df['date'] = pd.to_datetime(df['date'])
        except:
            df['date'] = pd.to_datetime(range(len(df)), unit='D', origin='2024-01-01')
    
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Normalize category field
    category_field = 'system_category' if 'system_category' in df.columns else 'category'
    if category_field == 'system_category' and 'system_category' not in df.columns:
        category_field = 'category'
    
    df['category'] = df[category_field].astype(str).str.lower()
    
    confidence_scores = {}
    
    for category in df['category'].unique():
        cat_df = df[df['category'] == category]
        
        # 🔹 Score 1: Data Volume (0-40 points)
        # 0 points: < 3 transactions
        # 20 points: 5-10 transactions
        # 40 points: 20+ transactions
        tx_count = len(cat_df)
        volume_score = min(40, (tx_count / 20) * 40)
        
        # 🔹 Score 2: Time Coverage (0-30 points)
        # Days between first and last transaction
        date_range = (cat_df['date'].max() - cat_df['date'].min()).days
        time_score = min(30, (date_range / 30) * 30)  # 30 days = full score
        
        # 🔹 Score 3: Consistency (0-30 points)
        # Lower coefficient of variation = higher consistency
        daily = cat_df.groupby('date')['amount'].sum()
        if len(daily) >= 2:
            mean_val = daily.mean()
            if mean_val > 0:
                cv = daily.std() / mean_val  # Coefficient of variation
                # cv=0 → 30pts, cv=3 → 0pts
                consistency_score = max(0, 30 * (1 - min(cv / 3, 1)))
            else:
                consistency_score = 0
        else:
            consistency_score = 10  # Minimal score for very few data points
        
        # 🎯 Total confidence (0.0 to 1.0)
        total_score = (volume_score + time_score + consistency_score) / 100
        confidence_scores[category] = round(min(total_score, 1.0), 2)
    
    return confidence_scores


def predict_spending(transactions: list[dict]) -> dict:
    """
    Generate hybrid spending predictions using:
    - Trend model (spending growth trajectory)
    - Moving average (7-day stability)
    - Recent spending (last 3 days)
    
    Formula: (Trend * 0.4) + (Moving Average * 0.4) + (Recent * 0.2)
    """
    if not transactions:
        return {}

    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Ensure we have required columns
    if 'amount' not in df.columns:
        return {}
    
    # Handle date conversion
    if 'date' not in df.columns:
        # If no date, use transaction order as proxy
        df['date'] = pd.to_datetime(range(len(df)), unit='D', origin='2024-01-01')
    else:
        try:
            df['date'] = pd.to_datetime(df['date'])
        except:
            df['date'] = pd.to_datetime(range(len(df)), unit='D', origin='2024-01-01')
    
    # Ensure amount is numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Normalize category field
    category_field = 'system_category' if 'system_category' in df.columns else 'category'
    if category_field == 'system_category' and 'system_category' not in df.columns:
        category_field = 'category'
    
    df['category'] = df[category_field].astype(str).str.lower()
    
    # Sort by date
    df = df.sort_values('date')
    
    category_predictions = {}
    
    # Predict per category
    for category in df['category'].unique():
        cat_df = df[df['category'] == category]
        
        # Group by day and sum amounts
        daily = cat_df.groupby('date')['amount'].sum()
        
        # If insufficient data, use simple mean
        if len(daily) < 5:
            category_predictions[category] = round(float(daily.mean()), 2)
            continue
        
        values = daily.values.astype(float)
        
        # 🔹 Moving Average (last 7 days)
        moving_avg = np.mean(values[-7:])
        
        # 🔹 Trend (polynomial fit slope)
        x = np.arange(len(values), dtype=float)
        coeffs = np.polyfit(x, values, 1)
        trend = coeffs[0] * len(values)  # Scale trend to match magnitude
        
        # 🔹 Recent spending (last 3 days average)
        recent = np.mean(values[-3:])
        
        # 🔥 Hybrid prediction formula
        prediction = (trend * 0.4) + (moving_avg * 0.4) + (recent * 0.2)
        
        # Ensure non-negative prediction
        category_predictions[category] = round(max(prediction, 0), 2)
    
    return category_predictions
