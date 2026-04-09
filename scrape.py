import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import matplotlib.pyplot as plt

urls = ['https://www.hamradio.com/detail.cfm?pid=H0-016772', 
        'https://www.radioddity.com/products/xiegu-g90-hf-transceiver',
        'https://www.amazon.com/dp/B08X6Z6KN2', 
        "https://www2.randl.com/index.php?main_page=product_info&products_id=75815"]
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
		# <div id="corePrice_feature_div" class="celwidget" data-feature-name="corePrice" data-csa-c-type="widget" data-csa-c-content-id="corePrice" data-csa-c-slot-id="corePrice_feature_div" data-csa-c-asin="B08X6Z6KN2" data-csa-c-is-in-initial-active-row="false" data-csa-c-id="5xz4s9-c15z71-4jbniq-44u0de" data-cel-widget="corePrice_feature_div">
        # <div data-csa-c-type="widget" data-csa-c-slot-id="apex_dp_offer_display" data-csa-c-content-id="apex_with_rio_cx" data-csa-c-id="9meg2n-xob7h1-fidyg-hdg9e3">
        # <div class="a-section a-spacing-micro">
        # <div class="a-section apex-core-price-identifier"> 
        # <span class="a-price aok-align-center apex-pricetopay-value" data-a-size="xl" data-a-color="base">
        # <span class="a-offscreen">$465.00</span><span aria-hidden="true">
        # <span class="a-price-symbol">$</span>
        # <span class="a-price-whole">465<span class="a-price-decimal">.</span></span>
        # <span class="a-price-fraction">00</span></span></span>
        # <span id="taxInclusiveMessage" class="a-size-mini a-color-base aok-align-center aok-nowrap"></span>
        # </div></div></div>

		price=corePrice_feature_div = soup.find('div', id='corePrice_feature_div')
		parent = soup.find_all('span', class_='a-offscreen')
		if parent:
			price = parent[0].text
		else:
			price = 'Not available'

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

# average the prices for the same date
date_price_dict = {}
for date, price in zip(dates, prices):
	# group prices by date
	date_price_dict.setdefault(date, []).append(price)

# sort dates so the plot is chronological
dates = sorted(date_price_dict.keys())
prices = [sum(date_price_dict[date]) / len(date_price_dict[date]) for date in dates]

# Convert dates to datetime objects
dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates]
# Plot the prices
plt.plot(dates, prices)
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Prices of Xiegu G90 over time')
plt.xticks(rotation=45)
plt.savefig('G90_prices.png', bbox_inches='tight')
plt.show()
