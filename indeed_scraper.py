import csv
import os
import asyncio
from pyppeteer import launch

async def scrape_indeed(browser, job_title: str, search_location: str, top_company_writer):
    # Open a new page (tab) in the browser
    page = await browser.newPage()

    # Go to indeed.com
    await page.goto('https://www.indeed.com/career/salaries')

    # Wait for the input field elements to load
    await page.waitForSelector('#input-title-autocomplete')
    await page.waitForSelector('#input-location-autocomplete-localized')

    # Type in the search query
    await page.type('#input-title-autocomplete', job_title) # Type in the job title
    await page.click('#input-location-autocomplete-localized', clickCount=3) # Focus the default location input
    await page.keyboard.press('Backspace')  # Clear the input
    await page.type('#input-location-autocomplete-localized', search_location) # Type in the location

    # Click the search button
    await page.click('button[type="submit"]')

    # Wait for the next page to load
    await page.waitForNavigation()

    # Extract "Average Base Salary"
    avg_base_salary_element = await page.querySelector('div[data-testid = "avg-salary-value"]')
    avg_base_salary = await page.evaluate('(element) => element.textContent', avg_base_salary_element)

    # Append the average base salary to the CSV file
    with open('average_base_salary.csv', 'a', newline='', encoding='utf-8') as file:
        avg_base_salary_writer = csv.writer(file)
        avg_base_salary_writer.writerow([job_title, search_location, avg_base_salary])

    # Fully expand the list of "Top Companies..." (max expansions = 3, which gives 20 results). If there
    # are fewer than 20 results, the button should not be toggled 3 times.
    for _ in range(3):
        expand_button_element = await page.querySelector('button[data-a11y-tabtest="top-paying-load-more-button"]')

        # If the list is already fully expanded, break
        if await page.evaluate('(element) => element.textContent', expand_button_element) == 'Show less':
            break

        # Click the button to expand the list
        await expand_button_element.click()

    # import pdb; pdb.set_trace()
    # Select all list items from "Top Companies..." list and extract company name, aggregate rating, 
    # average salary, number of reviews, and number of salaries reported from each
    top_company_listings = await page.querySelectorAll('li[data-tn-element="ranked-list-item"]')
    for company in top_company_listings:
        # Extract the company name
        company_name_element = await company.querySelector('a[data-tn-element="top-paying-company-acme"]')
        company_name = await page.evaluate('(element) => element.textContent', company_name_element)

        # Extract the aggregate rating
        rating_element = await company.querySelector('a[data-tn-element="top-paying-company-reviews"] span')
        rating = await page.evaluate('(element) => element.textContent', rating_element) if rating_element else 'No rating'

        # Extract the average salary
        avg_salary_element = await company.querySelector('strong[data-testid="top-company-salary"]')
        avg_salary = await page.evaluate('(element) => element.textContent', avg_salary_element)

        # Extract the number of reviews
        num_reviews_element = await company.querySelector('a[data-tn-element="top-paying-company-tagline-reviews"]')
        num_reviews = await page.evaluate('(element) => element.textContent', num_reviews_element)
        
        # Extract the number of salaries reported
        salaries_reported_element = await company.querySelector('a[data-tn-element="top-paying-company-tagline-salaries"]')
        salaries_reported = await page.evaluate('(element) => element.textContent', salaries_reported_element)

        # Append the company details to the CSV file
        top_company_writer.writerow([job_title, search_location, company_name, rating, avg_salary, num_reviews, salaries_reported])

    # Close the page after the scraping task is done
    await page.close()
    

async def main():
    # Launch a new browser window
    browser = await launch(headless=False)

    try:
        # Read job titles and locations from a CSV file called 'searches.csv'
        with open('searches.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            inputs = list(reader)
        
        # Check if the CSV file exists to decide on writing headers
        avg_base_salary_file_exists = os.path.isfile('average_base_salary.csv')
        top_companies_file_exists = os.path.isfile('top_companies.csv')

        # Open a CSV file to store the average base salary associated with each search
        with open('average_base_salary.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the headers if the file does not yet exist
            if not avg_base_salary_file_exists:
                writer.writerow(['Job Title', 'Search Location', 'Average Base Salary'])

        
        with open('top_companies.csv', 'a', newline='', encoding='utf-8') as file:
            top_company_writer = csv.writer(file)

            # Write the headers if the file does not yet exist
            if not top_companies_file_exists:
                top_company_writer.writerow(['Job Title', 'Search Location', 'Company Name', 'Aggregate Rating', 'Average Salary', 'Number of Reviews', 'Salaries Reported'])

            for job_title, search_location in inputs:
                await scrape_indeed(browser, job_title, search_location, top_company_writer)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        # Close the browser after all tasks are done
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())