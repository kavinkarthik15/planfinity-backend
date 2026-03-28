from collections import defaultdict
from app.ai.category_config import CATEGORY_RULES, DEFAULT_CATEGORY_RULE


def generate_alerts(transactions: list[dict], predictions: dict, budgets: dict) -> list[str]:
    alerts = []

    if not transactions:
        return ["Start tracking your expenses"]

    predictions = {str(k).lower(): float(v or 0) for k, v in (predictions or {}).items()}
    budgets = {str(k).lower(): float(v or 0) for k, v in (budgets or {}).items()}

    category_totals = defaultdict(float)
    for t in transactions:
        category = str(t.get('system_category') or t.get('category') or 'other').lower()
        amount = float(t.get('amount', 0) or 0)
        category_totals[category] += amount

    for category, actual in category_totals.items():
        predicted = float(predictions.get(category, 0) or 0)
        allowed = float(budgets.get(category, 0) or 0)

        rules = CATEGORY_RULES.get(category, DEFAULT_CATEGORY_RULE)
        overspend_limit = predicted * rules["overspend_threshold"]
        spike_limit = predicted * rules["spike_threshold"]
        priority = rules["priority"]

        if predicted > 0 and actual > overspend_limit:
            if priority == "high":
                alerts.append(f"🚨 {category.upper()}: Critical overspending")
            elif priority == "medium":
                alerts.append(f"⚠️ {category.upper()}: Overspending")
            else:
                alerts.append(f"ℹ️ {category.upper()}: Spending increased")

        if predicted > 0 and actual > spike_limit:
            alerts.append(f"📈 {category.upper()}: Unusual spike detected")

        if allowed > 0 and actual > allowed:
            alerts.append(f"💸 {category.upper()}: Budget exceeded")

    if not alerts and category_totals:
        alerts.append("✨ Great job! You're on track with your spending")

    return alerts

