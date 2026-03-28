def suggest_budget(category_predictions, total_budget=None, user_weights=None):
    """
    Suggests a budget based on predicted spending.
    If total_budget is given, it proportionally adjusts per category.
    If user_weights is provided, category budgets are additionally re-weighted.
    """

    if not category_predictions:
        return {}

    user_weights = user_weights or {}

    # Calculate total predicted spending
    predicted_total = sum(category_predictions.values())

    budget_suggestion = {}

    # If total_budget is provided, scale predictions
    if total_budget:
        scale_factor = total_budget / predicted_total
    else:
        scale_factor = 1

    for cat, amount in category_predictions.items():
        weighted_amount = amount * float(user_weights.get(cat, 1.0))
        budget_suggestion[cat] = round(weighted_amount * scale_factor, 2)

    if total_budget and budget_suggestion:
        adjusted_total = sum(budget_suggestion.values())
        if adjusted_total > 0:
            normalize_factor = total_budget / adjusted_total
            for cat in budget_suggestion:
                budget_suggestion[cat] = round(budget_suggestion[cat] * normalize_factor, 2)

    return budget_suggestion


def build_overspending_alerts(
    category_breakdown,
    prediction_total,
    prediction_category,
    budget_recommendation,
    total_budget=None,
):
    alerts = []

    if total_budget and prediction_total and prediction_total > total_budget:
        alerts.append(
            {
                "type": "total_budget_exceeded",
                "message": "Predicted spending may exceed the total budget.",
                "predicted_total": round(prediction_total, 2),
                "total_budget": round(total_budget, 2),
            }
        )

    if not prediction_category or not budget_recommendation:
        return alerts

    for category, predicted_amount in prediction_category.items():
        category_budget = budget_recommendation.get(category)
        if category_budget is None:
            continue

        if predicted_amount > category_budget:
            alerts.append(
                {
                    "type": "category_budget_exceeded",
                    "category": category,
                    "message": f"Predicted {category} spending may exceed recommended budget.",
                    "predicted": round(predicted_amount, 2),
                    "recommended_budget": round(category_budget, 2),
                    "current_spent": round(float(category_breakdown.get(category, 0.0)), 2),
                }
            )

    return alerts
