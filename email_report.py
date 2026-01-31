import os
import pandas as pd
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText

from engine.revenue_metrics import (
    prepare_revenue_data,
    compute_revenue_metrics,
    compute_revenue_changes
)
from engine.revenue_risk import revenue_signals


# =====================================================
# LOAD + PREP DATA
# =====================================================
def load_data():
    df = pd.read_csv("data/orders_by_date.csv")
    df = prepare_revenue_data(df)

    max_date = df["day"].max()
    df = df[df["day"] >= max_date - timedelta(days=30)]

    return df


# =====================================================
# BUILD EMAIL CONTENT (FORMAT 2)
# =====================================================
def build_email_content(metrics, changes, alerts, dashboard_url):
    if changes.get("day_delta") is not None:
        direction = "up" if changes["day_delta"] > 0 else "down"
        exec_summary = (
            f"Net revenue moved {direction} by "
            f"₹{abs(int(changes['day_delta'])):,} compared to yesterday."
        )
    else:
        exec_summary = "Not enough data for daily comparison."

    alerts_text = "\n".join(f"- {a}" for a in alerts) if alerts else "No major risk signals today."

    subject = (
        f"₹{int(metrics['total_net']):,} Net Revenue | "
        f"WoW {changes.get('wow_pct')}% | Arista Vault"
    )

    body = f"""
Hi Founder,

Today’s revenue performance at a glance:

• Net revenue: ₹{int(metrics['total_net']):,}
• Orders: {metrics['orders']}
• Average Order Value: ₹{metrics['aov']:,}
• WoW change: {changes.get('wow_pct')}%
• MoM change: {changes.get('mom_pct')}%
• Monthly run rate: ₹{int(changes.get('run_rate', 0)):,}

What stood out today:
{exec_summary}

Potential risks / signals:
{alerts_text}

For a deeper breakdown (products, discounts, trends),
open the Revenue Command Dashboard:
{dashboard_url}

Access password: aristavault1

—
Automated Revenue Command
Arista Vault
"""

    return subject, body


# =====================================================
# SEND EMAIL
# =====================================================
def send_daily_email():
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receivers = os.getenv("EMAIL_RECEIVER")
    dashboard_url = os.getenv("DASHBOARD_URL")

    if not all([sender, password, receivers, dashboard_url]):
        raise Exception("Missing required environment variables")

    df = load_data()

    metrics = compute_revenue_metrics(df)
    changes = compute_revenue_changes(df)
    alerts, _, _ = revenue_signals(metrics)

    subject, body = build_email_content(metrics, changes, alerts, dashboard_url)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receivers

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receivers.split(","), msg.as_string())

    print("✅ Daily revenue email sent successfully")


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    send_daily_email()
