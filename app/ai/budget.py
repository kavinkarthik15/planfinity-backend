def generate_budget(predictions: dict) -> dict:
    """Recommend budget as 90% of predicted spend per category."""
    return {
        category: round(float(amount) * 0.9, 2)
        for category, amount in predictions.items()
    }
