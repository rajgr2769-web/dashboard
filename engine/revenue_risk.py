def revenue_signals(metrics):
    alerts = []

    total_discounts = metrics.get("total_discounts", 0)
    total_gross = metrics.get("total_gross", 0)
    total_net = metrics.get("total_net", 0)

    # Discount %
    discount_pct = (
        round((total_discounts / total_gross) * 100, 2)
        if total_gross > 0 else 0
    )

    # Discount ROI
    discount_roi = (
        round(total_net / total_discounts, 2)
        if total_discounts > 0 else None
    )

    if discount_pct > 25:
        alerts.append(
            f"High discount leakage: {discount_pct}% of gross revenue."
        )

    if metrics.get("top_3", 0) > 55:
        alerts.append(
            f"Revenue concentration risk: Top 3 products drive {metrics['top_3']}% of net revenue."
        )

    if discount_roi is not None and discount_roi < 3:
        alerts.append(
            f"Low discount ROI: ₹{discount_roi} revenue per ₹1 discount."
        )

    if not alerts:
        alerts.append("Revenue health looks stable with no major red flags.")

    return alerts, discount_pct, discount_roi
