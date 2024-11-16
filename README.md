# Valorant-LeagueOS-Scraper

**Purpose:** Scraps Valorant team data from LeagueOS to get important match statistics.

---

## Table of Contents

- [Description](#description)
- [Requirements](#requirements)
- [Example](#example)
- [Output](#output)

---

## Description

This Python script uses Selenium WebDriver to automate the process of scraping team match data from the LeagueOS website. It navigates through the team's match history, extracts match statistics, and provides detailed analytics including win rates, most played maps, and best performing maps.

**Note:** This script is not perfect and may not work in all cases. Sometimes maps are not available.

---

## Requirements

- **Python 3.x**
- **Python Packages:**
  - `selenium`
- **WebDriver:**
  - **Chrome WebDriver** matching your installed version of **Google Chrome**
- **Google Chrome Browser**

---

## Example

**Sample Output:**
```bash
Please enter the match link: https://njcaae.leagueos.gg/league/matches/12345
Please select your team:
1. Knights Esports
2. Dragons Esports
Enter the number corresponding to your team: 1

Found 3 games on this page.

Processing Match 1: https://njcaae.leagueos.gg/league/matches/12345/game/1

Game 1 map: Ascent
Score: Knights Esports 13 - 7 Dragons Esports
Result: Knights Esports Win the map

...

--- Statistics ---
Your team: Knights Esports
Total matches processed: 3
Matches won: 2
Match win rate: 66.67%
Total valid maps found: 6
Total 'N/A' entries (maps not available): 0
Total rounds won: 78
Total rounds lost: 54
Overall round win rate: 59.09%

Map             Wins      Losses    Win %     Rnd Win %
------------------------------------------------------------
Ascent          2         0         100.00    65.00
Bind            0         1         0.00      40.00
...

--- Additional Statistics ---
Most Played Maps:
Ascent: 2 times
Bind: 1 times
...

Best Performing Maps (by Win %):
Ascent: 100.00% win rate
Bind: 0.00% win rate
...
```

---

## Output

The script provides detailed statistics including:

- **Total matches processed**
- **Matches won**
- **Match win rate**
- **Total valid maps found**
- **Total 'N/A' entries (maps not available)**
- **Total rounds won**
- **Total rounds lost**
- **Overall round win rate**
- **Per-map statistics:**
  - Number of wins and losses
  - Win percentage
  - Round win percentage
- **Additional Statistics:**
  - Most played maps
  - Best performing maps by win percentage
