import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import matplotlib.pyplot as plt

urls = ['https://www.hamradio.com/detail.cfm?pid=H0-016772', 'https://www.radioddity.com/products/xiegu-g90-hf-transceiver', 'https://amazon.com/dp/B08X6Z6KN2']
hostname = None

prices = []
price = None


def addToDatabase(price, url):
	conn = sqlite3.connect('G90_prices.db')
	c = conn.cursor()
	c.execute('CREATE TABLE IF NOT EXISTS prices (date text, price text, website text)')
	hostname = urlparse(url).hostname
	c.execute('INSERT INTO prices VALUES (?, ?, ?)', (datetime.today().strftime('%Y-%m-%d'), price.replace('$', ''), hostname))
	conn.commit()
	conn.close()




for url in urls:
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	if 'radioddity' in url:
		# <span class="price-item price-item--sale price-item--last">
        #   <span class="money">$445.00</span>
        # </span>
        
        # Use both price-item and money to get the price
        # Get parent element .price-item
		parent = soup.find('span', class_='price-item')
		# Get the child element money of parent
		price = parent.find('span', class_='money').text
		if price is None:
			price = 'Not available'

	elif 'amazon' in url:
		parent = soup.find('span', class_='a-price')
		# Get the child element money of parent
		whole = parent.find('span', class_='a-price-whole').text
		fraction = parent.find('span', class_='a-price-fraction').text
		price = "$" + whole + fraction
  
		if price is None:
			price = 'Not available'
   
	elif 'hamradio' in url:
		parent = soup.find('p', class_='addtoCart')
		# Get the child strong element and get the inner text
		price = parent.find('strong').text
   
	prices.append(price)
	addToDatabase(price, url)
	
 

 
 
average_price = str(sum([float(price.replace('$', '')) for price in prices]) / len(prices))
# round to 2 decimal places
average_price = "{:.2f}".format(float(average_price))


print("The prices of the Xiegu G90 are:")
print(prices)
print("On today, " + datetime.today().strftime('%Y-%m-%d') + ":")
print("The average price is $" + average_price)
lowest_price = min([float(price.replace('$', '')) for price in prices])
print("The lowest price is $" + "{:.2f}".format(lowest_price) + " at " + urls[prices.index("${:.2f}".format(lowest_price))] + ", which is $" + ("{:.2f}".format(abs(lowest_price - float(average_price)))) + " less than the average price.")

# Generate a graphic with the prices

# Convert prices to float for plotting
prices_float = [float(price.replace('$', '')) for price in prices]

# Extract hostnames from URLs
hostnames = [urlparse(url).hostname for url in urls]

plt.bar(hostnames, prices_float)
plt.ylabel('Price')
plt.xlabel('Website')
plt.ylim(min(prices_float) - 10, max(prices_float) + 10)
print(min(prices_float) - 50, max(prices_float) + 30)
plt.title('Prices of the Xiegu G90')
plt.savefig('prices.png')
plt.show()

# Generate historical data with the db for each website
conn = sqlite3.connect('G90_prices.db')
c = conn.cursor()
c.execute('SELECT * FROM prices')
data = c.fetchall()
conn.close()



# Group data by hostname
historical_data = {}
for row in data:
	date, price, hostname = row
	if hostname not in historical_data:
		historical_data[hostname] = {'dates': [], 'prices': []}
	historical_data[hostname]['dates'].append(date)
	historical_data[hostname]['prices'].append(float(price.replace('$', '')))

# Plot historical data for each website
for hostname, values in historical_data.items():
	plt.plot(values['dates'], values['prices'], label=hostname)

plt.ylabel('Price')
plt.xlabel('Date')
plt.title('Historical Prices of the Xiegu G90')
plt.legend()
plt.savefig('historical_prices.png')
plt.show()
