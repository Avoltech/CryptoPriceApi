from flask import Flask
from flask import request
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

allowed_cryptos = pd.read_csv('cryptos_allowed.csv', header=None)[0].to_list()

app = Flask(__name__)

def cvtToUnixDate(dt):
	try:
		dt = datetime.datetime.strptime(dt, '%m-%d-%Y')
	except:
		dt = datetime.datetime.today()
	unix_dt = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
	return int(unix_dt)

def extractData(crypto_name, start, end):
	try:
		baseurl = 'https://finance.yahoo.com/quote/'
		url = baseurl + crypto_name + '-USD/history?' + 'period1=' + str(start) + '&period2=' + str(end)

		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		page = requests.get(url, headers=headers)
		soup = BeautifulSoup(page.content, 'html.parser')
		rows = soup.find(id='Col1-1-HistoricalDataTable-Proxy').find('table').find('tbody').find_all('tr')

		_date = []
		_open = []
		_high = []
		_low = []
		_close = []
		_adj_close = []
		_volume = []

		for row in rows:
			cells = row.find_all('td')
			if cells[6].text == '-':
				continue
			datetime_object = datetime.datetime.strptime(cells[0].text, '%b %d, %Y')
			_date.append(datetime_object)
			_open.append(float(cells[1].text.replace(',', '')))
			_high.append(float(cells[2].text.replace(',', '')))
			_low.append(float(cells[3].text.replace(',', '')))
			_close.append(float(cells[4].text.replace(',', '')))
			_adj_close.append(float(cells[5].text.replace(',', '')))
			_volume.append(int(cells[6].text.replace(',', '')))

		values = [_date, _open, _high, _low, _close, _adj_close, _volume]
		df = pd.DataFrame(list(zip(_date, _open, _high, _low, _close, _adj_close, _volume)), columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])
		df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
		df.set_index('Date', inplace=True)
		return df.to_json()
	except:
		return {}


@app.route('/')
def index():
	return f'API 1:<h3><i>/getNames</i></h3>Usage: <h4>https://crypto-api-yf.herokuapp.com/getNames</h4>==>Returns a list of crypto supported by yahoo finance \
	<br><br><br><br><br>API 2: <h3><i>/getData?name=&lt;insert_crypto_name_here&gt;&start=&lt;insert_start_date_here&gt;&end=&lt;insert_end_date_here&gt;</i></h3>Example: <h4>https://crypto-api-yf.herokuapp.com/getData?name=ETH&start=08-20-2021&end=08-30-2021</h4>==>Returns daily crypto data'



@app.route('/getData')
def getData():
	crypto_name = request.args.get('name')
	start = request.args.get('start')
	end = request.args.get('end')

	start = cvtToUnixDate(start)
	end = cvtToUnixDate(end)

	output = extractData(crypto_name, start, end)
	return f'{output}'

@app.route('/getNames')
def getNames():
	df = pd.read_csv('cryptos_allowed.csv', header=None)
	crypto_list = {'crypto_list': df[0].values.tolist()}

	return f'{crypto_list}'
