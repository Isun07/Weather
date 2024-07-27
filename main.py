"""
Created by N3evin
An application that displays time and weather information for Raspberry Pi
"""

from tkinter import *
import urllib.request
import json
import threading
import datetime
import sys

class MainApp:

    # Config
    location = "New York"  # {Country} or {Country, City} without parenthesis.
    url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/New%20York?include=fcst%2Cobs%2Chistfcst%2Cstats%2Cdays%2Chours%2Ccurrent%2Calerts&key=YOUR_API_KEY&options=beta&contentType=json"
    weatherRefresh = 600  # in seconds, default 10 minutes

    def __init__(self):
        # Variables
        self.dateString = None
        self.currentTempString = None
        self.currentWeatherImage = None
        self.weatherLastUpdateString = None
        self.content = None
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Thread variables
        self.weatherThread = threading.Timer(0, None)
        self.timeThread = threading.Timer(0, None)

        # Initialize the frame.
        self.top = Tk()
        self.top.attributes('-fullscreen', True)  # Set to fullscreen
        self.top.config(cursor="none", bg="black")
        self.top.title("WeatherPi v0.1")  # Title of app
        self.top.protocol('WM_DELETE_WINDOW', self.stop)  # When close, stop all thread
        self.top.geometry("480x320")

        # Configure the weight, so that widget will be centered.
        self.top.rowconfigure(0, weight=1)
        self.top.columnconfigure(0, weight=1)

        # Update weather and run
        self.updateWeather()
        self.run()

    # Retrieve weather from url and update weather.
    def updateWeather(self):
        try:
            result_bytes = urllib.request.urlopen(self.url)
            self.content = json.load(result_bytes)
        except urllib.error.HTTPError as e:
            error_info = e.read().decode()
            print('Error code: ', e.code, error_info)
            sys.exit()
        except urllib.error.URLError as e:
            error_info = e.read().decode()
            print('Error code: ', e.code, error_info)
            sys.exit()

    # Get the icon image for the current weather
    def getCurrentIcon(self):
        try:
            icon = PhotoImage(file="./images/" + self.content["currentConditions"]["icon"] + ".png")
        except Exception:
            icon = PhotoImage(file="./images/3200.png")
        return icon

    # Initial run start up.
    def run(self):
        # Display Current Time
        self.currentTimeString = StringVar()
        currentTime = Label(self.top, textvariable=self.currentTimeString, font=("Pixeled", 25, "bold"), fg="white", bg="black")
        currentTime.grid(row=0, column=0, columnspan=2)
        self.currentTimeString.set(datetime.datetime.now().strftime("%I:%M:%S %p"))

        # Display Date
        self.dateString = StringVar()
        dateInfo = Label(self.top, textvariable=self.dateString, fg="white", bg="black", font=(None, 20, "bold"))
        dateInfo.grid(row=1, column=0, columnspan=2)

        # Display Today Temperature
        self.currentTempString = StringVar()
        currentTemp = Label(self.top, textvariable=self.currentTempString, fg="white", bg="black", font=(None, 20, "bold"), justify="left")
        currentTemp.grid(row=2, column=0)

        # Display current weather images
        icon = self.getCurrentIcon()
        self.currentWeatherImage = Label(self.top, image=icon, bg="black")
        self.currentWeatherImage.image = icon
        self.currentWeatherImage.grid(row=2, column=1, padx=30)

        # Display Weather Last Update
        self.weatherLastUpdateString = StringVar()
        weatherLastUpdate = Label(self.top, textvariable=self.weatherLastUpdateString, fg="white", bg="black", font=(None, 10, "bold"))
        weatherLastUpdate.grid(row=3, column=0, columnspan=2)

        # Refresh data
        self.refreshWeather()
        self.refreshTime()

        self.top.mainloop()

    # Refresh weather data
    def refreshWeather(self):
        self.updateWeather()

        # Update current icon
        icon = self.getCurrentIcon()
        self.currentWeatherImage.configure(image=icon)
        self.currentWeatherImage.image = icon

        # Update current temperature text
        temp = float(self.content["currentConditions"]["temp"])
        highTemp = float(self.content["days"][0]["tempmax"])
        lowTemp = float(self.content["days"][0]["tempmin"])
        self.currentTempString.set(f"Current: {int(temp)}°\nHigh: {int(highTemp)}°\nLow: {int(lowTemp)}°")

        # Update weather last update
        self.weatherLastUpdateString.set("Last update: " + datetime.datetime.now().strftime("%I:%M:%S %p"))

        # Refresh Weather
        self.weatherThread = threading.Timer(self.weatherRefresh, self.refreshWeather)
        self.weatherThread.start()

    # Refresh Time info
    def refreshTime(self):
        # Update Time
        self.currentTimeString.set(datetime.datetime.now().strftime("%I:%M:%S %p"))

        # Update date
        day = datetime.datetime.today().weekday()
        self.dateString.set(self.days[day] + ", " + datetime.datetime.now().strftime("%d/%m/%Y"))

        # Refresh Time
        self.timeThread = threading.Timer(1, self.refreshTime)
        self.timeThread.start()

    # Kill all threads
    def stop(self):
        self.weatherThread.cancel()
        self.timeThread.cancel()
        self.top.destroy()

if __name__ == "__main__":
    MainApp()
