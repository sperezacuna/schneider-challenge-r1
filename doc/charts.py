#Ensure that you have installed all the necessary dependencies. You can do this by executing "pip install NAME", for example, NAME=seaborn.1
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

"""--------------------------------------------------------------
#EXPLORATORY ANALYSIS 1 - Insights [2/8]
--------------------------------------------------------------
"""

csv_file_path = "../data/processed_data_only_entsoe.csv"
df = pd.read_csv(csv_file_path)

print(df)

#Total green per country
total_load = df[[col for col in df.columns if 'green' in col]].sum()

plt.figure(figsize=(10, 6))
plt.bar(total_load.index.str[:8], total_load.values, color='green')
plt.xlabel('Country')
plt.ylabel('Total Green Energy')
plt.title('Total Green Energy per Country')

plt.savefig('total_green_entsoe.png')
plt.show() #Do not remove the 'show' without incorporating a sleep delay. The '.savefig' operation is not sequential, and closing it too soon may result in the image not being saved.
plt.close()

#Total load per country
total_load = df[[col for col in df.columns if 'load' in col]].sum()

plt.figure(figsize=(10, 6))
plt.bar(total_load.index, total_load.values)
plt.xlabel('Country')
plt.ylabel('Total Load')
plt.title('Total Load per Country')

plt.savefig('total_load_entsoe.png')
plt.show()
plt.close()

"""--------------------------------------------------------------
#EXPLORATORY ANALYSIS 2 - Insights [2/8]
--------------------------------------------------------------
"""

csv_file_path = "../data/processed_data.csv"
df = pd.read_csv(csv_file_path)

print(df)

#Total load per country
total_load = df[[col for col in df.columns if 'load' in col]].sum()

plt.figure(figsize=(10, 6))
plt.bar(total_load.index, total_load.values)
plt.xlabel('Country')
plt.ylabel('Total Load')
plt.title('Total Load per Country')

plt.savefig('total_load_with_uk.png')
plt.show()
plt.close()

# Botplox for surplus
df_surplus = df[[col for col in df.columns if 'surplus' in col]]

plt.figure(figsize=(12, 8))
sns.boxplot(data=df_surplus, palette='Set3')
plt.title('Boxplot of Surplus')
plt.xticks(rotation=45)

plt.savefig('surplus_plotbox.png')
plt.show()
plt.close()

# STD Hour
df['Time'] = pd.to_datetime(df['Time'])
df['Hour'] = df['Time'].dt.hour

mean_load = df.groupby('Hour')[[col for col in df.columns if 'surplus' in col]].mean()
std_load = df.groupby('Hour')[[col for col in df.columns if 'surplus' in col]].std()

plt.figure(figsize=(12, 8))
for column in mean_load.columns:
    plt.plot(mean_load.index, mean_load[column], label=column)
    plt.fill_between(mean_load.index, mean_load[column]-std_load[column], mean_load[column]+std_load[column], alpha=0.2)

plt.title('Mean and Standard Deviation of Surplus for Each Hour of the Day')
plt.xlabel('Hour')
plt.ylabel('Load')
plt.legend()

plt.savefig('surplus_std.png')
plt.show()
plt.close()