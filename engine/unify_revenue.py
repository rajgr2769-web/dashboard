import pandas as pd

# ---------- PLATFORM NORMALIZERS ----------

def normalize_shopify(df):
    df.columns = df.columns.str.strip().str.lower()
    return pd.DataFrame({
        "date": pd.to_datetime(df["day"]),
        "platform": "Shopify",
        "order_id": df["order id"],
        "product_name": df["product title"],
        "gross_revenue": df["total sales"],
        "discount": df["discounts"],
        "net_revenue": df["net sales"],
        "quantity": df.get("quantity ordered", 1)
    })


def normalize_amazon(df):
    return pd.DataFrame({
        "date": pd.to_datetime(df["order-date"]),
        "platform": "Amazon",
        "order_id": df["amazon-order-id"],
        "product_name": df["sku"],
        "gross_revenue": df["item-price"],
        "discount": df["promotion-discount"],
        "net_revenue": df["item-price"] - df["promotion-discount"],
        "quantity": df["quantity"]
    })


def normalize_myntra(df):
    return pd.DataFrame({
        "date": pd.to_datetime(df["order_date"]),
        "platform": "Myntra",
        "order_id": df["order_id"],
        "product_name": df["style_id"],
        "gross_revenue": df["mrp"],
        "discount": df["discount"],
        "net_revenue": df["net_amount"],
        "quantity": df["qty"]
    })


# ---------- BUILD UNIFIED TABLE ----------

def build_unified_revenue():
    frames = []

    try:
        shopify = pd.read_csv("data/shopify_orders.csv")
        frames.append(normalize_shopify(shopify))
    except FileNotFoundError:
        pass

    try:
        amazon = pd.read_csv("data/amazon_orders.csv")
        frames.append(normalize_amazon(amazon))
    except FileNotFoundError:
        pass

    try:
        myntra = pd.read_csv("data/myntra_orders.csv")
        frames.append(normalize_myntra(myntra))
    except FileNotFoundError:
        pass

    if not frames:
        raise Exception("No platform revenue files found")

    unified = pd.concat(frames, ignore_index=True)
    unified = unified[unified["net_revenue"] > 0]

    unified.to_csv("data/unified_revenue.csv", index=False)
    print("✅ unified_revenue.csv updated")


if __name__ == "__main__":
    build_unified_revenue()
