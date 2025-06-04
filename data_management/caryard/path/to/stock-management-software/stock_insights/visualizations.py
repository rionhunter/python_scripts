import matplotlib.pyplot as plt

def generate_stock_availability_chart(stock_data):
    """Generate a bar chart to visualize the stock availability."""
    stock_names = []
    stock_quantities = []
    
    for stock in stock_data:
        stock_names.append(stock.name)
        stock_quantities.append(stock.quantity)
    
    plt.bar(stock_names, stock_quantities)
    plt.xlabel('Stock Name')
    plt.ylabel('Stock Quantity')
    plt.title('Stock Availability')
    plt.xticks(rotation=45)
    
    plt.show()

def generate_sales_trends_chart(sales_data):
    """Generate a line chart to visualize the sales trends."""
    months = []
    sales = []
    
    for month, sale in sales_data.items():
        months.append(month)
        sales.append(sale)
    
    plt.plot(months, sales)
    plt.xlabel('Month')
    plt.ylabel('Sales')
    plt.title('Sales Trends')
    
    plt.show()