# Macinator Discord Bot

A personal Discord bot for a small private server, running on a Raspberry Pi.
Built with `discord.py` and a separate Flask backend that handles all database
access.

## Architecture

The project runs as **two independent processes**:

| Process | File | Role |
|---|---|---|
| Bot | `startup.py` | Connects to Discord, loads the cogs, handles commands |
| Backend | `backend.py` | Flask API on `localhost:5000`, owns the SQLite database |

The cogs never touch the database directly — they talk to the backend over
HTTP. This keeps the Discord layer and the data layer separate, and means the
backend can be tested on its own without a Discord connection.

Each feature lives in its own cog under `cogs/`, loaded at startup via
`load_extension`.

## Commands

| Command | Description |
|---|---|
| `!ping` | Check whether the bot is responding |
| `!m8b <question>` | Magic 8-Ball |
| `!coinflip` | Flip a coin |
| `!roll` | Roll a d20 |
| `!dmc_art` | Post a random image from the image folder |
| `!pi-status` | Show host statistics for the Raspberry Pi |
| `!balance` | Show your coin balance |
| `!daily` | Claim the daily coin reward |
| `!pay <user> <amount>` | Transfer coins to another user |
| `!top` / `!leaderboard` | Show the richest users |
| `!bj` | Play blackjack against the bot |
| `!highlow` / `!hl` | Play a higher-or-lower guessing game |
| `!bus` | Play the "ride the bus" card game |
| `!oc <name>` | Look up an original character |
| `!oc create` / `!oc set` / `!oc delete` / `!oc list` | Manage original characters |

The bot also posts a random image to a configured channel every six hours.

## Setup

### Requirements

- Python 3.9 or newer
- A Discord bot application ([Developer Portal](https://discord.com/developers/applications))
- A Google Gemini API key, if you want the OC question feature

### Installation

```bash
git clone https://github.com/Kriegerp/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### Configuration

Copy the example environment file and fill in your own values:

```bash
cp .env.example .env
```

| Variable | What it is |
|---|---|
| `DISCORD_TOKEN` | Bot token from the Discord Developer Portal |
| `GEMINI_API_KEY` | Google Gemini API key |
| `OWNER_ID` | Your own Discord user ID |
| `IMAGE_CHANNEL_ID` | Channel ID the image loop posts to |

To get IDs, enable Developer Mode in Discord under
*Settings → Advanced*, then right-click a user or channel and choose
*Copy ID*.

You also need an `images/` folder next to `startup.py` containing the pictures
the bot should post. It is not part of this repository.

### Running

Both processes are needed. Start the backend first, since the bot's economy
commands depend on it:

```bash
python3 backend.py     # creates data.db on first run
python3 startup.py
```

## Running as a service

The `units/` folder contains systemd unit files for running both processes
automatically on a Raspberry Pi.

**These are examples, not drop-in files.** They contain a hardcoded username
(`mok`) and paths (`/home/mok/bot`) that you have to change to match your own
system. After editing:

```bash
sudo cp units/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now discordbot discordbackend
```

Check the logs with:

```bash
journalctl -u discordbot -f
```

## Notes

- This bot was written for one specific private server, so some behaviour is
  hardcoded to that setup.
- `.env`, `data.db` and the `images/` folder are excluded from version control.

## License

MIT