# financialcoy

A small personal-finance CLI written in Python. Four use cases:

- **Portfolio tracking** — value a CSV of holdings against live quotes.
- **Expense / budget analysis** — categorize a transactions CSV and compare to a budget.
- **Market data** — fetch quotes and price history (via `yfinance`).
- **Financial calculators** — compound interest, loan amortization, NPV, IRR, retirement projection.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The CLI is exposed as `fc`.

## Usage

```bash
fc --help
```

### Market data

```bash
fc market quote AAPL MSFT VTI
fc market history AAPL --period 3mo --interval 1d
```

### Portfolio

`holdings.csv`:

```csv
symbol,shares,cost_basis
AAPL,10,150.00
MSFT,5,280.50
VTI,25,210.00
```

```bash
fc folio show examples/holdings.csv
```

### Expenses & budget

`transactions.csv` (negative amounts are expenses):

```csv
date,description,amount,category
2026-01-02,Paycheck,4200.00,income
2026-01-03,Rent,-1850.00,housing
2026-01-04,Whole Foods,-92.40,groceries
```

```bash
fc expense by-category examples/transactions.csv
fc expense monthly      examples/transactions.csv
fc expense budget       examples/transactions.csv examples/budget.json
```

### Calculators

```bash
fc calculate compound --principal 1000 --rate 0.07 --years 10
fc calculate loan --principal 250000 --rate 0.06 --years 30 --schedule
fc calculate npv --rate 0.08 -- -1000 200 300 400 500
fc calculate irr -- -1000 200 300 400 500
fc calculate retire --current 10000 --annual 6000 --rate 0.06 --years 30
```

## Project layout

```
src/financialcoy/
  cli.py        # click CLI: market / folio / expense / calculate
  market.py     # yfinance wrapper (Quote, get_history)
  portfolio.py  # load/value holdings, summarize
  expenses.py   # load transactions, by-category / monthly / budget
  calc.py       # compound, loan, NPV, IRR, retirement
tests/          # pytest suite (calc, expenses, portfolio)
examples/       # sample holdings.csv, transactions.csv, budget.json
```

## Development

```bash
pytest
ruff check .
```

## Scope notes

This is a v0.1 scaffold. Known gaps:

- Budget reports compare totals against budget without dividing by months in the data.
- No persistence — everything reads CSVs each run.
- Market data is best-effort via `yfinance` and depends on an internet connection.

## License

Apache-2.0 — see `LICENSE`.
