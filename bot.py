#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  9Router × Antigravity — Batch OAuth Connector               ║
║  Auto-link Google accounts to 9Router Antigravity provider   ║
║  Engine: DrissionPage (CDP-native, zero WebDriver footprint) ║
╚══════════════════════════════════════════════════════════════╝
"""

# ── Bootstrap: auto-install DrissionPage if missing ──────────
import os, sys, subprocess, tempfile, shutil, random, time, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(SCRIPT_DIR, ".venv")


def _bootstrap():
    """Ensure DrissionPage is importable. Creates venv as fallback."""
    try:
        import DrissionPage  # noqa: F401
        return
    except ImportError:
        pass

    print("\n  ⏳  DrissionPage not found — installing automatically...\n")

    # Try direct pip first
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "DrissionPage"],
            stdout=sys.stdout, stderr=sys.stderr,
        )
        return
    except subprocess.CalledProcessError:
        pass

    # Fallback: create venv
    print("  ℹ  System pip blocked — creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    except subprocess.CalledProcessError:
        print("  ✗  Failed to create venv. Run: sudo apt install python3-venv")
        sys.exit(1)

    venv_py = os.path.join(
        VENV_DIR, "Scripts" if sys.platform == "win32" else "bin",
        "python.exe" if sys.platform == "win32" else "python3",
    )
    subprocess.check_call([venv_py, "-m", "pip", "install", "-q", "--upgrade", "pip"])
    subprocess.check_call([venv_py, "-m", "pip", "install", "DrissionPage"])
    print("  ✓  Installed in venv — restarting...\n")
    os.execv(venv_py, [venv_py] + sys.argv)


_bootstrap()

from DrissionPage import ChromiumPage, ChromiumOptions  # noqa: E402
from DrissionPage._units.actions import Keys             # noqa: E402

# ── Configuration ────────────────────────────────────────────
ROUTER_URL = "http://localhost:20128/dashboard/providers/antigravity"
DEFAULT_ACCOUNTS_FILE = os.path.join(SCRIPT_DIR, "accounts.txt")
DEFAULT_DELAY = 3

# ── Timing profiles ─────────────────────────────────────────
PROFILES = {
    "fast": {
        "page_load": 1, "after_add": 1, "after_confirm": 0.5,
        "tab_timeout": 10, "google_load": 1, "after_email": 0.5,
        "after_email_next": 2, "pw_timeout": 8, "after_pw": 0.5,
        "after_pw_next": 2, "step_wait": 1, "tos_timeout": 3,
        "after_tos": 1, "btn_timeout": 2, "after_btn": 1,
        "after_allow": 1, "no_btn_wait": 2, "redirect_wait": 2,
        "after_ok": 1,
    },
    "normal": {
        "page_load": 1, "after_add": 1, "after_confirm": 0.5,
        "tab_timeout": 15, "google_load": 3, "after_email": 1,
        "after_email_next": 4, "pw_timeout": 15, "after_pw": 1,
        "after_pw_next": 4, "step_wait": 2, "tos_timeout": 5,
        "after_tos": 2, "btn_timeout": 3, "after_btn": 2,
        "after_allow": 3, "no_btn_wait": 3, "redirect_wait": 3,
        "after_ok": 2,
    },
}

# ── ANSI color helpers ──────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_GREEN  = "\033[42m"
    BG_RED    = "\033[41m"
    BG_BLUE   = "\033[44m"
    BG_CYAN   = "\033[46m"


# ── Pretty output helpers ───────────────────────────────────
def banner():
    art = f"""{C.CYAN}{C.BOLD}
    ┌─────────────────────────────────────────────────────────┐
    │   ____  ____              _                             │
    │  / __ \\/ __ \\____  __  __/ /____  _____                 │
    │ / /_/ / /_/ / __ \\/ / / / __/ _ \\/ ___/                 │
    │ \\__, / _, _/ /_/ / /_/ / /_/  __/ /                     │
    │/____/_/ |_|\\____/\\__,_/\\__/\\___/_/                      │
    │                                                         │
    │   ×  A N T I G R A V I T Y   C O N N E C T O R         │
    │                                                         │
    │   Batch OAuth Linker for 9Router                        │
    │   Engine: DrissionPage (CDP)                            │
    └─────────────────────────────────────────────────────────┘{C.RESET}
    """
    print(art)


def table_header():
    print(f"\n  {C.BOLD}{C.WHITE}{'#':>4}  {'Email':<42} {'Status':<10} {'Time':>6}{C.RESET}")
    print(f"  {C.DIM}{'─'*4}  {'─'*42} {'─'*10} {'─'*6}{C.RESET}")


def table_row(idx, total, email, status, elapsed):
    if status == "OK":
        badge = f"{C.BG_GREEN}{C.WHITE}{C.BOLD}    OK    {C.RESET}"
    elif status == "FAIL":
        badge = f"{C.BG_RED}{C.WHITE}{C.BOLD}   FAIL   {C.RESET}"
    elif status == "SKIP":
        badge = f"{C.BG_BLUE}{C.WHITE}{C.BOLD}   SKIP   {C.RESET}"
    else:
        badge = f"{C.DIM}  {status:<8}{C.RESET}"

    masked = email.split("@")[0][:12] + "…@" + email.split("@")[1] if len(email) > 30 else email
    print(f"  {C.DIM}{idx:>4}{C.RESET}  {masked:<42} {badge} {C.DIM}{elapsed:>5.1f}s{C.RESET}")


def progress_bar(current, total, width=40):
    pct = current / total if total else 0
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    print(f"\n  {C.CYAN}[{bar}]{C.RESET} {C.BOLD}{current}/{total}{C.RESET} ({pct*100:.0f}%)", end="\r\n")


def summary_box(total, ok, fail, elapsed_total):
    ok_rate = (ok / total * 100) if total else 0
    print(f"""
  {C.BOLD}{C.CYAN}┌──────────────────────────────────────┐{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  {C.BOLD}SESSION COMPLETE{C.RESET}                     {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}├──────────────────────────────────────┤{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  Total      {C.BOLD}{total:>6}{C.RESET}    accounts          {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  {C.GREEN}Success    {C.BOLD}{ok:>6}{C.RESET}    {C.GREEN}({ok_rate:.0f}%){C.RESET}              {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  {C.RED}Failed     {C.BOLD}{fail:>6}{C.RESET}                     {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  Duration   {C.BOLD}{elapsed_total:>5.0f}s{C.RESET}                   {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}│{C.RESET}  Avg/acct   {C.BOLD}{elapsed_total/total if total else 0:>5.1f}s{C.RESET}                   {C.BOLD}{C.CYAN}│{C.RESET}
  {C.BOLD}{C.CYAN}└──────────────────────────────────────┘{C.RESET}
""")


# ── Account file I/O ────────────────────────────────────────
def load_accounts(filepath):
    if not os.path.exists(filepath):
        print(f"  {C.RED}✗  File not found: {filepath}{C.RESET}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    accounts = []
    for line in lines:
        if "|" not in line:
            continue
        parts = line.split("|", 1)
        email, pw = parts[0].strip(), parts[1].strip()
        if email and pw:
            accounts.append({"email": email, "password": pw, "raw": line})
    return accounts


def drop_account(filepath, raw_line):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(l for l in lines if l.strip() != raw_line)


# ── Browser interaction primitives ──────────────────────────
def click_first(target, locators, timeout=5):
    for loc in locators:
        try:
            el = target.ele(loc, timeout=timeout)
            if el:
                el.click()
                return True
        except Exception:
            continue
    return False


def type_into(target, locator, text, timeout=15):
    el = target.ele(locator, timeout=timeout)
    if el is None:
        raise RuntimeError(f"Element not found: {locator}")

    # Strategy 1: native input
    try:
        el.input(text, clear=True)
        time.sleep(0.4)
        v = el.attr("value") or el.property("value") or ""
        if text in v:
            return el
    except Exception:
        pass

    # Strategy 2: JS input
    try:
        el.input(text, clear=True, by_js=True)
        time.sleep(0.4)
        v = el.attr("value") or el.property("value") or ""
        if text in v:
            return el
    except Exception:
        pass

    # Strategy 3: CDP keyboard
    try:
        el.click()
        time.sleep(0.2)
        target.actions.key_down(Keys.CTRL).type("a").key_up(Keys.CTRL)
        time.sleep(0.1)
        target.actions.type(Keys.BACKSPACE)
        time.sleep(0.2)
        target.actions.input(text)
        time.sleep(0.4)
        v = el.attr("value") or el.property("value") or ""
        if text in v:
            return el
    except Exception:
        pass

    # Strategy 4: raw JS
    try:
        el.click()
        time.sleep(0.2)
        el.run_js(
            "this.focus(); this.value=arguments[0];"
            "this.dispatchEvent(new Event('input',{bubbles:true}));"
            "this.dispatchEvent(new Event('change',{bubbles:true}));",
            text,
        )
        time.sleep(0.4)
        return el
    except Exception:
        pass

    raise RuntimeError(f"All input strategies failed for: {locator}")


# ── Core: process one account ────────────────────────────────
def process_account(acct, idx, total, headless=False, tp=None):
    """
    OAuth-link a single Google account to 9Router Antigravity.
    Returns (success: bool, error_msg: str|None)
    """
    if tp is None:
        tp = PROFILES["normal"]

    email, pw = acct["email"], acct["password"]
    tmp_dir = tempfile.mkdtemp(prefix="ag_session_")

    opts = ChromiumOptions()
    opts.set_argument("--start-maximized")
    opts.set_argument("--disable-blink-features=AutomationControlled")
    opts.set_argument("--no-first-run")
    opts.set_argument("--no-default-browser-check")
    opts.set_user_data_path(tmp_dir)
    opts.set_local_port(random.randint(19200, 29200))
    if headless:
        opts.headless(True)

    browser = ChromiumPage(opts)

    try:
        # Step 1 — Navigate to provider page
        browser.get(ROUTER_URL)
        time.sleep(tp["page_load"])

        # Step 2 — Click "Add"
        if not click_first(browser, [
            "tag:button@@text():Add Connection",
            "tag:button@@text():Add",
            "tag:button@@text()=Add",
        ], timeout=1.5):
            if not browser.run_js(
                "const b=Array.from(document.querySelectorAll('button'))"
                ".find(x=>x.textContent.trim().includes('Add'));"
                "if(b){b.click();return true}return false"
            ):
                return False, "Add button not found"
        time.sleep(tp["after_add"])

        # Step 3 — Confirm modal
        pre_tabs = set(browser.tab_ids)

        if not click_first(browser, [
            "tag:button@@text():I Understand",
            "tag:button@@text():I understand",
            "tag:button@@text():Continue",
            "tag:button@@text():Confirm",
        ], timeout=1):
            browser.run_js(
                "const b=Array.from(document.querySelectorAll('button')).find(x=>"
                "x.innerText.includes('I Understand')||x.innerText.includes('Continue')"
                "||x.innerText.includes('Confirm')||x.className.includes('bg-red')"
                "||x.className.includes('danger'));"
                "if(b){b.click();return true}return false"
            )

        # Step 4 — Wait for Google tab
        new_tab_id = None
        for _ in range(3):
            time.sleep(0.5)
            diff = set(browser.tab_ids) - pre_tabs
            if diff:
                new_tab_id = diff.pop()
                break

        if not new_tab_id:
            new_tab_id = browser.wait.new_tab(timeout=tp["tab_timeout"])

        if not new_tab_id:
            for tid in browser.tab_ids:
                try:
                    t = browser.get_tab(tid)
                    if "accounts.google.com" in (t.url or ""):
                        new_tab_id = tid
                        break
                except Exception:
                    continue

        if not new_tab_id:
            return False, "Google tab did not open"

        tab = browser.get_tab(new_tab_id)
        time.sleep(tp["google_load"])

        # Step 5 — Google login
        type_into(tab, "#identifierId", email, timeout=15)
        time.sleep(tp["after_email"])

        if not click_first(tab, [
            "#identifierNext",
            "tag:button@@text():Next",
            "tag:button@@text():Berikutnya",
        ], timeout=5):
            return False, "Email Next button not found"
        time.sleep(tp["after_email_next"])

        pw_ok = False
        for loc in ["@type=password", "tag:input@@type=password", "@name=Passwd"]:
            try:
                type_into(tab, loc, pw, timeout=tp["pw_timeout"])
                pw_ok = True
                break
            except Exception:
                continue
        if not pw_ok:
            return False, "Password field not found"
        time.sleep(tp["after_pw"])

        if not click_first(tab, [
            "#passwordNext",
            "tag:button@@text():Next",
            "tag:button@@text():Berikutnya",
        ], timeout=5):
            return False, "Password Next button not found"
        time.sleep(tp["after_pw_next"])

        # Step 6 — Handle Google consent flow
        for step in range(10):
            time.sleep(tp["step_wait"])

            try:
                url = tab.url
            except Exception:
                break  # tab closed = success

            if "accounts.google.com" not in url and "google.com" not in url:
                break

            # Workspace TOS
            if "workspacetermsofservice" in url or "speedbump" in url:
                handled = click_first(tab, [
                    "tag:button@@text():I understand",
                    "tag:button@@text():I Understand",
                    "tag:button@@text():Accept",
                    "tag:input@@type=submit",
                ], timeout=tp["tos_timeout"])

                if not handled:
                    tab.run_js(
                        "window.scrollTo(0,document.body.scrollHeight);"
                        "const b=Array.from(document.querySelectorAll('button,input[type=submit]'))"
                        ".find(e=>/i understand|accept/i.test(e.innerText||e.value||''));"
                        "if(b)b.click()"
                    )
                time.sleep(tp["after_tos"])
                continue

            if any(k in url for k in ["oauthchooseaccount", "consent", "signin/oauth", "approval"]):
                pass  # fall through to button search

            # Try buttons in priority order
            for locs, label, delay_key in [
                (["tag:button@@text():Continue", "tag:button@@text():Lanjutkan"], "Continue", "after_btn"),
                (["#gaplustosNext", "tag:button@@text():I Understand", "tag:button@@text():I understand",
                  "tag:button@@text():I agree"], "Agree", "after_btn"),
                (["#submit_approve_access", "tag:button@@text():Allow",
                  "tag:button@@text():Izinkan"], "Allow", "after_allow"),
            ]:
                if click_first(tab, locs, timeout=tp["btn_timeout"]):
                    time.sleep(tp[delay_key])
                    break
            else:
                # Tick any unchecked checkboxes
                try:
                    tab.run_js("document.querySelectorAll('input[type=checkbox]:not(:checked)').forEach(c=>c.click())")
                except Exception:
                    pass

                # JS fallback: click any consent-like button
                try:
                    tab.run_js(
                        "const kw=['i understand','continue','allow','accept','i agree','confirm','next'];"
                        "const b=Array.from(document.querySelectorAll('button,a,input[type=submit]'))"
                        ".find(e=>kw.some(k=>(e.innerText||e.value||'').toLowerCase().includes(k)));"
                        "if(b)b.click()"
                    )
                except Exception:
                    pass

                time.sleep(tp["no_btn_wait"])
                continue

        # Step 7 — Verify completion
        time.sleep(tp["redirect_wait"])
        try:
            if new_tab_id in browser.tab_ids:
                try:
                    if "accounts.google.com" in tab.url:
                        return False, "Stuck on Google page"
                except Exception:
                    pass
        except Exception:
            pass

        return True, None

    except Exception as e:
        return False, str(e)[:120]

    finally:
        try:
            browser.quit()
        except Exception:
            pass
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass


# ── Entrypoint ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="9Router × Antigravity — Batch OAuth Connector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--headless", action="store_true", help="Run browser in background")
    parser.add_argument("--fast", action="store_true", help="Fast mode (low-latency connection)")
    parser.add_argument("--delay", type=int, default=DEFAULT_DELAY, help=f"Delay between accounts (default: {DEFAULT_DELAY}s)")
    parser.add_argument("--file", type=str, default=None, help="Path to accounts file (default: accounts.txt)")
    args = parser.parse_args()

    acct_file = args.file or DEFAULT_ACCOUNTS_FILE
    tp = PROFILES["fast" if args.fast else "normal"]

    banner()

    # Clean up zombie processes from previous runs
    if sys.platform != "win32":
        os.system("pkill -f 'chromium.*ag_session_' 2>/dev/null")
        os.system("pkill -f 'chrome.*ag_session_' 2>/dev/null")
    import glob
    for d in glob.glob(os.path.join(tempfile.gettempdir(), "ag_session_*")):
        shutil.rmtree(d, ignore_errors=True)

    accounts = load_accounts(acct_file)
    if not accounts:
        print(f"  {C.YELLOW}⚠  No accounts to process.{C.RESET}")
        print(f"  {C.DIM}   Create {acct_file} with format: email|password{C.RESET}\n")
        sys.exit(1)

    mode = "FAST" if args.fast else "NORMAL"
    print(f"  {C.BOLD}Accounts  {C.CYAN}{len(accounts)}{C.RESET}")
    print(f"  {C.BOLD}Mode      {C.CYAN}{mode}{C.RESET}")
    print(f"  {C.BOLD}Headless  {C.CYAN}{'Yes' if args.headless else 'No'}{C.RESET}")
    print(f"  {C.BOLD}Delay     {C.CYAN}{args.delay}s{C.RESET}")
    print(f"  {C.BOLD}File      {C.CYAN}{acct_file}{C.RESET}")

    table_header()

    ok_count = 0
    fail_count = 0
    t_start = time.time()
    errors_log = []

    for i, acct in enumerate(accounts):
        t0 = time.time()
        success, err = process_account(acct, i, len(accounts), headless=args.headless, tp=tp)
        elapsed = time.time() - t0

        if success:
            ok_count += 1
            drop_account(acct_file, acct["raw"])
            table_row(i + 1, len(accounts), acct["email"], "OK", elapsed)
        else:
            fail_count += 1
            errors_log.append((acct["email"], err))
            table_row(i + 1, len(accounts), acct["email"], "FAIL", elapsed)

        progress_bar(i + 1, len(accounts))

        if i < len(accounts) - 1:
            time.sleep(args.delay)

    total_time = time.time() - t_start
    summary_box(len(accounts), ok_count, fail_count, total_time)

    if errors_log:
        print(f"  {C.RED}{C.BOLD}Failed accounts:{C.RESET}")
        print(f"  {C.DIM}{'─'*55}{C.RESET}")
        for email, err in errors_log:
            print(f"  {C.RED}✗{C.RESET}  {email}")
            print(f"     {C.DIM}{err}{C.RESET}")
        print()


if __name__ == "__main__":
    main()
