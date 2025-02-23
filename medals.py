import urllib.request
import json
from bs4 import BeautifulSoup

def fetch_html(url):
    """
    Fetch the HTML content of a given URL.
    """
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
        
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def load_competitors(filename="competitors.json"):
    """
    Load competitors from a JSON file.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
        
    except FileNotFoundError:
        print("No competitor data found. Run competitors.py first.")
        return {}

def search_competitor(first_name, last_name, competitors):
    """
    Search for a competitor by first and last name and return their ID.
    """
    for name, details in competitors.items():
        if details["first_name"].lower() == first_name.lower() and details["last_name"].lower() == last_name.lower():
            return details["id"]
        
    return None

def fetch_achievements(user_id):
    """
    Fetch achievements from the competitor's profile page.
    """
    url = f"https://sonkal.cz/osobni_karta/{user_id}"
    html = fetch_html(url)
    if not html:
        print(f"Could not retrieve achievements for ID {user_id}.")
        return None

    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find("div", id="div_hlavni")
    if not main_div:
        print(f"Main content not found for ID {user_id}.")
        return None

    achievements_div = main_div.find("div", class_="col d_sirsi_sloupec")
    if not achievements_div:
        print(f"Achievements section not found for ID {user_id}.")
        return None

    achievements = {
        "total_medals": 0,
        "gold": 0,
        "silver": 0,
        "bronze": 0,
        "mvp": 0
    }

    for table in achievements_div.find_all("table", class_="t_space"):
        for tr in table.find_all("tr"):
            for td in tr.find_all("td", class_="td_uspechy_umisteni"):
                img = td.find("img")
                if img and "src" in img.attrs:
                    src = img["src"]
                    if "design/1_place.png" in src:
                        achievements["gold"] += 1
                    elif "design/2_place.png" in src:
                        achievements["silver"] += 1
                    elif "design/3_place.png" in src:
                        achievements["bronze"] += 1
                    elif "design/pohar.png" in src:  
                        achievements["mvp"] += 1

    achievements["total_medals"] = achievements["gold"] + achievements["silver"] + achievements["bronze"]
    
    return achievements

def main():
    competitors = load_competitors()
    if not competitors:
        return
    
    first_name = input("Enter competitor first name: ")
    last_name = input("Enter competitor last name: ")
    user_id = search_competitor(first_name, last_name, competitors)
    
    if user_id:
        print(f"Competitor ID for {first_name} {last_name}: {user_id}")

        achievements = fetch_achievements(user_id)
        if achievements:
            print("\n--- Achievements ---")
            print(f"Total Medals: {achievements['total_medals']}")
            print(f"Gold Medals: {achievements['gold']}")
            print(f"Silver Medals: {achievements['silver']}")
            print(f"Bronze Medals: {achievements['bronze']}")
            print(f"MVP Awards: {achievements['mvp']}")

    else:
        print("Competitor not found.")

if __name__ == "__main__":
    main()