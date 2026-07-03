# 9Router Antigravity Bot

Automates adding Google accounts to 9Router's Antigravity provider. Handles the full OAuth flow — login, Workspace TOS, consent — so you don't have to click through it manually for every account.

Uses [DrissionPage](https://github.com/g1879/DrissionPage) (CDP-based, no WebDriver) to control Chrome directly, which avoids the usual automation detection.

---

## Requirements

| Requirement | Details |
|:------------|:--------|
| **Python** | 3.8 or higher |
| **Browser** | Google Chrome or Chromium |
| **9Router** | Running at `http://localhost:20128/` |
| **DrissionPage** | Auto-installed on first run |

---

## Quick Start

```bash
git clone https://github.com/fhryzal/9router-antigravity-bot.git
cd 9router-antigravity-bot
```

Create `accounts.txt` with one account per line:

```
email@example.com|password
another@example.com|password
```

Run:

```bash
python3 bot.py
```

> DrissionPage installs automatically on first run. No manual setup needed.

---

## Usage

```bash
python3 bot.py                          # standard mode
python3 bot.py --fast                   # shorter delays for fast connections
python3 bot.py --delay 10               # 10s between accounts
python3 bot.py --file other-list.txt    # custom accounts file
```

### Options

| Flag | Default | What it does |
|:-----|:--------|:-------------|
| `--fast` | off | Less wait time between steps |
| `--delay N` | `3` | Seconds between accounts |
| `--file PATH` | `accounts.txt` | Path to accounts file |
| `--headless` | off | Background mode *(experimental)* |

---

## How It Works

For each account in the file, the bot:

| Step | Action |
|:-----|:-------|
| 1 | Opens Chrome with a fresh temp profile |
| 2 | Navigates to 9Router → Antigravity provider page |
| 3 | Clicks **Add Connection** |
| 4 | Confirms the risk notice modal |
| 5 | Waits for Google OAuth tab to open |
| 6 | Enters email → clicks Next |
| 7 | Enters password → clicks Next |
| 8 | Handles Workspace TOS ("I understand") if prompted |
| 9 | Handles OAuth consent ("Allow") |
| 10 | Verifies redirect back to 9Router |

Successfully linked accounts are automatically removed from `accounts.txt`. Failed accounts are skipped and reported — they don't block the rest of the queue.

---

## Output

The bot prints a live table with colored status and a summary box:

```
   #  Email                                      Status       Time
  ──  ──────────────────────────────────────────  ──────────  ──────
   1  user1@example.com                              OK       18.2s
   2  user2@example.com                              OK       21.5s
   3  user3@example.com                             FAIL      34.1s
   4  user4@example.com                              OK       19.7s
   5  user5@example.com                              OK       20.3s

  [████████████████████████████████████░░░░░] 5/5 (100%)

  ┌──────────────────────────────────────┐
  │  SESSION COMPLETE                    │
  ├──────────────────────────────────────┤
  │  Total           5    accounts       │
  │  Success         4    (80%)          │
  │  Failed          1                   │
  │  Duration      119s                  │
  │  Avg/acct     23.8s                  │
  └──────────────────────────────────────┘

  Failed accounts:
  ──────────────────────────────────────────────
  ✗  user3@example.com
     Google CAPTCHA triggered
```

---

## Under the Hood

### Anti-Detection

DrissionPage talks to Chrome via the **Chrome DevTools Protocol** directly — no WebDriver binary, no Selenium, no `navigator.webdriver` flag. Google has a much harder time detecting this compared to Selenium or Puppeteer.

### Multi-Strategy Input

Typing into fields uses 4 fallback methods to handle different page states:

| Strategy | Method |
|:---------|:-------|
| 1 | Native `.input()` — standard DrissionPage |
| 2 | JS-backed `.input(by_js=True)` |
| 3 | CDP keyboard — `Ctrl+A → Backspace → type` |
| 4 | Raw JS — direct `value` assignment + event dispatch |

If one fails, it falls through to the next.

### Fresh Profiles

Each account gets a new temporary browser profile, deleted after use. No cookie/session leakage between accounts.

### Google Consent Handling

The bot handles multiple consent pages automatically:

| Page | URL Pattern | Action |
|:-----|:-----------|:-------|
| Workspace TOS | `workspacetermsofservice` | Click "I understand" |
| OAuth consent | `signin/oauth` | Click "Continue" / "Allow" |
| Checkbox consent | any | Tick unchecked boxes |
| Fallback | any Google page | JS scan for consent-like buttons |

Up to 10 consent steps handled per account before giving up.

---

## Platform Setup

<details>
<summary><strong>Linux (headless server)</strong></summary>

```bash
sudo apt install xvfb
xvfb-run python3 bot.py
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
pip3 install DrissionPage
python3 bot.py
```

</details>

<details>
<summary><strong>Windows</strong></summary>

```cmd
pip install DrissionPage
python bot.py
```

</details>

---

## Troubleshooting

| Problem | Fix |
|:--------|:----|
| Google CAPTCHA | Increase delay (`--delay 10`), don't use `--headless`, avoid back-to-back runs. 2FA accounts won't work. |
| Google tab doesn't open | Make sure 9Router is running and the URL loads in a normal browser. |
| Timeout errors | Use default mode (not `--fast`), check your internet. |
| DrissionPage install fails | `pip3 install --break-system-packages DrissionPage` on Ubuntu 24.04+ |

---

## Security

- `accounts.txt` is in `.gitignore` — won't be committed accidentally
- Each browser session uses an isolated temp profile, deleted after use
- No credentials are logged or transmitted anywhere except to Google's login page
- Runs entirely locally — no external servers

---

## License

MIT
