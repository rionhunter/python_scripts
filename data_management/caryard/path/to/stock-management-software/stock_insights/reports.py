# reports.py

import datetime
import pandas as pd
import matplotlib.pyplot as plt
import base64

from database.models import StockItem
from stock_insights.visualizations import generate_bar_chart

def generate_report():
    """
    Generates a report with insights into the stock inventory.

    Returns:
        report (str): Generated report as a string.
    """
    # Get current date and time
    current_date = datetime.datetime.now()
    report = f"Stock Insights Report - {current_date}\n\n"

    # Retrieve stock data from the database
    stock_items = StockItem.query.all()

    # Calculate stock availability
    available_stock = sum(item.quantity for item in stock_items if item.availability == 'Available')
    total_stock = sum(item.quantity for item in stock_items)

    # Add stock availability to the report
    report += f"Available Stock: {available_stock}\n"
    report += f"Total Stock: {total_stock}\n\n"

    # Generate sales trends chart
    sales_trends_chart = generate_sales_trends_chart(stock_items)
    report += sales_trends_chart

    return report

def generate_sales_trends_chart(stock_items):
    """
    Generates a sales trends chart based on the stock data.

    Args:
        stock_items (list): List of StockItem objects.

    Returns:
        sales_trends_chart (str): Sales trends chart as a string.
    """
    # Create a dataframe with stock data
    data = {'Car Name': [], 'Quantity Sold': []}
    for item in stock_items:
        data['Car Name'].append(item.car_name)
        data['Quantity Sold'].append(item.quantity_sold)
    df = pd.DataFrame(data)

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.barh(df['Car Name'], df['Quantity Sold'])
    plt.xlabel('Quantity Sold')
    plt.ylabel('Car Name')
    plt.title('Sales Trends')
    plt.tight_layout()
    plt.savefig('sales_trends.png')
    plt.close() # Close the figure after saving

    # Encode the chart as base64 and convert it to a string
    with open('sales_trends.png', 'rb') as file:
        encoded_chart = base64.b64encode(file.read()).decode('utf-8')

    # Generate the sales trends chart as a string
    sales_trends_chart = f"Sales Trends Chart:\n\n![Sales Trends](data:image/png;base64,{encoded_chart})\n\n"

    return sales_trends_chart