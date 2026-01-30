import pandas as pd


# ✅ ADD THIS BACK (THIS FIXES YOUR ERROR)
def prepare_revenue_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df["day"] = pd.to_datetime(df["day"])

    # Keep only revenue rows
    df = df[df["net sales"] > 0]

    return df


def compute_revenue_metrics(df):
    total_net = df["net sales"].sum()
    total_gross = df["total sales"].sum()
    total_discounts = df["discounts"].sum()

    orders = df["order id"].nunique()
    aov = round(total_net / orders, 2) if orders else 0

    revenue_by_day = df.groupby("day")["net sales"].sum()

    revenue_by_product = (
        df.groupby("product title")["net sales"]
        .sum()
        .sort_values(ascending=False)
    )

    discount_by_product = (
        df.groupby("product title")[["net sales", "discounts"]]
        .sum()
    )

    top_1 = round(revenue_by_product.head(1).sum() / total_net * 100, 2)
    top_3 = round(revenue_by_product.head(3).sum() / total_net * 100, 2)
    top_5 = round(revenue_by_product.head(5).sum() / total_net * 100, 2)

    # ---- New vs Repeat Revenue (Order-Level Proxy) ----
    order_revenue = df.groupby("order id")["net sales"].sum()
    repeat_revenue = order_revenue[order_revenue > order_revenue.median()].sum()
    new_revenue = total_net - repeat_revenue

    return {
        "total_net": total_net,
        "total_gross": total_gross,
        "total_discounts": total_discounts,
        "orders": orders,
        "aov": aov,
        "revenue_by_day": revenue_by_day,
        "revenue_by_product": revenue_by_product,
        "discount_by_product": discount_by_product,
        "top_1": top_1,
        "top_3": top_3,
        "top_5": top_5,
        "new_revenue": new_revenue,
        "repeat_revenue": repeat_revenue
    }


def compute_revenue_changes(df):
    daily = df.groupby("day")["net sales"].sum().sort_index()

    weekly = daily.resample("W").sum()
    monthly = daily.resample("M").sum()

    def pct_change(series):
        if len(series) < 2:
            return None
        prev, curr = series.iloc[-2], series.iloc[-1]
        if prev == 0:
            return None
        return round((curr - prev) / prev * 100, 2)

    def abs_change(series):
        if len(series) < 2:
            return None
        return round(series.iloc[-1] - series.iloc[-2], 2)

    run_rate = round(daily.mean() * 30, 2)

    return {
        "wow_pct": pct_change(weekly),
        "mom_pct": pct_change(monthly),
        "aov_wow": pct_change(weekly),
        "day_delta": abs_change(daily),
        "run_rate": run_rate,
        "latest_day": daily.index.max()
    }
