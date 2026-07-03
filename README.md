# 9Router Antigravity Bot

Automates adding Google accounts to 9Router's Antigravity provider. Handles the full OAuth flow — login, Workspace TOS, consent — so you don't have to click through it manually for every account.

Uses [DrissionPage](https://github.com/g1879/DrissionPage) (CDP-based, no WebDriver) to control Chrome directly, which avoids the usual automation detection.

## Requirements

- Python 3.8+
- Google Chrome or Chromium
- 9Router running at `http://localhost:20128/`

DrissionPage installs automatically on first run.

## Setup

```bash
git clone https://github.com/fhryzal/9router-antigravity-bot.git
cd 9router-antigravity-bot
```

Create `accounts.txt` with one account per line:

```
email@example.com|password
another@example.com|password
```

## Usage

```bash
python3 bot.py                          # standard mode
python3 bot.py --fast                   # shorter delays for fast connections
python3 bot.py --delay 10               # 10s between accounts
python3 bot.py --file other-list.txt    # custom accounts file
```

| Flag | Default | What it does |
|:-----|:--------|:-------------|
| `--fast` | off | Less wait time between steps |
| `--delay N` | `3` | Seconds between accounts |
| `--file PATH` | `accounts.txt` | Path to accounts file |
| `--headless` | off | Background mode (experimental) |

## What it does

For each account:

1. Opens Chrome with a fresh temp profile
2. Goes to `localhost:20128` → Antigravity → clicks Add
3. Confirms the risk modal
4. Waits for Google login tab
5. Enters email/password
6. Handles "Welcome to your new account" (Workspace TOS) if it shows up
7. Clicks Allow on OAuth consent
8. Verifies redirect back to 9Router
9. Removes the account from `accounts.txt` on success
10. Closes browser, cleans up temp data, moves to next

Failed accounts are skipped and reported at the end — they don't block the rest.

## Output

```
   #  Email                                      Status       Time
  ──  ──────────────────────────────────────────  ──────────  ──────
   1  user1@example.com                              OK       18.2s
   2  user2@example.com                              OK       21.5s
   3  user3@example.com                             FAIL      34.1s

  ┌──────────────────────────────────────┐
  │  SESSION COMPLETE                    │
  ├──────────────────────────────────────┤
  │  Total           3    accounts       │
  │  Success         2    (67%)          │
  │  Failed          1                   │
  │  Duration       79s                  │
  └──────────────────────────────────────┘
```

## Notes

**Input strategies** — typing into Google's login fields uses 4 fallback methods (native → JS → CDP keyboard → raw JS). If one doesn't work on a particular page state, it tries the next.

**Fresh profiles** — every account gets its own temp browser profile, deleted after use. No session leakage between accounts.

**Google consent handling** — the bot loops through up to 10 consent steps per account, matching buttons by text (`I understand`, `Continue`, `Allow`, etc.) and falling back to JS scanning if the normal selectors miss.

## Platform notes

**Linux (headless server):**
```bash
sudo apt install xvfb
xvfb-run python3 bot.py
```

**macOS:**
```bash
pip3 install DrissionPage
python3 bot.py
```

**Windows:**
```cmd
pip install DrissionPage
python bot.py
```

## Troubleshooting

**Google CAPTCHA** — increase delay (`--delay 10`), don't use `--headless`, don't run too many accounts back-to-back. Accounts with 2FA won't work.

**Tab doesn't open** — make sure 9Router is actually running and the URL loads in a regular browser.

**DrissionPage install fails** — try `pip3 install --break-system-packages DrissionPage` on Ubuntu 24.04+.

## License

MIT
