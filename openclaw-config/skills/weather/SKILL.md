---
name: weather
description: "Get current weather and forecasts via Open-Meteo (primary). Use when: user asks about weather, temperature, or forecasts for any location. NOT for: historical weather data, severe weather alerts, or detailed meteorological analysis. No API key needed."
homepage: https://open-meteo.com/en/docs
metadata: { "openclaw": { "emoji": "🌤️", "requires": { "bins": ["curl"] } } }
---

# Weather Skill

Get current weather conditions and forecasts.

## When to Use

✅ **USE this skill when:**

- "What's the weather?"
- "Will it rain today/tomorrow?"
- "Temperature in [city]"
- "Weather forecast for the week"
- Travel planning weather checks

## When NOT to Use

❌ **DON'T use this skill when:**

- Historical weather data → use weather archives/APIs
- Climate analysis or trends → use specialized data sources
- Hyper-local microclimate data → use local sensors
- Severe weather alerts → check official NWS sources
- Aviation/marine weather → use specialized services (METAR, etc.)

## Location

Always include a city name in weather queries. Open-Meteo requires latitude/longitude — use the Geocoding API first to resolve a city name to coordinates.

## Primary: Open-Meteo (No API key required)

### Step 1 — Resolve city to coordinates

```bash
# Geocoding: get latitude & longitude for a city
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=London&count=1&language=en"
# Returns JSON with results[0].latitude and results[0].longitude
```

### Step 2 — Query current weather

```bash
# Current conditions (temperature, wind, humidity, precipitation, weather code)
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m&wind_speed_unit=kmh&timezone=auto"
```

### Step 3 — Query forecasts

```bash
# 7-day daily forecast (high/low temp, precipitation, UV index, wind)
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,uv_index_max,weather_code&timezone=auto"

# Hourly forecast for today (next 24 hours)
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code&forecast_days=1&timezone=auto"
```

### One-liner (geocode + weather combined via shell)

```bash
# Get coords for Beijing, then fetch current weather
COORDS=$(curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Beijing&count=1" | \
  grep -o '"latitude":[^,]*,"longitude":[^,]*' | head -1)
LAT=$(echo "$COORDS" | grep -o '"latitude":[^,]*' | cut -d: -f2)
LON=$(echo "$COORDS" | grep -o '"longitude":[^,]*' | cut -d: -f2)
curl -s "https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto"
```

### Key Weather Code Reference (WMO)

| Code   | Condition                               |
| ------ | --------------------------------------- |
| 0      | Clear sky                               |
| 1–3    | Mainly clear / partly cloudy / overcast |
| 45, 48 | Fog                                     |
| 51–67  | Drizzle / Rain                          |
| 71–77  | Snow                                    |
| 80–82  | Rain showers                            |
| 85–86  | Snow showers                            |
| 95     | Thunderstorm                            |
| 96, 99 | Thunderstorm with hail                  |

## Fallback Sources (if Open-Meteo is unreachable)

Try the following free services in order:

### Fallback 1 — wttr.in (text-based, no API key)

```bash
# One-line summary
curl -s "wttr.in/London?format=3"

# Full current conditions + 3-day forecast
curl -s "wttr.in/London?0"

# Detailed format: condition, temp, feels-like, wind, humidity
curl -s "wttr.in/London?format=%l:+%c+%t+(feels+like+%f),+%w+wind,+%h+humidity"

# JSON output
curl -s "wttr.in/London?format=j1"
```

### Fallback 2 — 7timer.info (JSON, no API key)

```bash
# Current + 7-day forecast (requires lat/lon — reuse coords from geocoding above)
curl -s "http://www.7timer.info/bin/api.pl?lon=-0.13&lat=51.51&product=civillight&output=json"

# Detailed hourly (civil conditions)
curl -s "http://www.7timer.info/bin/api.pl?lon=-0.13&lat=51.51&product=civil&output=json"
```

### Fallback 3 — Open-Meteo mirror (self-hosted community instance)

```bash
# Same API, alternate host
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&current=temperature_2m,weather_code&timezone=auto"
# If the above fails, try the official GitHub self-hosted endpoint documented at:
# https://github.com/open-meteo/open-meteo
```

## Quick Responses

**"What's the weather in Tokyo?"**

```bash
# 1. Get coordinates
curl -s "https://geocoding-api.open-meteo.com/v1/search?name=Tokyo&count=1&language=en"
# 2. Use lat=35.6895 lon=139.6917
curl -s "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&timezone=auto"
```

**"Will it rain today?"**

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&hourly=precipitation_probability,precipitation&forecast_days=1&timezone=auto"
```

**"Weekend forecast"**

```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code&forecast_days=7&timezone=auto"
```

## Notes

- No API key needed for Open-Meteo (non-commercial use)
- Open-Meteo integrates ECMWF, NOAA GFS, DWD ICON and other top global models
- Supports up to 16-day forecasts
- wttr.in supports airport codes: `curl wttr.in/ORD`
- 7timer.info requires lat/lon (reuse coords from Geocoding API)
- Rate limit: avoid hammering any single service; space out requests
