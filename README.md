# Terencher Management System

A comprehensive management system for trencher operations, built with PyQt6, SQLite, and Pandas.

## Project Structure

```
terencher/
├── src/
│   ├── gui/           # GUI components and windows
│   ├── database/      # Database operations and models
│   ├── services/      # Business logic and calculations
│   ├── utils/         # Utility functions
│   └── locales/       # Localization files
├── tests/             # Test files
├── reports/           # Generated reports
├── data/              # Data files and backups
├── logs/              # Application logs
├── main.py           # Main entry point
├── requirements.txt   # Dependencies
└── README.md         # This file
```

## Features

- Trencher and operator management
- Project tracking and scheduling
- Financial calculations and reporting
- Data export (CSV, PDF)
- Multi-language support

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Development

- The application uses SQLite for data storage
- GUI is built with PyQt6
- Reports are generated using Pandas
- Tests can be run with pytest

## License

This project is licensed under the MIT License - see the LICENSE file for details.