import asyncio
import aiohttp
import aioconsole  # Для асинхронного ввода
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, WeatherData
from datetime import datetime
import openpyxl

engine = create_engine('sqlite:///weather.db')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)
async def fetch_weather_data(session):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 55.7558,
        "longitude": 37.6173,
        "current_weather": "true"
    }
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            print("Данные успешно получены от API:", data)
            return data
        else:
            print(f"Ошибка получения данных. Статус: {response.status}")
            return None
def save_weather_data(data):
    try:
        current_weather = data.get('current_weather', {})
        if not current_weather:
            print("Нет данных о текущей погоде в ответе API")
            return

        weather = WeatherData(
            temperature=current_weather.get('temperature'),
            wind_speed=current_weather.get('windspeed'),
            wind_direction=current_weather.get('winddirection'),
            pressure=None,
            precipitation_type=current_weather.get('weathercode', 'No Data'),
            precipitation_amount=0.0,
            timestamp=datetime.utcnow()
        )
        session.add(weather)
        session.commit()
        print(f"Данные о погоде успешно добавлены в базу данных: {weather.timestamp}")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
async def fetch_weather_periodically():
    async with aiohttp.ClientSession() as http_session:
        while True:
            try:
                weather_data = await fetch_weather_data(http_session)
                if weather_data:
                    save_weather_data(weather_data)
                else:
                    print("Данные не получены, запись не будет выполнена.")
            except Exception as e:
                print(f"Ошибка при запросе данных: {e}")
            await asyncio.sleep(180)

def export_to_excel():
    try:
        weather_data = session.query(WeatherData).order_by(WeatherData.timestamp.desc()).all()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(
            ['Идентификатор', 'Температура', 'Скорость ветра',
             'Направление ветра', 'Давление', 'Код погоды',
             'Количество осадков', 'Временная метка'])
        for data in weather_data:
            ws.append(
                [data.id, data.temperature, data.wind_speed, data.wind_direction, data.pressure, data.precipitation_type,
                 data.precipitation_amount, data.timestamp])
        wb.save("weather_data.xlsx")
        print("Данные экспортированы в файл weather_data.xlsx")
    except Exception as e:
        print(f"Ошибка при экспорте данных в Excel: {e}")
async def handle_user_commands():
    while True:
        command = await aioconsole.ainput("Введите '1' для экспорта данных в Excel: ")
        if command == '1':
            export_to_excel()
async def main():
    task_weather = asyncio.create_task(fetch_weather_periodically())
    task_commands = asyncio.create_task(handle_user_commands())

    await asyncio.gather(task_weather, task_commands)

if __name__ == "__main__":
    asyncio.run(main())
