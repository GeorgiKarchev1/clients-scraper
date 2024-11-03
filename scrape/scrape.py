import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import json
from typing import List, Dict

class BusinessScraper:
    def __init__(self):
        self.results: List[Dict] = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        self.target_categories = [
            'restaurants', 'gyms', 'fitness', 'salons', 
            'spas', 'real estate', 'hotels', 'wedding venues'
        ]

    def scrape_yelp_website(self, location: str, category: str):
        """Scrape business information directly from Yelp website"""
        search_url = f"https://www.yelp.com/search?find_desc={category}&find_loc={location}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            print(f"Yelp Status Code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Updated selectors for Yelp
            businesses = soup.find_all('div', {'class': 'arrange-unit__373c0__1piwO'})
            
            if not businesses:
                print("No businesses found on Yelp with primary selector, trying alternative...")
                businesses = soup.find_all('div', {'class': 'container'})
            
            print(f"Found {len(businesses)} businesses on Yelp")
            
            for business in businesses:
                try:
                    # Updated selectors
                    name_element = business.find('a', {'class': 'css-19v1rkv'}) or business.find('a', {'class': 'link__373c0'})
                    if not name_element:
                        continue
                        
                    name = name_element.text.strip()
                    business_url = "https://www.yelp.com" + name_element['href'] if name_element.get('href') else None
                    
                    # Get address
                    address_element = business.find('span', {'class': 'css-chan6m'}) or business.find('address')
                    address = address_element.text.strip() if address_element else None
                    
                    # Get rating
                    rating_element = business.find('span', {'class': 'display--inline__373c0__2SfH_'})
                    rating = rating_element.text.strip() if rating_element else None

                    self.results.append({
                        'business_name': name,
                        'website': business_url,
                        'location': address,
                        'business_category': category,
                        'rating': rating,
                        'source': 'Yelp',
                        'scrape_date': datetime.now().strftime("%Y-%m-%d")
                    })
                    print(f"Added business: {name}")
                    
                except Exception as e:
                    print(f"Error processing Yelp business: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Yelp website for {category} in {location}: {e}")

    def scrape_yellow_pages(self, location: str, category: str):
        """Scrape business information from Yellow Pages"""
        search_url = f"https://www.yellowpages.com/search?search_terms={category}&geo_location_terms={location}"
        
        try:
            response = requests.get(search_url, headers=self.headers)
            print(f"YP Status Code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            businesses = soup.find_all('div', {'class': 'result'})
            
            print(f"Found {len(businesses)} businesses on Yellow Pages")
            
            for business in businesses:
                try:
                    name_element = business.find('a', {'class': 'business-name'})
                    if not name_element:
                        continue
                        
                    name = name_element.text.strip()
                    business_url = "https://www.yellowpages.com" + name_element['href'] if name_element.get('href') else None
                    
                    # Get address
                    address_element = business.find('div', {'class': 'street-address'})
                    address = address_element.text.strip() if address_element else None
                    
                    # Get phone
                    phone_element = business.find('div', {'class': 'phones'})
                    phone = phone_element.text.strip() if phone_element else None

                    self.results.append({
                        'business_name': name,
                        'website': business_url,
                        'phone': phone,
                        'location': address,
                        'business_category': category,
                        'source': 'Yellow Pages',
                        'scrape_date': datetime.now().strftime("%Y-%m-%d")
                    })
                    print(f"Added business: {name}")
                    
                except Exception as e:
                    print(f"Error processing YP business: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping Yellow Pages for {category} in {location}: {e}")

    def export_results(self, filename="video_editing_jobs.csv"):
        """Export results to CSV file"""
        if not self.results:
            print("No results to export!")
            return
            
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")
        print(f"Total businesses found: {len(self.results)}")

def main():
    scraper = BusinessScraper()
    
    # List of locations to search in
    locations = ["New York, NY", "Los Angeles, CA", "Chicago, IL"]
    
    # Scrape data for each location and category combination
    for location in locations:
        for category in scraper.target_categories:
            print(f"\nScraping {category} businesses in {location}...")
            scraper.scrape_yelp_website(location, category)
            scraper.scrape_yellow_pages(location, category)
            # Add delay to avoid rate limiting
            time.sleep(5)
    
    # Export results
    scraper.export_results()

if __name__ == "__main__":
    main()