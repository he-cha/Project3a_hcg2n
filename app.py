
from datetime import datetime
import csv
import pygal
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort, Response
from api import TIME_SERIES_DAILY, TIME_SERIES_INTRADAY, TIME_SERIES_MONTHLY, TIME_SERIES_WEEKLY

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'



def read_symbols():
    with open('stocks.csv', newline='') as csvfile:
        fr = csv.reader(csvfile)
        sym = [row[0] for row in fr]
    return sym

@app.route("/", methods=["GET", "POST"])
def index():
    symbols = read_symbols()
    chart_svg = None

    if request.method == "POST":
        symbol = request.form["symbol"]
        chart_type = request.form["chart_type"]
        time_option = request.form["time"]
        interval = request.form["interval"] if time_option == "intra" else None
        start_date = datetime.strptime(request.form["start"], "%Y-%m-%d") if request.form["start"] else None
        end_date = datetime.strptime(request.form["end"], "%Y-%m-%d") if request.form["end"] else None




        if time_option == "intra" and interval:
            data = data.TIME_SERIES_INTRADAY(symbol, interval)
            time_series_key = f'Time Series ({interval}min)'
            time_series_data = data.get(time_series_key, {}) if data else None
            data_filter = time_series_data
        elif time_option == "daily":
            data = TIME_SERIES_DAILY(symbol)
            data_key = next((key for key in data.keys() if "Time Series" in key), None)
        elif time_option == "weekly":
            data = TIME_SERIES_WEEKLY(symbol)
            data_key = next((key for key in data.keys() if "Time Series" in key), None)
        elif time_option == "monthly":
            data = TIME_SERIES_MONTHLY(symbol)
            data_key = next((key for key in data.keys() if "Time Series" in key), None)

        if data and data_key in data:
            time_series_data = data.get(data_key, {})
            if start_date and end_date:
                data_filter = {
                    date: values for date, values in time_series_data.items()
                    if start_date <= datetime.strptime(date, "%Y-%m-%d") <= end_date
                }                   
            else: 
                data_filter = time_series_data
        else:
            flash(f"No data found")
            return redirect(url_for("index"))


        dates = []
        open_prices = []
        high_prices = [] 
        low_prices =[]
        close_prices =[]

        for date, values in sorted(data_filter.items(), reverse = True):
            dates.append(date)
            open_prices.append(float(values['1. open']))
            high_prices.append(float(values['2. high']))
            low_prices.append(float(values['3. low']))
            close_prices.append(float(values['4. close']))
        if chart_type == "bar":
            chart = pygal.Bar(x_label_rotation = 45)
        else:
            chart = pygal.Line(x_label_rotation = 45)
        
        chart.add("Open", open_prices)
        chart.add("High", high_prices)
        chart.add("Low", low_prices)
        chart.add("Close", close_prices)
        chart.x_labels = dates
        
        if time_option == 'intra':
            chart.title = f"Stock data for {symbol} ({interval}min)"
        else:
            chart.title = f"Stock data for {symbol}: {start_date} to {end_date}"
        
        chart_svg = chart.render(is_unicode=True)

        return render_template("index.html", symbols=symbols, chart_svg=chart_svg)
    
    return render_template("index.html", symbols=symbols, chart_svg=chart_svg)

if __name__ == "__main__":
    app.run(host="0.0.0.0")