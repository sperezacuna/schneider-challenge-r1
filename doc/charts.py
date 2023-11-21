#Ensure that you have installed all the necessary dependencies. You can do this by executing "pip install NAME", for example, NAME=seaborn.1
import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from pandas import json_normalize


"""--------------------------------------------------------------
#EXPLORATORY ANALYSIS 1 - Insights [2/3]
--------------------------------------------------------------
"""

csv_file_path = "../data/processed_data_only_entsoe.csv"
df = pd.read_csv(csv_file_path)

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
#EXPLORATORY ANALYSIS 2 - Insights [2/3]
--------------------------------------------------------------
"""

csv_file_path = "../data/processed_data.csv"
df = pd.read_csv(csv_file_path)

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
plt.ylabel('Surplus')
plt.legend()

plt.savefig('hour_surplus_std.png')
plt.show()
plt.close()

"""--------------------------------------------------------------
#EXPLORATORY ANALYSIS 2 - Insights [3/3]
--------------------------------------------------------------
"""
csv_file_path = "../data/processed_data.csv"
df = pd.read_csv(csv_file_path)

# (Training dataset) Pie chart group by 'label' and count the number of occurrences of each label 
label_counts = df['label'].value_counts()

plt.figure(figsize=(10, 6))
plt.pie(label_counts, labels=label_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Labels (Training dataset)')

plt.savefig('correct_training_labels.png')
plt.show()
plt.close()


# (prediction labels) Pie chart group by 'label' and count the number of occurrences of each label 
file_path = os.path.join(os.path.dirname(__file__), '../predictions/predictions.json')
with open(file_path, 'r') as file:
    json_data = json.load(file)

df = json_normalize(json_data).transpose()
df.columns = ['label']
label_counts = df['label'].value_counts()

plt.figure(figsize=(10, 6))
plt.pie(label_counts, labels=label_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Labels')

plt.savefig('predicted_labels.png')
plt.show()
plt.close()


csv_file_path = "../data/test-labeled.csv"
df = pd.read_csv(csv_file_path)

# (Correct test dataset) Pie chart group by 'label' and count the number of occurrences of each label 
label_counts = df['label'].value_counts()

plt.figure(figsize=(10, 6))
plt.pie(label_counts, labels=label_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribution of Labels (Training dataset)')

plt.savefig('correct_test_labels.png')
plt.show()
plt.close()

csv_file_path = "../data/processed_data.csv"
df = pd.read_csv(csv_file_path)

# STD Monthly
df['Time'] = pd.to_datetime(df['Time'])
df['Month'] = df['Time'].dt.month

mean_load = df.groupby('Month')[[col for col in df.columns if 'surplus' in col]].mean()
std_load = df.groupby('Month')[[col for col in df.columns if 'surplus' in col]].std()

plt.figure(figsize=(12, 8))
for column in mean_load.columns:
    plt.plot(mean_load.index, mean_load[column], label=column)
    plt.fill_between(mean_load.index, mean_load[column]-std_load[column], mean_load[column]+std_load[column], alpha=0.2)

plt.title('Mean and Standard Deviation of Surplus for Each Month')
plt.xlabel('Month')
plt.ylabel('Surplus')
plt.legend()

plt.savefig('monthly_surplus_std.png')
plt.show()
plt.close()

"""--------------------------------------------------------------
Others
--------------------------------------------------------------
"""

# Circle with 24 points
def calculate_circle_points(radius, num_points):
    theta = np.linspace(0, 2*np.pi, num_points)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x, y

num_points = 24 # Number of points to mark on the circle
radius = 1.0
x_circle, y_circle = calculate_circle_points(radius, num_points)
plt.figure(figsize=(6, 6))
plt.plot(x_circle, y_circle, label='Circle')
plt.scatter(x_circle, y_circle, color='red', label='Points')
for i, (x, y) in enumerate(zip(x_circle, y_circle)):
    plt.text(x, y, str(i+1), color='black', ha='center', va='center')
plt.axis('equal')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Circle with 24 Points')

plt.savefig('circle_24_points.png')
plt.show()
plt.close()