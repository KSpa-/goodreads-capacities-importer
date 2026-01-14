# GoodReads to Capacities Importer

Import your read books from GoodReads into Capacities. 

PLEASE NOTE THAT CAPACITIES API CANNOT ACTUALLY HANDLE CREATING OBJECTS VIA API YET

## Features

- Imports only books you've actually read (books with a read date or rating)
- Transfers title, author, ISBN, rating, pages, publisher, and read date
- Includes both public reviews and private notes
- Preserves bookshelf information and publication year
- Preview mode to test before full import
- Rate limiting to respect API limits

## Prerequisites

- Python 3.7+
- A Capacities account with API access
- Your GoodReads library export CSV

## API Documentation

This project uses the Capacities API. For more details on the API and available endpoints, see the [official Capacities API documentation](https://docs.capacities.io/developer/api#api-reference).

## Setup

1. **Export your GoodReads library**
   - Go to GoodReads → My Books → Import and Export → Export Library
   - Download the CSV file and place it in the same directory as this script
   - Rename it to `goodreads_library_export.csv`

2. **Get your Capacities API credentials**
   - Log into Capacities
   - Go to Settings → API
   - Generate an API token
   - Note your Space ID and Structure ID for Books
   - See the [Capacities API documentation](https://docs.capacities.io/developer/api#api-reference) for more details

   **Optional:** Run `find_properties.py` to see all available structures and property IDs in your space:
   ```bash
   export CAPACITIES_API_TOKEN="your_token"
   export CAPACITIES_SPACE_ID="your_space_id"
   python find_properties.py
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   
   **On macOS/Linux:**
   ```bash
   export CAPACITIES_API_TOKEN="your_api_token_here"
   export CAPACITIES_SPACE_ID="your_space_id_here"
   export CAPACITIES_STRUCTURE_ID="your_structure_id_here"
   ```
   
   **On Windows (Command Prompt):**
   ```cmd
   set CAPACITIES_API_TOKEN=your_api_token_here
   set CAPACITIES_SPACE_ID=your_space_id_here
   set CAPACITIES_STRUCTURE_ID=your_structure_id_here
   ```
   
   **On Windows (PowerShell):**
   ```powershell
   $env:CAPACITIES_API_TOKEN="your_api_token_here"
   $env:CAPACITIES_SPACE_ID="your_space_id_here"
   $env:CAPACITIES_STRUCTURE_ID="your_structure_id_here"
   ```

5. **Run the script**
   ```bash
   python import_books.py
   ```

## Usage

When you run the script, it will:

1. Load and filter your GoodReads export
2. Show a preview of the first 10 books
3. Ask if you want to proceed with the full import or test with 10 books

**Options:**
- `y` or `yes` - Import all read books
- `test` - Import only the first 10 books (for testing)
- `n` or `no` - Cancel the import

## What Gets Imported

- **Title** - Book title
- **Author** - Author name
- **ISBN** - ISBN-13 number
- **Rating** - Your rating (1-5 stars)
- **Pages** - Number of pages
- **Publisher** - Publisher name
- **Date Read** - When you finished the book
- **Notes** - Your review and private notes
- **Description** - Bookshelf tags and publication year

## Filtering Logic

A book is considered "read" if it has:
- A date in the "Date Read" field, OR
- A rating greater than 0

All other books are skipped.

## Rate Limiting

The script includes a 1.2 second delay between requests to stay within Capacities' API rate limits (~50 requests per minute).

## Troubleshooting

**"Missing required environment variables" error:**
- Make sure you've set all three environment variables before running the script

**"404 Not Found" errors:**
- Verify your Space ID and Structure ID are correct
- Make sure your API token is valid and hasn't expired

**Date formatting issues:**
- GoodReads exports dates in YYYY/MM/DD format
- The script converts these to YYYY-MM-DD for Capacities

**Books not showing as read:**
- Check that the book has either a "Date Read" or a "My Rating" value in the CSV

## Resources
- [Capacities API Documentation](https://docs.capacities.io/developer/api#api-reference)
- [GoodReads Export Guide](https://www.goodreads.com/review/import)
  
## License

MIT

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
