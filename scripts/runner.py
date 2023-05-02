import requests
import json
from bs4 import BeautifulSoup
import hashlib

url = "https://alfred.app/workflows/"

def get_workflows(url):
    workflows = []
    page = 0
    while True:
        print(f"Fetching page {page+1}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the URL: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        workflowlist_section = soup.find("nav", {"id": "workflowlist"})

        if workflowlist_section is None:
            break

        for a_tag in workflowlist_section.find_all("a", href=True):
            div = a_tag.find("div")
            if div is None:
                continue

            icon = div.find_all("img")
            h2 = div.find("h2")
            p = div.find("p")

            if len(icon) == 2:
                icon = icon[1]
            else:
                icon = icon[0]

            icon_hash = compute_image_hash('https://alfred.app' + icon["src"])

            if icon is None or h2 is None or p is None:
                continue

            href_parts = a_tag["href"].split("/")
            if len(href_parts) < 3:
                continue

            workflows.append({
                "url": 'https://alfred.app' + a_tag["href"],
                "icon_url": 'https://alfred.app' + icon["src"],
                'icon_hash': icon_hash,
                "title": h2.text,
                "description": p.text,
                "author": href_parts[2],
                'installation_url': 'alfred://gallery' + a_tag["href"].replace("/workflows/", "/workflow/")
            })

        pagination_section = soup.find("nav", {"class": "pagination"})
        if pagination_section is None:
            break

        next_page = pagination_section.find("li", {"class": "pagenext"})
        if next_page is None:
            break

        link = next_page.find('a')
        if link:
            url = "https://alfred.app" + link["href"]
        else:
            break
        page += 1

    return workflows


def compute_image_hash(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the image URL: {e}")
        return None

    image_data = response.content
    sha256 = hashlib.sha256()
    sha256.update(image_data)

    return sha256.hexdigest()

try:
    workflows = get_workflows(url)
    with open('workflows.json', 'w') as f:
        json.dump(workflows, f, indent=4)
except Exception as e:
    print(f"An unexpected error occurred: {e}")

