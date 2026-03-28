def generate_insights(transactions: list[dict], predictions: dict) -> str:
    if not transactions:
        return 'Not enough data to generate insights yet.'

    if not predictions:
        return 'No category data found for insights.'

    insights = []
    for category, value in predictions.items():
        amount = float(value or 0)

        if amount > 3000:
            insights.append(f'You are spending heavily on {category}')
        elif amount < 500:
            insights.append(f'Your {category} spending is under control')

    if not insights:
        top_category = max(predictions, key=predictions.get)
        top_amount = predictions[top_category]
        return (
            f'You are spending more on {top_category}. '
            f'Estimated next spend is around Rs {top_amount}.'
        )

    return ' '.join(insights)
