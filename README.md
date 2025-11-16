# Performativ Tech Challenge - Financial Metrics Calculator

A Python-based financial metrics calculator that computes simplified financial metrics for investment positions over a specified time window. This project calculates metrics at both the positional level (individual positions) and basket level (aggregated positions).

## Overview

This application takes a set of investment positions with open/close dates and prices, retrieves market data (prices and FX rates) from the Performativ API, and calculates comprehensive financial metrics including:

- **IsOpen**: Whether a position was open on a given day
- **Price**: Market price of the instrument in local and target currency
- **Value**: Position value in local and target currency
- **ReturnPerPeriod**: Daily monetary return
- **ReturnPerPeriodPercentage**: Daily percentage return

## Project Structure

```
performativ-tech-challenge/
├── src/
│   ├── main.py                          # Entry point
│   ├── controllers/
│   │   └── main_controller.py           # Main application controller
│   ├── services/
│   │   ├── financial_metrics_calculator.py   # Core metrics calculation
│   │   ├── position_calculator.py            # Position-level calculations
│   │   ├── basket_calculator.py              # Basket-level aggregations
│   │   └── performativ_resource_loader.py    # API data loader
│   ├── repositories/
│   │   ├── positions_data_repo.py       # Position data file handling
│   │   ├── performativ_api_repo.py      # Performativ API client
│   │   ├── enviroment_loader.py         # Environment configuration
│   │   └── tests/                       # Repository unit tests
│   ├── models/
│   │   ├── positions_data.py            # Position DTOs
│   │   ├── performativ_api_params.py    # API request/response models
│   │   ├── performativ_resource.py      # Data resource models
│   │   └── position_metric_fields.py    # Metric field constants
│   ├── entities/
│   │   └── financial_metrics.py         # Financial metrics data classes
│   └── .env                             # Environment variables
├── pyproject.toml                       # Project configuration
├── tech-challenge-2025-positions.json   # Sample positions data
└── README.md                            # This file
```

## Prerequisites

- Python 3.14+
- uv

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd performativ-tech-challenge
```

2. **Install dependencies:**
```bash
./scripts/build_dependencies.sh install
```

3. **Set up environment variables:**

Create a `.env` file in the `src/` directory with the following variables:

```env
PYTHONPATH=src
PERFORMATIV_API_URL=performativ_api
PERFORMATIV_API_KEY=your_api_key_here
PERFORMATIV_CANDIDATE_ID=your_candidate_id_here
VALUE_PRECISION=8
```

## Usage

### Using the Run Script (Recommended)

The simplest way to run the application:

```bash
# Make script executable (first time only)
chmod +x scripts/run_app.sh

# Run with default parameters (USD, 2023-01-01 to 2024-11-10)
./scripts/run_app.sh /path/to/positions.json

# Run with custom parameters
./scripts/run_app.sh /path/to/positions.json EUR 2023-01-01 2024-12-31

# Skip virtual environment setup and build (faster reruns)
SKIP_BUILD=true ./scripts/run_app.sh /path/to/positions.json
```

### Direct Python Execution

Alternatively, run directly with Python:

```bash
PYTHONPATH=src python -m src.main \
  --positions-file=/path/to/positions.json \
  --target-currency=EUR \
  --start-date=2023-01-01 \
  --end-date=2024-12-31
```

### Command-Line Options

- `--positions-file` (required): Path to JSON file containing position data
- `--target-currency` (optional, default: USD): Target currency for conversion (e.g., EUR, GBP, SEK)
- `--start-date` (optional, default: 2023-01-01): Start date in YYYY-MM-DD format
- `--end-date` (optional, default: 2024-11-10): End date in YYYY-MM-DD format

## Input Data Format

### Positions File

The positions file should be a JSON file with the following structure:

```json
{
  "positions": [
    {
      "id": 24141,
      "open_date": "2021-01-15",
      "close_date": "2022-02-15",
      "open_price": "152.21451251",
      "close_price": "98.1242",
      "quantity": 142.21,
      "instrument_id": 413,
      "instrument_currency": "GBP"
    }
  ]
}
```

**Fields:**
- `id`: Unique position identifier
- `open_date`: Date position was opened (YYYY-MM-DD)
- `close_date`: Date position was closed (null if still open)
- `open_price`: Price at which position was opened
- `close_price`: Price at which position was closed (null if still open)
- `quantity`: Number of shares/units
- `instrument_id`: Identifier for the instrument
- `instrument_currency`: Currency of the instrument (local currency)

## Output Data Format

The application returns metrics in the following structure:

```json
{
  "positions": {
    "24141": {
      "IsOpen": [1.0, 1.0, ..., 0.0],
      "Price": [152.21, 152.50, ..., 98.12],
      "Value": [21614.41, 21665.63, ..., 0.0],
      "ReturnPerPeriod": [0.0, 51.22, ..., -100.0],
      "ReturnPerPeriodPercentage": [0.0, 0.24, ..., -1.02]
    }
  },
  "basket": {
    "IsOpen": [1.0, 1.0, ..., 0.0],
    "Price": [0.0, 0.0, ..., 0.0],
    "Value": [21614.41, 21665.63, ..., 0.0],
    "ReturnPerPeriod": [0.0, 51.22, ..., -100.0],
    "ReturnPerPeriodPercentage": [0.0, 0.24, ..., -1.02]
  },
  "dates": ["2021-01-15", "2021-01-16", ..., "2022-02-15"]
}
```

**Metrics:**
- `IsOpen`: 1.0 if position was open, 0.0 if closed
- `Price`: Market price in target currency
- `Value`: Position value (Price × Quantity)
- `ReturnPerPeriod`: Daily monetary return
- `ReturnPerPeriodPercentage`: Daily percentage return

## Key Calculations

### Position-Level Metrics

1. **IsOpen**: Determined by open_date and close_date
2. **PriceLocal**: Market price in instrument's local currency
3. **PriceTarget**: Price converted to target currency using FX rates
4. **Quantity**: Position quantity (0 if closed)
5. **ValueLocal**: PriceLocal × Quantity
6. **ValueTarget**: ValueLocal × FX Rate
7. **ReturnPerPeriod**: Daily change in ValueTarget
8. **ReturnPerPeriodPercentage**: Daily percentage change in ValueTarget

### Basket-Level Metrics

Basket metrics are aggregates of all positions:
- Sum of all position values
- Average returns across positions
- Weighted return percentages

## API Integration

The calculator integrates with the Performativ API to fetch:

1. **FX Rates** (`/fx-rates` endpoint)
   - Currency pair rates for each day in the time window
   - Used to convert local prices to target currency

2. **Instrument Prices** (`/prices` endpoint)
   - Historical prices for each instrument
   - Required for all metric calculations

## Scripts

The project includes several utility scripts for building, testing, and code quality:

```bash
# Build and run the application
./scripts/run_app.sh /path/to/positions.json

# Build dependencies
./scripts/build_dependencies.sh <update|install>
  update  - Update requirements.txt from requirements.in
  install - Install dependencies from requirements.txt

# Format and lint code
./scripts/format_code.sh <check|fix>
  check - Check for code formatting issues
  fix   - Auto-fix code formatting issues

# Run tests
./scripts/test_app.sh <unit_test|integration_test>
  unit_test        - Run unit tests
  integration_test - Run integration tests

# Complete build (format check, tests, then prepare)
./scripts/build_app.sh
```

## Testing

### Run Unit Tests

```bash
pytest src -vv
```

### Run Specific Test File

```bash
pytest src/repositories/tests/test_performativ_api_repo.py -vv
```

### Generate Coverage Report

```bash
pytest src --cov=src --cov-report=html
# Open htmlcov/index.html in your browser
```

### Test Structure

- `src/repositories/tests/`: Repository layer tests
- Coverage reports generated in `htmlcov/`
- Tests follow the pattern established in `test_positions_data_repo.py`

## Configuration

### Environment Variables

Defined in `src/.env`:

- `PERFORMATIV_API_URL`: Base URL for Performativ API
- `PERFORMATIV_API_KEY`: API authentication key
- `PERFORMATIV_CANDIDATE_ID`: Candidate identifier for submissions
- `VALUE_PRECISION`: Decimal precision for numerical results (8 decimals)

### Tool Configuration

`pyproject.toml` includes configuration for:
- **mypy**: Static type checking
- **ruff**: Code linting and formatting
- **pytest**: Unit testing
- **coverage**: Code coverage tracking

## Known Implementation Details

1. **Precision**: All numerical results are evaluated with eight decimal point precision.
3. **FX Rates**: Default FX rate is 1.0 for missing currency pairs
4. **Date Alignment**: All time series are aligned to the specified date range

## Development

### Adding New Metrics

To add a new financial metric:

1. **Define the metric field** in `src/entities/position.py`:
   ```python
   class PositionMetricFields(str, Enum):
       NEW_METRIC = "new_metric"
   ```

2. **Implement calculation** in `src/services/position_calculator.py`:
   ```python
   def _new_metric_calculate(self, dataframe: DataFrame) -> None:
       dataframe[PositionMetricFields.NEW_METRIC] = ...
   ```

3. **Call the calculation** in the `calculate()` method

4. **Add aggregation** in `src/services/basket_calculator.py` if needed:
   ```python
   def _new_metric_calculate(self, basket_aggregate: DataFrameGroupBy) -> Series[float]:
       return basket_aggregate.sum()
   ```

5. **Include in response** in `src/models/performativ_api_params.py`:
   ```python
   NewMetric: list[float]
   ```

### Project Dependencies

Core dependencies:
- **pandas**: Data manipulation and time series analysis
- **pydantic**: Data validation and settings
- **requests**: HTTP client for API calls
- **numpy**: Numerical computing

Development dependencies:
- **pytest**: Testing framework
- **mypy**: Type checking
- **ruff**: Linting and formatting
- **uv**: Package management

## Troubleshooting

### "Positions file not found"

Verify the `--positions-file` path is correct and the file exists:

```bash
ls -la tech-challenge-2025-positions.json
```

### API Authentication Errors

Check environment variables in `src/.env`:
- `PERFORMATIV_API_KEY` is valid
- `PERFORMATIV_CANDIDATE_ID` is correct
- `PERFORMATIV_API_URL` is reachable

## Performance Considerations

- The calculator processes up to 680 days (one value per day per metric)
- Lazy loading of API data reduces memory usage
- Pandas operations are vectorized for efficiency

## License

This project is part of the Performativ Tech Challenge.