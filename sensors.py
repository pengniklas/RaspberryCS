import time
import board
import adafruit_dht
import sqlite3
import RPi.GPIO as GPIO

# Warten auf app.py
time.sleep(10)

# GPIO  Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.IN) 

# DHT11-Sensors einrichten
dht_device = adafruit_dht.DHT11(board.D4)

#Datenbank Setup
conn = sqlite3.connect('sensor_data.db')
c = conn.cursor()

while True:
    try:
        # Messung
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        liquid_level = 'Ja' if GPIO.input(17) else 'Nein'
        uv_level = 'Ja' if GPIO.input(27) else 'Nein'
        
        # Resultate Terminal
        print(f"Temperatur: {temperature} °C, Luftfeuchtigkeit: {humidity} %, Niederschlag: {liquid_level}, Sonnenlicht: {uv_level}")

        # Datenbank befüllen
        c.execute('''
            INSERT INTO sensor_data (timestamp, temperature, humidity, liquid_level, uv_level)
            VALUES (datetime('now'), ?, ?, ?, ?)
        ''', (temperature, humidity, liquid_level, uv_level))
        conn.commit()

    except RuntimeError as error:
        print(f"RuntimeError: {error}")

    except Exception as e:
        print(f"Unbekannter Fehler: {e}")

    time.sleep(60)  # Messinterval 1min 

conn.close()
GPIO.cleanup()