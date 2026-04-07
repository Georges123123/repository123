from flask import Flask, render_template, request
import requests

app = Flask(__name__)

WEATHER_API_URL = 'https://api.open-meteo.com/v1/forecast'


def get_weather_description(code):
    descriptions = {
        0: 'Ясно',
        1: 'Преимущественно ясно',
        2: 'Переменная облачность',
        3: 'Пасмурно',
        45: 'Туман',
        48: 'Изморозь',
        51: 'Слабая морось',
        53: 'Морось',
        55: 'Сильная морось',
        61: 'Слабый дождь',
        63: 'Дождь',
        65: 'Сильный дождь',
        71: 'Слабый снег',
        73: 'Небольшой снег',
        75: 'Сильный снег',
        80: 'Ливень',
        95: 'Гроза'
    }
    return descriptions.get(code, 'Неизвестно')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forecast')
def get_forecast():
    try:
        latitude = request.args.get('lat', default=55.7558, type=float)
        longitude = request.args.get('lon', default=37.6173, type=float)

        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
            'timezone': 'auto',
            'forecast_days': 7
        }

        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()

        forecast_data = response.json()
        daily = forecast_data.get('daily', {})

        forecast_days = []
        for i in range(min(7, len(daily.get('time', [])))):
            forecast_days.append({
                'date': daily['time'][i],
                'temp_max': daily['temperature_2m_max'][i],
                'temp_min': daily['temperature_2m_min'][i],
                'weathercode': daily['weathercode'][i],
                'description': get_weather_description(daily['weathercode'][i])
            })

        return render_template(
            'forecast.html',
            forecast=forecast_days,
            latitude=latitude,
            longitude=longitude
        )

    except Exception as e:
        return render_template('error.html', error=str(e)), 500


if __name__ == '__main__':
    app.run(debug=True)
    