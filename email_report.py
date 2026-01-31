import os
import pandas as pd
import requests
from datetime import timedelta

from engine.revenue_metrics import (
    prepare_revenue_data,
    compute_revenue_metrics,
    compute_revenue_changes
)
from engine.revenue_risk import revenue_signals


def send_daily_email():
    # Load data
    df = pd.read_csv("data/orders_by_date.csv")
    df = prepare_revenue_data(df)

    max_date = df["day"].max()
    df = df[df["day"] >= max_date - timedelta(days=30)]

    metrics = compute_revenue_metrics(df)
    changes = compute_revenue_changes(df)
    alerts, discount_pct, discount_roi = revenue_signals(metrics)

    # SendGrid config
    api_key = os.getenv("SENDGRID_API_KEY")
    sender = os.getenv("EMAIL_SENDER")
    receivers = os.getenv("EMAIL_RECEIVER")

    if not api_key or not sender or not receivers:
        raise Exception("Missing email environment variables")

    subject = "📊 Daily Revenue Summary – Arista Vault"

    body = f"""
Arista Vault – Daily Revenue Summary

Net Revenue: ₹{int(metrics['total_net']):,}
Orders: {metrics['orders']}
AOV: ₹{metrics['aov']:,}

WoW Revenue Change: {changes.get('wow_pct')}%
MoM Revenue Change: {changes.get('mom_pct')}%

Run Rate (Monthly): ₹{int(changes.get('run_rate', 0)):,}

Discount %: {discount_pct}%
Discount ROI: ₹{discount_roi}

Founder Signals:
""" + "\n".join(alerts)

    data = {
        "personalizations": [{
            "to": [{"email": e.strip()} for e in receivers.split(",")]
        }],
        "from": {"email": sender},
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers=headers,
        json=data
    )

    if response.status_code >= 400:
        raise Exception(response.text)


if __name__ == "__main__":
    send_daily_email()
