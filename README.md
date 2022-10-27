# CTF Helper

A Discord Bot for CTF Crafting based on [Pycord](https://pycord.dev/github).

## Application

Clone this repository to your computer.

```bash
git clone https://github.com/Cnily03/ctf-bot.git
```

Install requirements.

```bash
pip install -r requirements.txt
```

or if you use Poetry to manage your project, install as following.

```bash
poetry install
```

Make file `token` at root directory, which contains your Discord Bot Token.

Then start the program.

```bash
python .
```

## Configure

Edit `config.yml` at the root directory.

## Development

### Class `AppPlugin`

`AppPlugin` is a abstract class for developers to create various plugins with colorful functions.

The implementation of API to connect with `bot` is method `apphandler` with a param `bot` in type `discord.Bot`.

#### Prototype of `AppPlugin`

```python
class AppPlugin:
    def apphandler(self, bot: discord.Bot): pass
```

### Class `BotController`

`BotController` is a packed abstract class of `discord.Bot`, which can help control the bot more easily.

#### Prototype of `BotController`

```python
class BotController:
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    def use(self, plugin: AppPlugin):
        plugin.apphandler(self.bot)
```

### Example

```python
class CustomPlugin(AppPlugin):
    # do something here
    def apphandler(self, bot: discord.Bot):
        #do something here
bot = discord.Bot()
app = BotController(bot)
app.use(CustomPlugin())
```

Many functions in this project is implemented by this way.

## Usage

### Register commands

All the commands python file is in `commands`.

Remember to modify `register_args` in `__main__.py` after adding  or removing a command.
