############################################################################################################
## Purpose: This script is used to scrape team data from the LeagueOS website.
## Created By: Tinsley Devers
## https://github.com/TinsleyDevers
## Created On: 2024-11-15 (YYYY-MM-DD)
## Last Updated: 2024-11-15 (YYYY-MM-DD)
############################################################################################################

# this script is not perfect and may not work in all cases. sometimes maps are not available.
# !! PLEASE - ON START: FULLSCREEN THE CHROME WINDOW TO AVOID ANY ISSUES WITH THE SCRIPT !!
# opens the match page, manually select your team, and let the script scrape the data.
# example match link: https://njcaae.leagueos.gg/league/matches/xxxxx

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter, defaultdict
import re
import platform

match_link = input("Please enter the match link: ")

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

try:
    driver.get(match_link)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'div.my-1.fw700.kanit.emH5')
    ))

    # team name elements
    team_name_elements = driver.find_elements(By.CSS_SELECTOR, 'div.my-1.fw700.kanit.emH5')

    teams = []
    for team_name_element in team_name_elements:
        team_name = team_name_element.text.strip()
        # parent div
        parent_div = team_name_element.find_element(By.XPATH, '..')
        # clickable element
        clickable_element = parent_div.find_element(By.CSS_SELECTOR, 'div.pointer[style*="padding: 2px; border-radius: 50%;"]')
        teams.append({'name': team_name, 'element': clickable_element})

    if len(teams) < 2:
        print("Could not find both teams.")
        driver.quit()
        exit()

    # select team
    print("Please select your team:")
    for idx, team in enumerate(teams):
        print(f"{idx + 1}. {team['name']}")
    while True:
        try:
            selection = int(input("Enter the number corresponding to your team: "))
            if 1 <= selection <= len(teams):
                your_team = teams[selection - 1]['name']
                your_team_element = teams[selection - 1]['element']
                break
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(teams)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # click on team;s page
    your_team_element.click()

    # wait for calandar
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'a.v-tab[href$="/calendar"]')
    ))

    # click on calendar
    calendar_tab = driver.find_element(By.CSS_SELECTOR, 'a.v-tab[href$="/calendar"]')
    calendar_tab.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'div.bRad5.ofh.bgDark.pt-2.pointer.mb-4')
    ))

    maps_played = []
    map_results = []
    processed_games = set()
    match_results = []
    rounds_data = defaultdict(lambda: {'your_rounds': 0, 'opponent_rounds': 0})

    if platform.system() == 'Darwin':
        key_modifier = Keys.COMMAND
    else:
        key_modifier = Keys.CONTROL

    while True:
        game_elements = driver.find_elements(By.CSS_SELECTOR, 'div.bRad5.ofh.bgDark.pt-2.pointer.mb-4')
        print(f"\nFound {len(game_elements)} games on this page.")

        if not game_elements:
            print("No more games found on this page.")
            break

        for game_index, game_element in enumerate(game_elements):
            try:
                driver.execute_script("arguments[0].scrollIntoView();", game_element)

                actions = ActionChains(driver)
                actions.key_down(key_modifier).click(game_element).key_up(key_modifier).perform()

                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.v-tabs')
                ))

                current_url = driver.current_url
                if current_url in processed_games:
                    print(f"Already processed game at {current_url}, skipping.")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                else:
                    processed_games.add(current_url)

                print(f"\nProcessing Match {game_index + 1}: {current_url}")

                short_wait = WebDriverWait(driver, 1)

                match_win = False
                maps_in_match = 0
                maps_won_in_match = 0

                for i in range(1, 4):
                    try:
                        game_tab = short_wait.until(EC.element_to_be_clickable(
                            (By.XPATH, f"//div[@role='tab' and contains(., 'Game {i}')]")
                        ))
                        game_tab.click()

                        map_element = short_wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'opac80') and contains(text(), 'Standard:')]")
                        ))

                        map_text = map_element.text.strip()
                        # map name
                        map_match = re.search(r'Standard:\s*(.*)', map_text)
                        if map_match:
                            map_name = map_match.group(1).strip()
                        else:
                            map_name = 'N/A'

                        score_element = short_wait.until(EC.presence_of_element_located(
                            (By.XPATH, "//div[contains(@class, 'mx-4') and contains(@class, 'emH2')]")
                        ))
                        score_text = score_element.text.strip()

                        # team names on page
                        team_name_elements = driver.find_elements(By.CSS_SELECTOR, 'div.my-1.fw700.kanit.emH5')
                        team_names_in_game = [elem.text.strip() for elem in team_name_elements]

                        if len(team_names_in_game) >= 2:
                            left_team = team_names_in_game[0]
                            right_team = team_names_in_game[1]

                            scores = score_text.split('-')
                            if len(scores) == 2:
                                left_score = int(scores[0].strip())
                                right_score = int(scores[1].strip())

                                # calculate which side is selected team
                                if your_team.lower() in left_team.lower():
                                    your_score = left_score
                                    opponent_score = right_score
                                    your_side = 'left'
                                elif your_team.lower() in right_team.lower():
                                    your_score = right_score
                                    opponent_score = left_score
                                    your_side = 'right'
                                else:
                                    print("Your team not found in this game.")
                                    your_score = None
                                    opponent_score = None
                                    your_side = None

                                if your_score is not None:
                                    if your_score > opponent_score:
                                        result = 'Win'
                                        maps_won_in_match += 1
                                    else:
                                        result = 'Loss'
                                    maps_in_match += 1
                                    maps_played.append(map_name)
                                    map_results.append((map_name, result))

                                    # round scores
                                    rounds_data[map_name]['your_rounds'] += your_score
                                    rounds_data[map_name]['opponent_rounds'] += opponent_score

                                    # end - output
                                    print(f"Game {i} map: {map_name}")
                                    print(f"Score: {left_team} {left_score} - {right_score} {right_team}")
                                    print(f"Result: {your_team} {result} the map")
                                else:
                                    print("Could not determine your team's score.")
                                    maps_played.append(map_name)
                                    map_results.append((map_name, 'Unknown'))
                            else:
                                print("Invalid score format.")
                                maps_played.append(map_name)
                                map_results.append((map_name, 'Unknown'))
                        else:
                            print("Could not find team names in game.")
                            maps_played.append(map_name)
                            map_results.append((map_name, 'Unknown'))

                    except Exception as e:
                        print(f"Could not find map or score for Game {i} within 1 second.")
                        maps_played.append('N/A')
                        map_results.append(('N/A', 'Unknown'))
                        continue

                # match results based on maps won
                if maps_in_match > 0:
                    if maps_won_in_match > maps_in_match / 2:
                        match_results.append('Win')
                    else:
                        match_results.append('Loss')

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Error processing game {game_index + 1}: {e}")
                continue

        try:
            last_7_days_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Last 7 Days')]"))
            )
            if 'disabled' in last_7_days_button.get_attribute('class'):
                print("The 'Last 7 Days' button is disabled. No more previous games to load.")
                break
            else:
                print("Clicking on 'Last 7 Days' button to load previous games.")
                last_7_days_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.bRad5.ofh.bgDark.pt-2.pointer.mb-4')
                    )
                )
        except Exception:
            print("No 'Last 7 Days' button found or it is not clickable. Exiting loop.")
            break

    valid_maps = [item[0] for item in map_results if item[0] != 'N/A' and item[1] != 'Unknown']
    total_maps_played = len(valid_maps)
    map_counts = Counter(valid_maps)

    total_games_processed = len(processed_games)
    total_matches_won = match_results.count('Win')
    match_win_rate = (total_matches_won / total_games_processed) * 100 if total_games_processed > 0 else 0

    total_rounds_won = sum(data['your_rounds'] for data in rounds_data.values())
    total_rounds_lost = sum(data['opponent_rounds'] for data in rounds_data.values())
    total_rounds_played = total_rounds_won + total_rounds_lost

    print("\n--- Statistics ---")
    print(f"Your team: {your_team}")
    print(f"Total matches processed: {total_games_processed}")
    print(f"Matches won: {total_matches_won}")
    print(f"Match win rate: {match_win_rate:.2f}%")
    print(f"Total valid maps found: {total_maps_played}")
    print(f"Total 'N/A' entries (maps not available): {maps_played.count('N/A')}")
    print(f"Total rounds won: {total_rounds_won}")
    print(f"Total rounds lost: {total_rounds_lost}")
    print(f"Overall round win rate: {(total_rounds_won / total_rounds_played) * 100:.2f}%\n")

    if total_maps_played > 0:
        map_wins = {}
        for map_name, result in map_results:
            if map_name != 'N/A' and result != 'Unknown':
                if map_name not in map_wins:
                    map_wins[map_name] = {'Win': 0, 'Loss': 0}
                map_wins[map_name][result] += 1

        print(f"{'Map':<15}{'Wins':<10}{'Losses':<10}{'Win %':<10}{'Rnd Win %':<10}")
        print('-' * 60)
        for map_name, results in map_wins.items():
            wins = results.get('Win', 0)
            losses = results.get('Loss', 0)
            total = wins + losses
            win_percent = (wins / total) * 100 if total > 0 else 0

            rounds_won = rounds_data[map_name]['your_rounds']
            rounds_lost = rounds_data[map_name]['opponent_rounds']
            rounds_played = rounds_won + rounds_lost
            round_win_percent = (rounds_won / rounds_played) * 100 if rounds_played > 0 else 0

            print(f"{map_name:<15}{wins:<10}{losses:<10}{win_percent:<10.2f}{round_win_percent:<10.2f}")
    else:
        print("No valid maps found.")

    na_count = maps_played.count('N/A')
    if na_count > 0:
        print(f"\nMaps not available for {na_count} game(s).")

    # extra info
    print("\n--- Additional Statistics ---")
    # most played maps
    most_played_maps = map_counts.most_common()
    print("Most Played Maps:")
    for map_name, count in most_played_maps:
        print(f"{map_name}: {count} times")

    # best maps
    print("\nBest Performing Maps (by Win %):")
    sorted_maps = sorted(map_wins.items(), key=lambda x: (x[1]['Win'] / (x[1]['Win'] + x[1]['Loss'])), reverse=True)
    for map_name, results in sorted_maps:
        wins = results['Win']
        losses = results['Loss']
        total = wins + losses
        win_percent = (wins / total) * 100 if total > 0 else 0
        print(f"{map_name}: {win_percent:.2f}% win rate")

finally:
    driver.quit()