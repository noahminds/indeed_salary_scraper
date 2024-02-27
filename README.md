# Indeed Salary Scraper

## Overview
This project provides a tool to scrape average base salary data and top company information from Indeed for specified job titles and locations. It uses Python with asyncio and Pyppeteer for asynchronous web scraping, improving efficiency and speed when processing multiple queries.

## Features
- **Dynamic Search Query Input**: Automatically extracts job titles and locations to search for from a provided CSV file (searches.csv), allowing for easy customization and batch processing of multiple queries.
- **Average Base Salary Scraping**: Retrieves average base salary information for specified job titles and locations from Indeed, offering insights into salary expectations across different roles and areas.
- **Top Company Information Extraction**: Gathers detailed information on top companies for each job title and location, including company name, aggregate rating, average salary, number of reviews, and salaries reported, helping identify leading employers in that role and area.
- **CSV Data Export**: Outputs scraped data into CSV files for each search query, facilitating easy access, analysis, and storage of the results. Two CSV files are generated: one for average base salaries (average_base_salary.csv) and another for top companies information (top_companies.csv).

## Requirements
- Python 3.7+
- asyncio
- Pyppeteer
- CSV module (built-in)

## Setup
1. **Install Dependencies**: Ensure you have Python installed on your system and the necessary libraries. You can install pyppeteer using pip:

```bash
pip install pyppeteer
```

2. **Prepare Input File**: Modify or create a CSV file named `searches.csv` with the job titles and locations you want to search for, formatted as "Job Title,Location". Ensure the CSV file is saved in the "Comma Separated Values (.csv)" format (not CSV UTF-8) to avoid encoding issues.

## Usage
1. **Run the Scraper**: Execute the script from the command line.

```bash
python indeed_scraper.py
```

2. **Output**: The script will create or append to two CSV files:
- `average_base_salary.csv`: Contains the average base salary for each job title and location.
- `top_companies.csv`: Contains information on the top companies for each job title and location.

## Notes
- **Headless Mode**: The script is designed to support headless operation for enhanced performance and resource efficiency during scraping tasks. However, no successful operation in headless mode has been observed yet. Users may experience better stability and visual debugging capabilities by running the scraper with the headless option set to `False`. This adjustment allows for real-time monitoring of the scraping process but might require additional resources. I am working on improving the headless mode compatibility and hope to resolve this limitation in future updates.
- **CSV File Formats**: It's crucial to ensure that the input CSV file (`searches.csv`) is saved in the correct format. For optimal compatibility, especially on macOS, the file should be saved as "Comma Separated Values (.csv)" and not "CSV UTF-8". Using the correct format ensures the scraper correctly interprets job titles and locations without encountering encoding issues or unexpected characters.
- **Concurrency**: While the current version of the scraper does not implement concurrency, future updates may include asynchronous processing to enhance efficiency and speed, particularly when handling multiple search queries.

## Consider Legal and Ethical Considerations
Understanding the legal and ethical implications of web scraping is paramount. This script is a powerful tool for quickly gathering salary information across different job titles and locations. It's ideal for job seekers, researchers, or anyone interested in labor market trends. Remember to use it responsibly and consider Indeed's terms of service regarding automated access and data usage.