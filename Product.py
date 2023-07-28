import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

def scrape_product_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting ASIN
        asin = soup.find('th', text='ASIN').find_next_sibling('td').text.strip()

        # Extracting Product Description
        product_description = soup.find('div', {'id': 'productDescription'}).text.strip()

        # Extracting Manufacturer
        manufacturer = soup.find('a', {'id': 'bylineInfo'}).text.strip()

        # Extracting Description
        description = soup.find('div', {'id': 'feature-bullets'}).ul.text.strip()

        return {
            'ASIN': asin,
            'Product Description': product_description,
            'Manufacturer': manufacturer,
            'Description': description
        }
    else:
        print(f"Failed to retrieve product details for URL: {url}")
        return None

def scrape_amazon_products(url, pages_to_scrape=20, products_to_hit=200):
    all_products = []

    for page_num in range(1, pages_to_scrape + 1):
        page_url = url + f'&page={page_num}'

        # Send a GET request to the Amazon URL
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all the product containers on the page
            product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

            for container in product_containers:
                # Extracting Product URL
                product_url = container.find('a', {'class': 'a-link-normal'})['href']

                # Extracting Product Name
                product_name = container.find('span', {'class': 'a-size-medium'}).text.strip()

                # Extracting Product Price
                product_price = container.find('span', {'class': 'a-price'}).find('span', {'class': 'a-offscreen'}).text.strip()

                # Extracting Rating
                rating = container.find('span', {'class': 'a-icon-alt'})
                product_rating = rating.text if rating else 'N/A'

                # Extracting Number of Reviews
                num_reviews = container.find('span', {'class': 'a-size-base'}).text.strip()

                # Scrape product details from the product URL
                product_details = scrape_product_details(f'https://www.amazon.in{product_url}')
                if product_details:
                    all_products.append({
                        'Product URL': f'https://www.amazon.in{product_url}',
                        'Product Name': product_name,
                        'Product Price': product_price,
                        'Rating': product_rating,
                        'Number of Reviews': num_reviews,
                        **product_details
                    })

                # Check if we have scraped the desired number of products
                if len(all_products) >= products_to_hit:
                    break

        else:
            print(f"Failed to retrieve page {page_num}. Status Code: {response.status_code}")
            break

        # Check if we have scraped the desired number of products
        if len(all_products) >= products_to_hit:
            break

    return all_products

if __name__ == "__main__":
    # URL to scrape
    amazon_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'

    # Scrape 20 pages of products and hit 200 product URLs
    scraped_products = scrape_amazon_products(amazon_url, pages_to_scrape=20, products_to_hit=200)

    # Export the data to a CSV file
    csv_filename = 'amazon_products.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'ASIN',
                      'Product Description', 'Manufacturer', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scraped_products)

    print(f"Scraped data saved to {csv_filename}")
