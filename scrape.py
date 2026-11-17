import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

URLS = [
    'https://www.hamradio.com/detail.cfm?pid=H0-016772',
    'https://www.radioddity.com/products/xiegu-g90-hf-transceiver',
    'https://www.amazon.com/dp/B08X6Z6KN2',
    'https://www.randl.com/index.php?main_page=product_info&products_id=75815'
]

DB_FILE = 'G90_prices.db'
IMAGE_FILE = 'G90_prices.png'


def add_to_database(price, url):
	print(f"Adding {price} from {url}")
	# """Save price to database."""
	# conn = sqlite3.connect(DB_FILE)
	# c = conn.cursor()
	# c.execute('CREATE TABLE IF NOT EXISTS prices (date text, price text, website text)')
	# hostname = urlparse(url).hostname
	# c.execute('INSERT INTO prices VALUES (?, ?, ?)', (datetime.today().strftime('%Y-%m-%d'), price.replace('$', ''), hostname))
	# conn.commit()
	# conn.close()


def extract_price_radioddity(soup):
	"""Extract price from Radioddity product page."""
	parent = soup.find('span', class_='price-item')
	if parent:
		money_span = parent.find('span', class_='money')
		return money_span.text if money_span else 'Not available'
	return 'Not available'


def extract_price_amazon(soup):
	"""Extract price from Amazon product page."""
	parent = soup.find_all('span', class_='a-offscreen')
	return parent[0].text if parent else 'Not available'


def extract_price_hamradio(soup):
	"""Extract price from Hamradio product page."""
	parent = soup.find('p', class_='addtoCart')
	if parent:
		strong = parent.find('strong')
		return strong.text if strong else 'Not available'
	return 'Not available'


def extract_price_randl(soup):
	"""Extract price from R&L Electronics product page."""
	parent = soup.find('h2', id='productPrices')
	if parent:
		span = parent.find('span', class_='productBasePrice')
		return span.text.strip() if span else 'Not available'
	return 'Not available'


def scrape_prices(urls):
	"""Scrape prices from all URLs."""
	prices = []
	for url in urls:
		page = requests.get(url)
		soup = BeautifulSoup(page.content, 'html.parser')

		if 'radioddity' in url:
			price = extract_price_radioddity(soup)
		elif 'amazon' in url:
			price = extract_price_amazon(soup)
		elif 'hamradio' in url:
			price = extract_price_hamradio(soup)
		elif 'randl' in url:
			price = extract_price_randl(soup)
		else:
			price = 'Not available'

		prices.append(price)
		if price != 'Not available':
			add_to_database(price, url)

	return prices


def print_daily_summary(prices):
	"""Print pricing summary."""
	valid_prices = [float(price.replace('$', '')) for price in prices if price != 'Not available']

	print("The prices of the Xiegu G90 are:")
	print(prices)
	print(f"On today, {datetime.today().strftime('%Y-%m-%d')}:")

	if valid_prices:
		average_price = "{:.2f}".format(sum(valid_prices) / len(valid_prices))
		print(f"The average price is ${average_price}")

		lowest_price = min(valid_prices)
		lowest_price_str = f"${lowest_price:.2f}"

		for i, price in enumerate(prices):
			if price == lowest_price_str:
				difference = abs(lowest_price - float(average_price))
				print(f"The lowest price is ${lowest_price:.2f} at {URLS[i]}, which is ${difference:.2f} less than the average price.")
				break
	else:
		print("The average price is N/A")


def generate_graph():
	"""Generate price trend graph from database."""
	conn = sqlite3.connect(DB_FILE)
	c = conn.cursor()
	c.execute('SELECT date, price FROM prices')
	rows = c.fetchall()
	conn.close()

	if not rows:
		print("No price data available to plot.")
		return

	dates = []
	prices = []
	for date, price in rows:
		if price != 'Not available':
			dates.append(date)
			prices.append(float(price))

	date_price_dict = {}
	for date, price in zip(dates, prices):
		date_price_dict.setdefault(date, []).append(price)

	sorted_dates = sorted(date_price_dict.keys())
	min_prices = [min(date_price_dict[date]) for date in sorted_dates]

	dates_dt = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]

	plt.figure(figsize=(10, 6))
	plt.plot(mdates.date2num(dates_dt), min_prices)
	plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
	plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
	plt.ylabel('Price')
	plt.title('Lowest Daily Price of Xiegu G90 over time')
	plt.xticks(rotation=45)
	plt.tight_layout()
	plt.savefig(IMAGE_FILE, bbox_inches='tight')
	plt.show()


if __name__ == '__main__':
	prices = scrape_prices(URLS)
	print_daily_summary(prices)
	generate_graph()
