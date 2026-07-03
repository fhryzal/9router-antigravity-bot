<div align="center">

<h1>9Router Antigravity Bot</h1>

**Automated batch tool for linking Google accounts to 9Router's Antigravity provider via OAuth. Handles login, Workspace TOS, and consent flow.**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Engine: DrissionPage](https://img.shields.io/badge/Engine-DrissionPage%20CDP-1a1a2e.svg)](https://github.com/g1879/DrissionPage)

</div>

---

> Uses [DrissionPage](https://github.com/g1879/DrissionPage) (CDP-based, no WebDriver) to control Chrome directly. No `navigator.webdriver` flag, no Selenium, significantly harder for Google to detect.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Output](#output)
- [Under the Hood](#under-the-hood)
- [Platform Setup](#platform-setup)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [License](#license)

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

> [!NOTE]
> DrissionPage installs automatically on first run. No manual setup needed.

---

## Usage

```bash
python3 bot.py                          # standard mode
python3 bot.py --fast                   # shorter delays for fast connections
python3 bot.py --delay 10               # 10s between accounts
python3 bot.py --file other-list.txt    # custom accounts file
```

### CLI Flags

| Flag | Default | Description |
|------|:---:|-------------|
| `--fast` | off | Less wait time between steps |
| `--delay N` | `3` | Seconds between accounts |
| `--file PATH` | `accounts.txt` | Path to accounts file |
| `--headless` | off | Background mode (experimental) |

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.8 or higher |
| **Browser** | Google Chrome or Chromium |
| **9Router** | Running at `http://localhost:20128/` |
| **DrissionPage** | Auto-installed on first run |

---

## How It Works

For each account in the file:

| Step | Action |
|:---:|--------|
| 1 | Opens Chrome with a fresh temp profile |
| 2 | Navigates to 9Router > Antigravity provider page |
| 3 | Clicks **Add Connection** |
| 4 | Confirms the risk notice modal |
| 5 | Waits for Google OAuth tab to open |
| 6 | Enters email, clicks Next |
| 7 | Enters password, clicks Next |
| 8 | Handles Workspace TOS ("I understand") if prompted |
| 9 | Handles OAuth consent ("Allow") |
| 10 | Verifies redirect back to 9Router |

Successfully linked accounts are removed from `accounts.txt`. Failed accounts are skipped and reported at the end.

---

## Output

```
   #  Email                                      Status       Time
  --  ----------------------------------------  ----------  ------
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
  -----------------------------------------------
  ✗  user3@example.com
     Google CAPTCHA triggered
```

---

## Under the Hood

### Multi-Strategy Input

Typing into Google's login fields uses 4 fallback methods:

| # | Strategy | Method |
|:---:|----------|--------|
| 1 | Native | Standard DrissionPage `.input()` |
| 2 | JS-backed | `.input(by_js=True)` |
| 3 | CDP keyboard | `Ctrl+A` > Backspace > type via DevTools |
| 4 | Raw JS | Direct `value` assignment + event dispatch |

If one fails, it falls through to the next.

### Fresh Profiles

Each account gets a new temporary browser profile, deleted after use. No cookie or session leakage between accounts.

### Google Consent Handling

The bot handles multiple consent pages automatically:

| Page | URL Pattern | Action |
|------|------------|--------|
| Workspace TOS | `workspacetermsofservice` | Click "I understand" |
| OAuth consent | `signin/oauth` | Click "Continue" / "Allow" |
| Checkbox consent | any | Tick unchecked boxes |
| Fallback | any Google page | JS scan for consent-like buttons |

Up to 10 consent steps are handled per account before giving up.

---

## Platform Setup

<details>
<summary><b>Linux (headless server)</b></summary>

```bash
sudo apt install xvfb
xvfb-run python3 bot.py
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
pip3 install DrissionPage
python3 bot.py
```

</details>

<details>
<summary><b>Windows</b></summary>

```cmd
pip install DrissionPage
python bot.py
```

</details>

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Google CAPTCHA | Increase delay (`--delay 10`), don't use `--headless`, avoid rapid back-to-back runs. 2FA accounts won't work. |
| Google tab doesn't open | Make sure 9Router is running and the URL loads in a normal browser. |
| Timeout errors | Use default mode (not `--fast`), check your internet. |
| DrissionPage install fails | `pip3 install --break-system-packages DrissionPage` on Ubuntu 24.04+ |

---

## Security

- `accounts.txt` is in `.gitignore` and won't be committed accidentally
- Each browser session uses an isolated temp profile, deleted after use
- No credentials are logged or transmitted anywhere except to Google's login page
- Runs entirely locally, no external servers

---

## License

MIT
