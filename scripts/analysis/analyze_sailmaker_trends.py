import pandas as pd
import matplotlib.pyplot as plt

# Sample data loading step - replace this with your actual data loading code
# data_filtered = pd.read_csv('your_data_file.csv')

# Include only Quantum, North, and Ullman sail purchases in the comparison
quantum_north_ullman_data = data_filtered[data_filtered['Sailmaker'].isin(['Quantum', 'North', 'Ullman'])]

# Ensure 'Delivery Date' is in datetime format (if not already)
quantum_north_ullman_data['Delivery Date'] = pd.to_datetime(quantum_north_ullman_data['Delivery Date'])

# Group by year and sailmaker, then count purchases
quantum_north_ullman_annual = quantum_north_ullman_data.groupby([quantum_north_ullman_data['Delivery Date'].dt.year, 'Sailmaker']).size().unstack(fill_value=0)

# Plotting the trend with Ullman included
quantum_north_ullman_annual.plot(kind='area', stacked=False, figsize=(14, 7), alpha=0.5)
plt.title('Annual Purchases: Quantum vs. North vs. Ullman (Area Chart)')
plt.xlabel('Year')
plt.ylabel('Number of Sails Purchased')
plt.legend(title='Sailmaker')
plt.show()
