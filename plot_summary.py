import pandas as pd
import matplotlib.pyplot as plt

# Load segmented results
df = pd.read_csv("rfm_segmented_customers.csv")

# Count customer distribution
segment_counts = df['Customer_Segment'].value_counts()

# Plot horizontal bar chart
plt.figure(figsize=(9, 5))
segment_counts.plot(kind='barh', color='#2b5c8f', edgecolor='black')
plt.title('Customer Distribution by RFM Segment', fontsize=14, fontweight='bold')
plt.xlabel('Number of Customers', fontsize=11)
plt.ylabel('Segment', fontsize=11)
plt.gca().invert_yaxis()
plt.tight_layout()

# Save image directly into assets
plt.savefig("assets/dashboard_preview.png", dpi=300)
print("[+] Chart saved to assets/dashboard_preview.png!")