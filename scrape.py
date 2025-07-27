import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import matplotlib.pyplot as plt

urls = ['https://www.hamradio.com/detail.cfm?pid=H0-016772', 'https://www.radioddity.com/products/xiegu-g90-hf-transceiver', 'https://www.amazon.com/dp/B08X6Z6KN2', "https://www2.randl.com/index.php?main_page=product_info&products_id=75815"]
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
		# <span class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay" data-a-size="xl" data-a-color="base">
		# <span class="a-offscreen"> </span><span aria-hidden="true"><span class="a-price-symbol">$</span>
		# <span class="a-price-whole">465<span class="a-price-decimal">.
		# </span></span><span class="a-price-fraction">00</span></span></span>

		# There are multiple elements with class 'a-price'
		# Find the first occurrence of class 'a-price'
		parent = soup.find_all('span', class_='a-price')
		if parent:
			first_parent = parent[0]
			whole_elem = first_parent.find('span', class_='a-price-whole')
			fraction_elem = first_parent.find('span', class_='a-price-fraction')
			if whole_elem and fraction_elem:
				whole = whole_elem.text.strip().replace(',', '')
				fraction = fraction_elem.text.strip()
				price = "$" + whole + "." + fraction

	elif 'hamradio' in url:
		parent = soup.find('p', class_='addtoCart')
		# Get the child strong element and get the inner text
		price = parent.find('strong').text
  
	elif 'randl' in url:
		parent = soup.find('h2', id='productPrices')
		if parent:
			price = parent.find('span', class_='productBasePrice').text.strip()

   
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


# Generate a graphic with the prices over time
# Get the dates from the database
conn = sqlite3.connect('G90_prices.db')
c = conn.cursor()
c.execute('SELECT date, price FROM prices')
rows = c.fetchall()
dates = []
prices = []
for row in rows:
	dates.append(row[0])
	prices.append(float(row[1]))
conn.close()

# Convert dates to datetime objects
dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
# Plot the prices
plt.plot(dates, prices)
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Prices of Xiegu G90 over time')
plt.xticks(rotation=45)
plt.savefig('G90_prices.png')
plt.show()
