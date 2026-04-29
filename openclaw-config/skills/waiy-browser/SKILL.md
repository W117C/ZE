---
name: waiy-browser
description: Automates browser interactions using waiy-browser CLI for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, or extract information from web pages.
allowed-tools: Bash(waiy-browser:*)
---

# Browser Automation with waiy-browser CLI

The `waiy-browser` command provides fast, persistent browser automation through a daemon-based architecture. The daemon stays active across commands, enabling complex multi-step workflows.

**Default Behavior**: Browser UI is visible by default (great for development and debugging). Use `--headless` for background automation.

## Prerequisites

Before using this skill, `waiy-browser` must be installed and configured.

Verify installation:
```bash
waiy-browser --help
```

### CDP MCP Server (Required Dependency)

This skill requires `cdp-mcp-server` to be installed on the system. Verify it exists before using this skill:

```bash
npx cdp-mcp-server --help
```

If the command outputs help information, the skill is ready to use. If not, this skill cannot be used.

## Core Workflow

1. **Navigate**: `waiy-browser go_to_url <url>` - Opens URL (starts daemon if needed)
2. **Inspect**: `waiy-browser snapshot` - Returns clickable elements with indices
3. **Interact**: Use indices from snapshot to interact (`waiy-browser click_element_by_index 5`, `waiy-browser input_text 3 "text"`)
4. **Verify**: `waiy-browser snapshot` or `waiy-browser take_screenshot` to confirm actions
5. **Repeat**: Browser daemon stays active between commands

## Global Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--headless` | Run browser in headless mode (no UI) |
| `--cdp-url URL` | Connect to existing browser via CDP URL |
| `--proxy URL` | Proxy server URL (e.g. `http://host:port` or `http://user:pass@host:port`) |
| `--fingerprint-os OS` | Browser fingerprint OS (e.g. `windows`, `macos`, `linux`; comma-separated for multiple) |
| `--fingerprint-device DEVICE` | Browser fingerprint device (e.g. `desktop`, `mobile`; comma-separated for multiple) |
| `--fingerprint-locale LOCALE` | Browser fingerprint locale (e.g. `en-US`, `zh-CN`; comma-separated for multiple) |

**Note**: By default, the browser shows UI. Use `--headless` to run without UI.

## Essential Commands

```bash
# Navigation
waiy-browser go_to_url <url>                    # Navigate to URL
waiy-browser go_to_url <url> --new-tab          # Open in new tab
waiy-browser go_back                             # Go back in history
waiy-browser get_current_url                    # Get current page URL

# Page State (always run snapshot first to get element indices)
waiy-browser snapshot                            # Get DOM snapshot with indexed elements
waiy-browser take_screenshot                     # Take screenshot (default: screenshot.png)
waiy-browser take_screenshot result.png          # Save screenshot to file
waiy-browser take_screenshot result.png --full-page  # Full page screenshot
waiy-browser save_page_as_pdf report.pdf        # Save current page as PDF

# Interactions (use indices from snapshot)
waiy-browser click_element_by_index <index>     # Click element
waiy-browser click_element_by_index 3 --button right  # Right-click element
waiy-browser click_element_by_index 3 --ctrl    # Ctrl+click element
waiy-browser hover_element_by_index <index>     # Hover over element
waiy-browser input_text <index> "text"          # Click element, then type
waiy-browser input_text 7 "text" --no-clear     # Don't clear existing text
waiy-browser input_text 7 "text" --keep-focus   # Keep focus after typing
waiy-browser send_keys "Enter"                  # Send keyboard keys
waiy-browser send_keys "Control+a"              # Send key combination

# Dropdowns & Sliders
waiy-browser set_slider_value <index> 75.0      # Set slider value

# Scrolling
waiy-browser scroll down                         # Scroll down (default: 3 pages)
waiy-browser scroll up 2                        # Scroll up 2 pages
waiy-browser scroll down 2 --frame 5            # Scroll inside element 5
waiy-browser scroll_to_text "text"              # Scroll until text is visible

# File Operations
waiy-browser upload_file_to_element <index> /path/file.pdf  # Upload file
waiy-browser write_file output.md "content"     # Write to file
waiy-browser write_file output.md "content" --append  # Append to file
waiy-browser read_file output.md                # Read file content
waiy-browser replace_file_str file.md "old" "new"  # Replace text in file

# Tabs
waiy-browser list_tabs                           # List all open tabs
waiy-browser switch_tab AB12                     # Switch to tab by ID
waiy-browser close_tab AB12                      # Close tab by ID

# Data Extraction & Search
waiy-browser search_bing "query"                # Search Bing

# Utilities
waiy-browser wait 5                              # Wait 5 seconds (max 10)
waiy-browser drag_element 3 5                   # Drag element 3 to element 5

# Captcha Solving
waiy-browser solve_captcha                       # Solve image captcha (default)
waiy-browser solve_captcha --type recaptchav2    # Solve reCAPTCHA v2
waiy-browser solve_captcha --type cloudflare     # Solve Cloudflare Turnstile
waiy-browser solve_captcha --timeout 120         # Custom timeout (default: 60s)

# Get Information
waiy-browser get cdp-url                         # Get the CDP WebSocket URL

# Close Browser
waiy-browser close                               # Close browser, keep daemon for faster restart
waiy-browser close -f                            # Fully stop browser and daemon
```

Use indices from `waiy-browser snapshot`.

## Common Workflows

### Web Automation Flow
```bash
# 1. Navigate and inspect (browser UI visible by default)
waiy-browser go_to_url "https://www.baidu.com"
waiy-browser snapshot

# 2. Interact with elements (use indices from snapshot)
waiy-browser input_text 1 "Python tutorial"
waiy-browser click_element_by_index 2

# 3. Wait and verify
waiy-browser wait 3
waiy-browser take_screenshot search_result.png

# 4. Clean up
waiy-browser close
```

### Form Filling
```bash
# Navigate to form
waiy-browser go_to_url "https://example.com/form"
waiy-browser snapshot

# Fill form fields (use actual indices from snapshot)
waiy-browser input_text 3 "John Doe"
waiy-browser input_text 4 "john@example.com"
waiy-browser set_slider_value 5 50.0
waiy-browser upload_file_to_element 6 "/path/to/resume.pdf"

# Submit and verify
waiy-browser click_element_by_index 7
waiy-browser wait 2
waiy-browser take_screenshot form_submitted.png
```

### Multi-Tab Operations
```bash
# Open multiple tabs
waiy-browser go_to_url "https://github.com" --new-tab
waiy-browser list_tabs

# Switch between tabs
waiy-browser switch_tab AB12
waiy-browser close_tab CD34
```

### Proxy Usage
```bash
# HTTP proxy
waiy-browser --proxy "http://proxy.example.com:8080" go_to_url "https://example.com"

# HTTP proxy with authentication
waiy-browser --proxy "http://username:password@proxy.example.com:8080" go_to_url "https://example.com"

# SOCKS5 proxy
waiy-browser --proxy "socks5://proxy.example.com:1080" go_to_url "https://example.com"
```

**Note**: The `--proxy` option must be specified on the first command that starts the daemon. Once the browser is started with a proxy, all subsequent commands will use it.

### Browser Fingerprint
```bash
# Simulate Windows desktop with English locale
waiy-browser --fingerprint-os windows --fingerprint-device desktop --fingerprint-locale en-US go_to_url "https://example.com"

# Simulate macOS with Chinese locale
waiy-browser --fingerprint-os macos --fingerprint-locale zh-CN go_to_url "https://example.com"

# Combine proxy + fingerprint for full anonymity
waiy-browser --proxy "http://user:pass@host:8080" --fingerprint-os windows --fingerprint-device desktop --fingerprint-locale en-US go_to_url "https://example.com"
```

**Note**: Fingerprint options are set once when starting the daemon. All options (`--proxy`, `--fingerprint-*`) take effect only on the first command that starts the browser.

### Headless vs UI Mode
```bash
# use UI (default)
waiy-browser go_to_url "https://example.com"
waiy-browser snapshot                     # See elements interactively
waiy-browser click_element_by_index 3

# use headless
waiy-browser --headless go_to_url "https://example.com"
waiy-browser snapshot                     # Get elements programmatically
waiy-browser click_element_by_index 3
waiy-browser take_screenshot result.png   # Capture result
```

## Tips

1. **Always run `waiy-browser snapshot` first** to see available elements and their indices
2. **Browser UI is visible by default** — great for debugging and development
3. **Use `--headless` for automation** when you don't need to see the browser
4. **Daemon persists** — the daemon stays active between commands
5. **Use `--json`** for programmatic parsing
6. **Element indices from snapshot** are required for most interaction commands
7. **Captcha handling** — when encountering any captcha (slider puzzle, image recognition, reCAPTCHA, Cloudflare Turnstile, etc.), **always use `waiy-browser solve_captcha` first** instead of manual interaction. Determine the captcha type: use `--type recaptchav2` for reCAPTCHA v2, `--type cloudflare` for Cloudflare Turnstile, and `--type image` for all other types (slider puzzles, image captchas, etc.). **If you cannot determine the captcha type, default to `--type image`**. The default timeout is 60 seconds, which is usually sufficient. If the first attempt fails, **retry 2-3 times** as captcha solving has inherent variability and retrying significantly improves the overall success rate.

## Captcha Detection Rules

**Run `waiy-browser solve_captcha --type image` immediately when snapshot shows any of these patterns:**

| Pattern in snapshot | Description | Action |
|---------------------|-------------|--------|
| `iframe name=*captcha*` | Captcha iframe (e.g., `t.captcha.qq.com`) | ✅ Solve immediately |
| `text=拖动下方滑块` or `text=拖动下方拼图` | Slider puzzle captcha | ✅ Solve immediately |
| `text=安全验证` | Security verification dialog | ✅ Solve immediately |
| `role=dialog aria-label=验证码` | Captcha dialog | ✅ Solve immediately |
| `text=刷新验证码` or `text=刷新验证` | Refresh captcha button visible | ✅ Solve immediately |
| `alt=close` + captcha context | Close button in captcha modal | ✅ Solve immediately |

**Decision Flow:**

```
snapshot → Check for captcha patterns → Found? → solve_captcha --type image --timeout 120
                                            ↓
                                      Not found? → Continue normal workflow
```

**Important:**

- **Do NOT attempt to bypass** captcha by navigating to different URLs
- **Do NOT try manual interaction** (clicking slider, etc.) before solve_captcha
- **Do NOT assume captcha is non-blocking** just because snapshot returns elements
- **Always solve first**, then verify with another snapshot

**Retry Strategy:**

```bash
# Check captcha occured after snapshot
waiy-browser snapshot

# First attempt
waiy-browser solve_captcha --type image --timeout 60

# If fails, retry 2-3 times (captcha solving has variability)
waiy-browser solve_captcha --type image --timeout 60
waiy-browser solve_captcha --type image --timeout 60

# After success, verify with snapshot
waiy-browser snapshot
```

## Troubleshooting

**Daemon won't start?**
```bash
waiy-browser close -f                     # Fully stop daemon
waiy-browser go_to_url <url>              # Try with visible window (default)
```

**Element not found?**
```bash
waiy-browser snapshot                     # Check current elements
waiy-browser scroll down                  # Element might be below fold
waiy-browser snapshot                     # Check again
```

**Connection issues?**
```bash
# Connect to existing browser instance
waiy-browser --cdp-url "ws://localhost:9222/devtools/browser" go_to_url "https://example.com"
```


## Cleanup

**Always close the browser when done:**

```bash
waiy-browser close                        # Recommended: keep daemon for faster restart
waiy-browser close -f                     # Fully stop browser and daemon
```

## Architecture

```
CLI command → Unix socket (length-prefixed JSON) → Daemon (Tools + Browser) → Browser
```

The daemon creates a Tools instance which registers all actions. CLI commands are dispatched via Tools.registry.execute_action(), calling the exact same code paths as the waiy-browser-use agent.