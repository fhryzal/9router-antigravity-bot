<div align="center">

<br>

```
 ██████╗ ██████╗  ██████╗ ██╗   ██╗████████╗███████╗██████╗
██╔═══██╗██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝██╔══██╗
╚██████╔╝██████╔╝██║   ██║██║   ██║   ██║   █████╗  ██████╔╝
 ╚═══██║ ██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  ██╔══██╗
 ██████║ ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗██║  ██║
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝
```

**Batch OAuth Connector for [9Router](https://github.com/nicepkg/9router) × Antigravity**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![DrissionPage](https://img.shields.io/badge/engine-DrissionPage_CDP-1a1a2e?style=flat-square)](https://github.com/g1879/DrissionPage)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey?style=flat-square)]()

*Zero WebDriver footprint. Multi-strategy input. Fully automated Google OAuth flow.*

<br>

</div>

---

## Why This Exists

Manually linking Google accounts to 9Router's Antigravity provider means clicking through the same OAuth flow over and over — open the dashboard, click Add, confirm the modal, log into Google, accept consent. For 5 accounts that's annoying. For 100+ it's not feasible.

This bot automates the entire flow end-to-end, one account at a time, with a fresh browser profile each run so sessions never leak between accounts.

---

## How It Works

```
┌─────────────┐     ┌───────────────┐     ┌──────────────────┐     ┌────────────┐
│  Read next   │────▶│  Open 9Router │────▶│  Click Add +     │────▶│  Google    │
│  account     │     │  Antigravity  │     │  Confirm modal   │     │  OAuth tab │
└─────────────┘     └───────────────┘     └──────────────────┘     └─────┬──────┘
                                                                         │
                    ┌───────────────┐     ┌──────────────────┐           │
                    │  Remove from  │◀────│  Handle consent  │◀──────────┘
                    │  accounts.txt │     │  I Understand →  │
                    │  on success   │     │  Allow → Done    │
                    └───────────────┘     └──────────────────┘
```

Each account goes through all 7 steps automatically. Failed accounts are skipped and reported — they don't block the queue.

---

## Quick Start

```bash
git clone https://github.com/fhryzal/9router-antigravity-bot.git
cd 9router-antigravity-bot
```

Create `accounts.txt`:

```
user1@example.com|password123
user2@example.com|password456
user3@example.com|password789
```

Run:

```bash
python3 bot.py
```

> DrissionPage installs automatically on first run. No manual setup needed.

---

## Usage

```bash
# Standard mode (recommended)
python3 bot.py

# Fast mode — shorter delays for fast connections
python3 bot.py --fast

# Custom delay between accounts (seconds)
python3 bot.py --delay 10

# Use a different accounts file
python3 bot.py --file /path/to/my-accounts.txt

# Combined
python3 bot.py --fast --delay 5 --file accounts.txt
```

### Options

| Flag | Default | Description |
|:-----|:--------|:------------|
| `--fast` | off | Reduced delays for low-latency connections |
| `--delay N` | `3` | Wait time between accounts in seconds |
| `--file PATH` | `accounts.txt` | Path to the accounts file |
| `--headless` | off | Run browser in background *(experimental)* |

---

## Output

The bot prints a live table with colored status badges and a summary box at the end:

```
   #  Email                                      Status       Time
  ──  ──────────────────────────────────────────  ──────────  ──────
   1  edwards1761@example.com                        OK       18.2s
   2  kaylynn148@example.com                         OK       21.5s
   3  jerimiah93@example.com                         OK       19.7s
   4  gavin69692@example.com                        FAIL      34.1s
   5  leona84334@example.com                         OK       20.3s

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
  ──────────────────────────────────────────────────
  ✗  gavin69692@example.com
     Google CAPTCHA triggered — try increasing delay
```

Successfully linked accounts are automatically removed from `accounts.txt`.

---

## Under the Hood

### Anti-Detection

DrissionPage communicates with Chrome via the **Chrome DevTools Protocol** directly — no WebDriver binary, no Selenium, no `navigator.webdriver` flag. This makes it significantly harder for Google to detect automation compared to traditional Selenium or Puppeteer setups.

### Multi-Strategy Input

Typing into fields uses **4 fallback strategies** to ensure reliability across different page states:

1. **Native `.input()`** — standard DrissionPage method
2. **JS-backed `.input(by_js=True)`** — JavaScript-driven clear + type
3. **CDP keyboard** — `Ctrl+A → Backspace → type` via Chrome DevTools
4. **Raw JS injection** — direct `value` assignment + event dispatch

If strategy 1 fails (value doesn't match), it falls through to 2, then 3, then 4.

### Fresh Profiles

Each account gets a **new temporary browser profile** created in the system temp directory. After the account is processed (success or failure), the profile is deleted. This prevents:

- Cookie/session leakage between accounts
- Google detecting multiple logins from the same browser profile
- Stale cache causing unexpected behavior

### Google Consent Flow

The bot handles the full Google OAuth consent chain:

| Page | URL Pattern | Action |
|:-----|:-----------|:-------|
| Workspace TOS | `workspacetermsofservice` | Click "I understand" |
| OAuth consent | `signin/oauth` | Click "Continue" / "Allow" |
| Checkbox consent | any | Check unchecked boxes |
| Generic fallback | any Google page | JS scan for consent-like buttons |

Up to 10 consent steps are handled per account before giving up.

---

## Requirements

| Requirement | Details |
|:------------|:--------|
| **Python** | 3.8 or higher |
| **Browser** | Google Chrome or Chromium |
| **9Router** | Running at `http://localhost:20128/` |
| **DrissionPage** | Auto-installed on first run |

### Platform Setup

<details>
<summary><strong>Linux</strong></summary>

```bash
chmod +x setup.sh && ./setup.sh
```

Or manually:
```bash
sudo apt install chromium-browser    # if Chrome not installed
pip3 install DrissionPage
```

For headless servers, install Xvfb:
```bash
sudo apt install xvfb
xvfb-run python3 bot.py
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install --cask google-chrome    # if not installed
pip3 install DrissionPage
python3 bot.py
```

</details>

<details>
<summary><strong>Windows</strong></summary>

```cmd
setup.bat
```

Or manually: install Chrome from [google.com/chrome](https://www.google.com/chrome/), then:
```cmd
pip install DrissionPage
python bot.py
```

</details>

---

## Troubleshooting

<details>
<summary><strong>Google asks for CAPTCHA</strong></summary>

- Increase delay: `--delay 10` or `--delay 15`
- Don't use `--headless` — visible browser triggers fewer CAPTCHAs
- Avoid running too many accounts back-to-back
- Make sure accounts don't have 2FA enabled

</details>

<details>
<summary><strong>Tab Google doesn't open</strong></summary>

- Make sure 9Router is running at `http://localhost:20128/`
- Open the URL manually in a browser to verify
- Check if popups are being blocked
- Try without `--headless`

</details>

<details>
<summary><strong>Timeout / slow connection</strong></summary>

- Use default mode (don't pass `--fast`)
- Increase delay: `--delay 10`
- Check your internet connection

</details>

<details>
<summary><strong>DrissionPage not installed</strong></summary>

It auto-installs on first run. If that fails:
```bash
pip3 install DrissionPage
```

On managed Python environments (Ubuntu 24.04+):
```bash
pip3 install --break-system-packages DrissionPage
```

</details>

---

## Security

- `accounts.txt` is in `.gitignore` — it will never be committed accidentally
- Each browser session uses an **isolated temp profile** that is deleted after use
- No credentials are logged, stored, or transmitted anywhere except to Google's login page
- The bot runs entirely locally — no external servers or APIs involved

---

## License

MIT — do whatever you want with it.
