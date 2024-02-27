# Indeed Salary Scraper

## Overview
This script is designed to automate the process of gathering salary information from Indeed.com. It specifically targets job titles and locations specified by the user, extracting average salaries, company names, aggregate ratings, the number of reviews, and the number of salaries reported for top-paying companies in the specified field and location.

## Requirements
- Python 3.6+
- asyncio
- pyppeteer

Ensure you have Python installed on your system and the necessary libraries. You can install pyppeteer using pip:

```bash
pip install pyppeteer
```

## Usage
1. **Setting Up**: Before running the script, ensure Python and pyppeteer are installed on your machine.
2. **Customizing Search Parameters**: Modify the main function's scrape_indeed call within the script to include the job title and location you're interested in. For example:
    
```python
asyncio.get_event_loop().run_until_complete(scrape_indeed('Software Engineer', 'San Francisco, CA'))
```

3. **Running the Script**: Execute the script in your terminal or command prompt:

```bash
python indeed_scraper.py
```

4. **Viewing Results**: The script prints the extracted data directly to the console. The data includes:
    - Company name
    - Aggregate rating
    - Average salary
    - Number of reviews
    - Salaries reported

## Final Notes
This script is a powerful tool for quickly gathering salary information across different job titles and locations. It's ideal for job seekers, researchers, or anyone interested in labor market trends. Remember to use it responsibly and consider Indeed's terms of service regarding automated access and data usage.