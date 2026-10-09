from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re


'''
returns a dict of {format: {deck name: {card name: (num_cards, percentage)}}}
'''
def scrape_goldfish(formats: list[str]) -> dict[str, dict[str, dict[str, tuple[float, float]]]]:
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    decklists = {f: {} for f in formats}

    card_info_re = re.compile(r'(\d\.\d) in (\d{1,3})% of decks')


    for f in formats:
        driver.get(f"https://www.mtggoldfish.com/metagame/{f}")
        deck_name_re = re.compile(fr'.*/({f}-)?([^#]*)(#.*)?')
        decklist_containers = driver.find_elements(By.CLASS_NAME, "archetype-tile")
        deck_links = []
        for decklist_container in decklist_containers:
            try:
                curr_link = decklist_container.find_element(By.CSS_SELECTOR, "a[href^='/archetype/']")
                deck_links.append(curr_link.get_attribute("href"))
            except NoSuchElementException: # Budget Decks have deck tag instead of archetype in name, don't want these
                continue
        for deck_link in deck_links:
            driver.get(deck_link)
            deck_name = deck_name_re.search(deck_link).group(2)

            deck_name = deck_name.replace("-", " ")
            decklists[f][deck_name] = {}
            deck_cards_container = driver.find_element(By.CLASS_NAME, "deck-display-left-contents")
            card_containers = deck_cards_container.find_elements(By.CLASS_NAME, "spoiler-card")
            for card_container in card_containers:
                card_name_element = card_container.find_element(By.CLASS_NAME, "price-card-invisible-label")
                card_name = card_name_element.get_attribute('innerHTML')
                card_info = card_container.find_element(By.CLASS_NAME, "archetype-breakdown-featured-card-text").text
                re_info = re.search(card_info_re, card_info)
                count = re_info.group(1)
                chance = re_info.group(2)
                decklists[f][deck_name][card_name] = (float(count), float(chance)/100.)

    return decklists

def main():
    deck_info = scrape_goldfish(["legacy"])
    for f, ds in deck_info.items():
        print("======================")
        print(f)
        for d, cards in ds.items():
            print(d, cards)
            print("---------------")


if __name__ == "__main__":
    main()