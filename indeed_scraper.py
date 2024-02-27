import asyncio
from pyppeteer import launch

async def scrape_indeed(job_title: str, search_location: str):
    # Launch the browser instance
    browser = await launch(headless=False)
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

    # Collect the job listing content from the results into a list
    job_listings = await page.querySelectorAll('.resultContent')

    # Extract "Average Base Salary"
    avg_base_salary_element = await page.querySelector('div[data-testid = "avg-salary-value"]')
    avg_base_salary = await page.evaluate('(element) => element.textContent', avg_base_salary_element)

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

        print({
            'Company Name': company_name,
            'Aggregate Rating': rating,
            'Average Salary': avg_salary,
            'Number of Reviews': num_reviews,
            'Salaries Reported': salaries_reported,
        })

    # Close the browser
    await browser.close()


def main():
    asyncio.get_event_loop().run_until_complete(scrape_indeed('Consultant', 'Chicago, IL'))


if __name__ == '__main__':
    main()