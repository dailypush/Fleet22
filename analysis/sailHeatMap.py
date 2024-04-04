import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the JSON file
file_path = '../data/sail_tags.json'  # Update this path
df_updated = pd.read_json(file_path)

# Convert "Delivery Date" to datetime and "Fleet" to string for proper filtering
df_updated["Delivery Date"] = pd.to_datetime(df_updated["Delivery Date"], errors='coerce')
df_updated = df_updated.dropna(subset=["Delivery Date"])  # Drop rows where 'Delivery Date' is NaT
df_updated["Fleet"] = df_updated["Fleet"].astype(str)

# Filter the dataset for Fleet 22
fleet_22_hulls = df_updated[df_updated['Fleet'] == '22']

# Unique hulls within Fleet 22
unique_hulls = fleet_22_hulls['Hull'].unique()

# For demonstration, we'll generate heat maps for up to 5 hulls due to space and processing limitations
for hull in unique_hulls[:12]:
    hull_data = fleet_22_hulls[fleet_22_hulls['Hull'] == hull]
    hull_purchases_detailed = hull_data.groupby([hull_data['Delivery Date'].dt.year, 'Sail Type', 'Sailmaker']).size().unstack(level=[1,2], fill_value=0)
    hull_purchases_detailed.columns = [' '.join(col).strip() for col in hull_purchases_detailed.columns.values]
    
    # Plotting the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(hull_purchases_detailed.T, cmap="YlGnBu", annot=True, fmt="d", cbar_kws={'label': 'Number of Purchases'})
    plt.title(f'Purchases for Hull {hull} by Year, Sail Type, and Sailmaker')
    plt.xlabel('Year')
    plt.ylabel('Sail Type and Sailmaker')
    plt.tight_layout()
    plt.show()
