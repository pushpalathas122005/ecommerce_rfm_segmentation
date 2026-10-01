import pandas as pd
import numpy as np
import datetime as dt
import os

def clean_retail_data(file_path):
    print("[+] Loading dataset...")
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    print(f"    Raw records: {len(df):,}")

    df = df.dropna(subset=['CustomerID'])
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    print(f"    Cleaned records: {len(df):,}")
    return df

def compute_rfm(df):
    print("[+] Computing Recency, Frequency, and Monetary scores...")
    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalAmount': 'sum'
    }).reset_index()

    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalAmount': 'Monetary'
    }, inplace=True)
    return rfm

def assign_segments(rfm):
    print("[+] Scoring quantiles and assigning customer personas...")
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

    def segment_mapping(row):
        r, f = row['R_Score'], row['F_Score']
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f < 2:
            return "New / Promising"
        elif r <= 2 and f >= 4:
            return "At Risk (Can't Lose Them)"
        elif r <= 2 and f <= 2:
            return "Lost / Inactive"
        else:
            return "Need Attention"

    rfm['Customer_Segment'] = rfm.apply(segment_mapping, axis=1)
    return rfm

if __name__ == "__main__":
    DATA_PATH = os.path.join("data", "Online_Retail.csv")
    
    if not os.path.exists(DATA_PATH):
        print(f"[!] Error: File not found at '{DATA_PATH}'.")
        print("    Ensure Online_Retail.csv is placed inside the 'data' folder.")
        exit(1)

    raw_df = clean_retail_data(DATA_PATH)
    rfm_table = compute_rfm(raw_df)
    final_rfm = assign_segments(rfm_table)
    
    output_path = "rfm_segmented_customers.csv"
    final_rfm.to_csv(output_path, index=False)
    print(f"\n[+] Success! Segmented results saved to '{output_path}'.")