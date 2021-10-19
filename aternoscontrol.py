from gevent import monkey
monkey.patch_all()
from discord.ext import commands
import discord
from discord_slash import SlashCommand
from flask import Flask
from flask_compress import Compress
from gevent.pywsgi import WSGIServer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread
import os
# https://antoinevastel.com/bots/datadome
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})
driver.get("https://aternos.org")
driver.execute_script('document.cookie="ATERNOS_SEC_i7yp5iowmp000000=ax4k0qqy0i000000;path=/";document.cookie="ATERNOS_SESSION=ObL4sV72QkiTWL3dZQUIVn0tWPAmfy56PyPUELNwRWQrdIOgixCWJ1BZQWSKMsmBtlSKXTe05qSSUwEoimDJZZsc8Sab9xhXCn6n;path=/";document.cookie="ATERNOS_SERVER=0ENnLybXxIMMTnsC;path=/";var xmlhttp=new XMLHttpRequest();xmlhttp.open("GET", "/panel/ajax/start.php?SEC=i7yp5iowmp000000:ax4k0qqy0i000000&TOKEN=xtKlLCbMBEWm1J3xwVdJ");xmlhttp.send();')

while True: pass
driver.find_element(By.ID, 'user').value = "MaliciousFiles"
driver.find_element(By.ID, 'password').value = "Tater2007aternos"
driver.run_script("login()")

for id in driver.find_elements(By.CLASS_NAME, "server-id"):
  if (id.innerHTML == "#0ENnLybXxIMMTnsC"):
    id.click();

while True: pass

bot = commands.Bot(command_prefix="!", case_insensitive=True)
bot.remove_command("help")

slash = SlashCommand(bot, sync_commands=True)

guildIDs = []

# element IDs: start, stop, statuslabel-label

def login(guild):
  driver = webdriver.Chrome(options=chrome_options)
  driver.get("https://aternos.org/go")

  driver.find_element(By.ID, 'user').value = os.environ[guild.id]['username']
  driver.find_element(By.ID, 'password').value = os.environ[guild.id]['password']
  driver.run_script("login()")

  for id in driver.find_elements(By.CLASS_NAME, "server-id"):
    if (id.innerHTML == os.environ[guild.id]["id"]):
      id.click();
  
  return driver

@bot.event
async def on_ready():
  for guild in bot.guilds:
    guildIDs.append(guild.id)
    if not os.environ[guild.id]: os.environ[guild.id] = {}

  await bot.change_presence(activity=discord.Game(name="!help |  /help"))

@bot.event
async def on_guild_join(guild):
  if not os.environ[guild.id]: os.environ[guild.id] = {}
  guildIDs.append(guild.id)

@bot.event
async def on_guild_remove(guild):
  guildIDs.remove(guild.id)
  del os.environ[guild.id]

async def start_aternos_server(ctx):
  login(ctx.guild).find_element(By.ID, "start").click()

@slash.slash(description="Start the Aternos server", guild_ids=guildIDs)
async def startserver(ctx):
  await start_aternos_server(ctx)

@bot.command(name="startserver")
async def start_server_bot(ctx):
  await start_aternos_server(ctx)

async def setup_credentials(ctx):  
  for var in ["username", "password", "server id"]:
    await ctx.author.send(embed=discord.Embed(title="Aternos ".join(s.title() for s in var.split()), description="Enter your Aternos "+var, colour=discord.Colour.from_rgb(43,135,211)))

    os.environ[ctx.guild.id][var.split()[-1]] = bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel == ctx.author.createDM());

  login(ctx.guild).close()
  
@slash.slash(description="Setup Aternos credentials", guild_ids=guildIDs)
async def setup(ctx):
  await setup_credentials(ctx)

@bot.command(name="start_server")
async def setup_bot(ctx):
  await setup_credentials(ctx)

@bot.command()
async def help(ctx):
  embed = discord.Embed(title="Aternos Control Help", description="""
  ***Commands*** | Prefix is `>`, or slash command
  **namecolor <color>**: *Sets your name color to **<color>**, which can be a Hex [#ffffff], RGB [rgb(255, 255, 255)], or a Preset [white]. `None` to clear.*
  **help**: *Shows this help page.*
  ------------------------------------------------------------""", colour=discord.Colour.green())
  await ctx.send(embed=embed)

app = Flask('')

@app.route('/')
def home():
  return "Name Color Change active!"

def run():
  WSGIServer(('0.0.0.0', 8080), app).serve_forever()

compress = Compress()
compress.init_app(app)
Thread(target=run).start()

bot.run(os.environ["token"])
