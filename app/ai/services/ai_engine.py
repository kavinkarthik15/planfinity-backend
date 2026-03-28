import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_insights(transactions, predictions, phase):
	"""
	Generate human-like insights based on transactions and predictions.
	"""

	if not transactions or not predictions:
		return "Not enough data to provide insights yet."

	# Build prompt for LLM.
	prompt = f"""
	You are a financial advisor AI.
	User transactions: {transactions}
	Predicted spending per category: {predictions}
	Phase: {phase}

	Provide 3 short, actionable insights in plain text.
	"""

	try:
		response = client.chat.completions.create(
			model="gpt-4o-mini",
			messages=[{"role": "user", "content": prompt}],
			max_tokens=150,
		)
		return response.choices[0].message.content.strip()
	except Exception:
		return "Insights unavailable right now. Please check OPENAI_API_KEY configuration."
