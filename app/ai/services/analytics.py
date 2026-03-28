from collections import defaultdict


def total_spending(transactions):
	return sum(t["amount"] for t in transactions)


def category_breakdown(transactions):
	category_total = defaultdict(float)

	for t in transactions:
		category_total[t["system_category"]] += t["amount"]

	return dict(category_total)


def daily_average(transactions):
	unique_days = set(t["date"] for t in transactions)

	if not unique_days:
		return 0

	total = total_spending(transactions)
	return total / len(unique_days)
