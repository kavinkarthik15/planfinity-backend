from collections import defaultdict
from datetime import datetime

from sklearn.linear_model import LinearRegression


def prepare_daily_data(transactions):
	daily_data = defaultdict(float)

	for t in transactions:
		daily_data[t["date"]] += t["amount"]

	return sorted(daily_data.items())  # [(date, amount)]


def convert_to_xy(daily_data):
	X = []
	y = []

	for i, (_, amount) in enumerate(daily_data):
		X.append([i])
		y.append(amount)

	return X, y


def train_model(X, y):
	model = LinearRegression()
	model.fit(X, y)
	return model


def predict_future(model, last_index, days_ahead):
	predictions = []

	for i in range(1, days_ahead + 1):
		future_day = [[last_index + i]]
		pred = model.predict(future_day)[0]
		predictions.append(max(pred, 0))

	return predictions


def predict_spending(transactions, days_ahead=10):
	if len(transactions) < 5:
		return None

	daily_data = prepare_daily_data(transactions)
	X, y = convert_to_xy(daily_data)

	model = train_model(X, y)

	last_index = len(X)
	future = predict_future(model, last_index, days_ahead)

	return sum(future)


def predict_category_spending(transactions, days_ahead=10):
	"""
	Predict future spending per category.
	"""
	category_data = defaultdict(list)
	for t in transactions:
		category_data[t["system_category"]].append(t)

	category_predictions = {}

	for cat, trans in category_data.items():
		if len(trans) < 5:
			continue

		daily_data = prepare_daily_data(trans)
		X, y = convert_to_xy(daily_data)

		model = train_model(X, y)

		last_index = len(X)
		future = predict_future(model, last_index, days_ahead)

		category_predictions[cat] = sum(future)

	return category_predictions


def _weekend_weekday_multiplier(transactions):
	day_totals = defaultdict(float)

	for transaction in transactions:
		date_key = transaction["date"]
		day_totals[date_key] += transaction["amount"]

	if not day_totals:
		return 1.0

	weekend_values = []
	weekday_values = []

	for date_key, amount in day_totals.items():
		day = datetime.strptime(date_key, "%Y-%m-%d").weekday()
		if day >= 5:
			weekend_values.append(amount)
		else:
			weekday_values.append(amount)

	if not weekend_values or not weekday_values:
		return 1.0

	avg_weekend = sum(weekend_values) / len(weekend_values)
	avg_weekday = sum(weekday_values) / len(weekday_values)

	historical_avg = (avg_weekend + avg_weekday) / 2
	future_mix_avg = (avg_weekday * 5 + avg_weekend * 2) / 7

	if historical_avg == 0:
		return 1.0

	return future_mix_avg / historical_avg


def predict_category_spending_with_adjustments(
	transactions,
	days_ahead=10,
	weekend_adjustment=False,
):
	category_predictions = predict_category_spending(transactions, days_ahead=days_ahead)

	if not weekend_adjustment or not category_predictions:
		return category_predictions

	adjusted_predictions = {}
	for category, amount in category_predictions.items():
		category_transactions = [
			transaction
			for transaction in transactions
			if transaction.get("system_category") == category
		]
		multiplier = _weekend_weekday_multiplier(category_transactions)
		adjusted_predictions[category] = round(amount * multiplier, 2)

	return adjusted_predictions
