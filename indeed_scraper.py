import csv
import os
import asyncio
from pyppeteer import launch

async def extract_salary_by_label(page, label):
    '''
    Extracts the salary information from the page based on the label provided.

    Arguments:
        page: The page object to extract the salary information from
        label: The label to search for in the page
    
    Returns:
        The salary text content associated with the label
    '''
    # Construct an XPath expression to find a span containing specific text, then select its parent
    xpath_expression = f"//span[contains(text(), '{label}')]/parent::*"
    
    # Execute the XPath query, which returns a list of matching ElementHandles
    elements = await page.xpath(xpath_expression)
    
    # Assuming the first match is the desired one, extract its text content
    if elements:
        salary = await page.evaluate('(element) => element.textContent', elements[0])
        return salary.split()[-1] # Assuming salary is the last word in the textContent
    else:
        # If no elements were found, raise a ValueError
        raise ValueError(f"No element with label '{label}' found on the page")

async def scrape_indeed(browser, job_title: str, search_location: str, top_company_writer):
    '''
    Scrapes the indeed.com website for salary information and top companies hiring for a specific job title
    in a specific location. The scraped data is then written to two CSV files.
    
    Arguments:
        browser: The browser object to use for scraping
        job_title: The job title to search for
        search_location: The location to search for the job title
        top_company_writer: The CSV writer object to write the top companies data to
        
    Returns:
        None
    '''
    # Open a new page (tab) in the browser
    page = await browser.newPage()

    try:
        # Go to indeed.com/career/salaries
        #***** Replace the URL with the country-specific version of Indeed for searches outside of US geographies. *****#
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

        # Check if the search returned the expected results
        search_result_element = await page.querySelector('div[data-testid="salary-information"] div h1')
        search_result = await page.evaluate('(element) => element.textContent', search_result_element)

        # If the search does not contain the job title and location, raise an error
        if job_title.lower() not in search_result.lower() or search_location.lower() not in search_result.lower():
            raise ValueError(f"Search did not return the expected results. Found: '{search_result}'")

        # Extract aggregated salary information including low, average, and high base salaries
        avg_base_salary_element = await page.querySelector('div[data-testid = "avg-salary-value"]')
        avg_base_salary = await page.evaluate('(element) => element.textContent', avg_base_salary_element)

        # As low and high base salary content is not stored in unique div classes, we need to use 
        # XPath to extract them. This is implemented in the extract_salary_by_label function.
        try:
            low_base_salary = await extract_salary_by_label(page, 'Low')
        except ValueError as e:
            low_base_salary = 'Error: Not found'
            print(f"Warning: {e} for '{job_title} | {search_location}'") # Log the error message

        try:
            high_base_salary = await extract_salary_by_label(page, 'High')
        except ValueError as e:
            high_base_salary = 'Error: Not found'
            print(f"Warning: {e} for '{job_title} | {search_location}'") # Log the error message

        # Append the average base salary to the CSV file
        with open('base_salary.csv', 'a', newline='', encoding='utf-8') as file:
            avg_base_salary_writer = csv.writer(file)
            avg_base_salary_writer.writerow([job_title, search_location, low_base_salary, avg_base_salary, high_base_salary])

        # Fully expand the list of "Top Companies..." (max expansions = 3, which gives 20 results). If there
        # are fewer than 20 results, the button should not be toggled 3 times.
        for _ in range(3):
            expand_button_element = await page.querySelector('button[data-a11y-tabtest="top-paying-load-more-button"]')

            # If the list is already fully expanded, break
            if await page.evaluate('(element) => element.textContent', expand_button_element) == 'Show less':
                break

            # Click the button to expand the list
            await expand_button_element.click()

        # Select all list items from "Top Companies..." list and extract company name, aggregate rating, 
        # average salary, number of reviews, and number of salaries reported from each list item.
        top_company_listings = await page.querySelectorAll('li[data-tn-element="ranked-list-item"]')

        # If no top company listings are found, raise a ValueError
        if not top_company_listings:
            raise ValueError("No top company listings found on the page")
        
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

    finally:
        # Close the page after the scraping task is complete or an error occurs
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
        avg_base_salary_file_exists = os.path.isfile('base_salary.csv')
        top_companies_file_exists = os.path.isfile('top_companies.csv')

        # Open a CSV file to store the average base salary associated with each search
        with open('base_salary.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the headers if the file does not yet exist
            if not avg_base_salary_file_exists:
                writer.writerow(['Job Title', 'Search Location', 'Low Base Salary', 'Average Base Salary', 'High Base Salary'])

        
        with open('top_companies.csv', 'a', newline='', encoding='utf-8') as file:
            top_company_writer = csv.writer(file)

            # Write the headers if the file does not yet exist
            if not top_companies_file_exists:
                top_company_writer.writerow(['Job Title', 'Search Location', 'Company Name', 'Aggregate Rating', 'Average Salary', 'Number of Reviews', 'Salaries Reported'])

            for job_title, search_location in inputs:
                try:
                    await scrape_indeed(browser, job_title, search_location, top_company_writer)
                except Exception as e:
                    print(f"An error occured while scraping the page for '{job_title} | {search_location}': {e}")

    except Exception as e:
        print(f"An error occurred while executing the program: {e}")

    finally:
        # Close the browser after all tasks are done
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())