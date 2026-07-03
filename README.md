# 9Router × Antigravity — Batch OAuth Connector

Automated batch tool for linking Google accounts to [9Router](https://github.com/nicepkg/9router) Antigravity provider via OAuth.

Built with **Python + DrissionPage** — CDP-native browser automation with zero WebDriver footprint for maximum stealth.

---

## Features

- **Zero WebDriver detection** — DrissionPage uses Chrome DevTools Protocol directly, no `navigator.webdriver` flag
- **Multi-strategy input** — 4 fallback methods for typing into fields (native → JS → CDP keyboard → raw JS)
- **Auto-installer** — DrissionPage installs automatically on first run (with venv fallback for managed environments)
- **Fresh browser profile** per account — no session leakage between accounts
- **Rich terminal output** — colored table view, progress bar, session summary
- **Error resilience** — individual account failures don't stop the batch
- **Dual speed modes** — `--fast` for low-latency connections, default for standard internet
- **Cross-platform** — Windows, Linux, macOS

---

## Requirements

- Python 3.8+
- Google Chrome or Chromium
- 9Router running at `http://localhost:20128/`

DrissionPage is installed automatically — no manual setup needed.

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/9router-antigravity-bot.git
cd 9router-antigravity-bot
```

Create an `accounts.txt` file:

```
user1@example.com|mypassword123
user2@example.com|anotherpass456
user3@example.com|securepass789
```

> Format: `email|password` — one account per line.

---

## Usage

**Standard mode:**
```bash
python3 bot.py
```

**Fast mode (low-latency internet):**
```bash
python3 bot.py --fast
```

**Custom delay between accounts:**
```bash
python3 bot.py --delay 10
```

**Custom accounts file:**
```bash
python3 bot.py --file /path/to/my-accounts.txt
```

**Combined:**
```bash
python3 bot.py --fast --delay 5 --file accounts.txt
```

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--headless` | Off | Run browser in background (experimental) |
| `--fast` | Off | Reduced delays for fast connections |
| `--delay N` | `3` | Seconds to wait between accounts |
| `--file PATH` | `accounts.txt` | Path to accounts file |

---

## How It Works

For each account in the file, the bot:

1. Opens a fresh Chrome instance (isolated profile)
2. Navigates to the 9Router Antigravity provider page
3. Clicks **Add Connection**
4. Confirms the risk notice modal
5. Waits for the Google OAuth tab to open
6. Enters email → clicks Next
7. Enters password → clicks Next
8. Handles Workspace TOS ("I understand") if prompted
9. Handles OAuth consent ("Allow")
10. Verifies successful redirect back to 9Router
11. Removes the account from `accounts.txt` on success
12. Closes browser, cleans up temp data, moves to next account

---

## Output Example

```
     #  Email                                      Status       Time
  ────  ────────────────────────────────────────── ────────── ──────
     1  user1@example.com                              OK      23.4s
     2  user2@example.com                              OK      19.8s
     3  user3@example.com                             FAIL     31.2s

  ┌──────────────────────────────────────┐
  │  SESSION COMPLETE                    │
  ├──────────────────────────────────────┤
  │  Total           3    accounts       │
  │  Success         2    (67%)          │
  │  Failed          1                   │
  │  Duration       79s                  │
  │  Avg/acct     26.3s                  │
  └──────────────────────────────────────┘
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `DrissionPage not found` | Auto-installs on first run. If it fails: `pip install DrissionPage` |
| `accounts.txt not found` | Create the file with `email\|password` format |
| Add button not found | Ensure 9Router is running at `http://localhost:20128/` |
| Google tab doesn't open | Check if popups are blocked; try without `--headless` |
| Google CAPTCHA triggered | Increase delay: `--delay 10`; use non-headless mode |
| Timeout errors | Slow connection — use default mode (not `--fast`) |

---

## Security

- **DO NOT** commit `accounts.txt` to version control
- The `.gitignore` file excludes sensitive files by default
- Each browser session uses an isolated temp profile that is deleted after use

---

## License

MIT
