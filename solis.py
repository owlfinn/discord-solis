import disnake
from disnake.ext import commands
import requests
import datetime

BASE_URL = 'http://api.openweathermap.org/data/2.5/'
API_KEY = open("API_WEATHER.txt", 'r').read()
TOKEN_BOT = open("DISCORD_BOT_TOKEN.txt", 'r').read()

bot = commands.Bot(command_prefix='!',
                   intents=disnake.Intents.all()
)

def get_date(timezone): # gets the localtime
    tz = datetime.timezone(datetime.timedelta(seconds=int(timezone)))
    
    return datetime.datetime.now(tz = tz).strftime("%H:%M, %d/%m/%y")

@bot.event
async def on_ready():
    print("ready")

@bot.slash_command(name='ping', description='see the ping of the bot')
async def ping(inter):
    await inter.send(f"latency {round(bot.latency * 1000)} ms")

@bot.slash_command(name='caesar-encoder', description='use caesar cipher to encode your text')
async def encoder(inter, text: str, pattern: int):
    result = ""

    for i in range(len(text)):
        char = text[i]
        if char.isalpha():
            if (char.isupper()):
                result += chr((ord(char) + pattern-65) % 26 + 65)
            else:
                result += chr((ord(char) + pattern-97) % 26 + 97)
        else:
            result += char

    await inter.send(f'Encoded text: {result}')

@bot.slash_command(name='caesar-decoder', description='use caesar cipher to decode your text')
async def decoder(inter, text: str, pattern: int):
    result = ""

    for i in range(len(text)):
        char = text[i]
        if char.isalpha():
            if (char.isupper()):
                result += chr((ord(char) - pattern-65) % 26 + 65)
            else:
                result += chr((ord(char) - pattern-97) % 26 + 97)
        else:
            result += char

    await inter.send(f'Encoded text: {result}')

@bot.slash_command(name='forecast', description='forecast weather 6 days')
async def forecast(inter, city):
    forecast_url = f'{BASE_URL}forecast?appid={API_KEY}&q={city}&units=metric'
    forecast_response = requests.get(forecast_url).json()
    cod =  forecast_response.get('cod')

    forecast_embed = disnake.Embed(
        title='Forecast',
        description=f'Conditions for the next 5 DAYS and today (`{city.upper()}`)\n(`MAX, MIN`)',
        color=disnake.Colour.yellow()
    )
    forecast_embed.set_author(
        name="Solis",
        icon_url="https://cdn.discordapp.com/app-icons/1179169125172527144/84824b41381955b38aee54370ddaef26.png"
    )

    if str(cod) != '200':
        embed_e = disnake.Embed(title=f'ERROR: {cod}', description=f'Try using the command again or check if the name is right')
        await inter.send(embed=embed_e)

        return # ends the function if cod isnt 200
    
    forecast_embed.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/jumpicon-agriculture-line/32/-_Sunny-Fields-Sun-Agriculture-Sunshine-Forecast-09-64.png")   
    temperature_data = {} # used for storing the max and min temps for each day

    for i in forecast_response['list']:
        time_forecasted = i['dt_txt'] # gets the time inside 'i'
        time_date, time_hour = time_forecasted.split(' ')
        temp_min = i['main']['temp_min']
        temp_max = i['main']['temp_max']

        year, month, day = time_date.split('-') 

        date_key = f'{day}/{month}/{year}'

        if date_key not in temperature_data: # checks if there is data for a determinated date already
            temperature_data[date_key] = {'max': temp_max, 'min': temp_min}
        else: # if the date_key is in temperature_data already it'll update the max/min
            temperature_data[date_key]['max'] = max(temperature_data[date_key]['max'], temp_max)
            temperature_data[date_key]['min'] = min(temperature_data[date_key]['min'], temp_min)

    for date, temps in temperature_data.items(): # add data to forecast embed
        forecast_embed.add_field(date, f"{temps['max']}ºC | {temps['min']}ºC")

    print(temperature_data)

    await inter.send(embed=forecast_embed)

@bot.slash_command(name='climate', description='see the climate of your city !')
async def climate(inter, city):
    # config api
    weather_url = f'{BASE_URL}weather?appid={API_KEY}&q={city}&units=metric'
    weather_response = requests.get(weather_url).json()
    cod =  weather_response.get('cod') # normal is 200
    
    weather_embed = disnake.Embed(
        title='Weather',
        description=f'Conditions (`{city.upper()}`)',
        color=disnake.Colour.yellow()
    )  
    weather_embed.set_author(
        name="Solis",
        icon_url="https://cdn.discordapp.com/app-icons/1179169125172527144/84824b41381955b38aee54370ddaef26.png"
    )

    if str(cod) != '200':
        embed_e = disnake.Embed(title=f'ERROR: {cod}', description=f'Try using the command again or check if the name is right')
        await inter.send(embed=embed_e)

        return # ends the function if cod isnt 200
    
    icon = weather_response['weather'][0]['icon']
    temp_w = weather_response['main']['temp']
    humidity = weather_response['main']['humidity']
    description_w = weather_response['weather'][0]['description']
    
    localtime = get_date(weather_response['timezone'])

    weather_embed.add_field('Temp', f'{round(temp_w)}ºC')
    weather_embed.add_field('Humidity', f'{humidity}%')
    weather_embed.add_field('Local Time', localtime)
    weather_embed.add_field('Description', description_w)
    weather_embed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{icon}@2x.png")

    await inter.send(embed=weather_embed)

bot.run(TOKEN_BOT) # runs the bot