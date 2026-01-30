import pandas as pd

def normalize_shopify(df):
    return pd.DataFrame({
        "date": pd.to_datetime(df["day"]),
        "platform": "Shopify",
        "order_id": df["order id"],
        "product_name": df["product title"],
        "gross_revenue": df["total sales"],
        "discount": df["discounts"],
        "net_revenue": df["net sales"],
        "quantity": df["quantity ordered"]
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
