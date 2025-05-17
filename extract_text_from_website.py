import requests
from bs4 import BeautifulSoup

# URL of the legislative document
url = "https://www.ejustice.just.fgov.be/cgi/article.pl?language=fr&sum_date=2024-05-17&lg_txt=f&pd_search=2024-05-17&s_editie=1&numac_search=2024202344&caller=sum&2024202344=4&view_numac=2024202344nx2024202344f"

# Send a GET request to the URL
response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

# Parse the HTML content
soup = BeautifulSoup(response.content, 'html.parser')

# Extract the main content
# Note: The actual HTML structure may vary; adjust selectors as needed
main_content = soup.find('div', class_='detaliuDocument')  # Example class name

# If the specific div is not found, fallback to extracting all text
if main_content:
    text = main_content.get_text(separator='\n', strip=True)
else:
    text = soup.get_text(separator='\n', strip=True)

# Save the text to a .txt file
with open('document.txt', 'w', encoding='utf-8') as file:
    file.write(text)

print("Document text has been saved to 'document.txt'.")
