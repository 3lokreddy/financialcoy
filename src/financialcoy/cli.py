"""Command-line interface for financialcoy."""
from __future__ import annotations

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from financialcoy import calc, expenses, portfolio
from financialcoy.market import get_history, get_quotes


console = Console()


@click.group(help="financialcoy: personal-finance CLI.")
@click.version_option(package_name="financialcoy")
def main() -> None:
    pass


# ---------------------------------------------------------------------------
# market
# ---------------------------------------------------------------------------
@main.group(help="Market data (quotes, history).")
def market() -> None:
    pass


@market.command("quote", help="Print latest quotes for one or more symbols.")
@click.argument("symbols", nargs=-1, required=True)
def market_quote(symbols: tuple[str, ...]) -> None:
    quotes = get_quotes(list(symbols))
    table = Table(title="Quotes")
    table.add_column("symbol")
    table.add_column("price", justify="right")
    table.add_column("currency")
    for q in quotes:
        table.add_row(q.symbol, f"{q.price:,.2f}", q.currency or "")
    console.print(table)


@market.command("history", help="Print price history for a symbol.")
@click.argument("symbol")
@click.option("--period", default="1mo", show_default=True)
@click.option("--interval", default="1d", show_default=True)
def market_history(symbol: str, period: str, interval: str) -> None:
    df = get_history(symbol, period=period, interval=interval)
    console.print(df[["open", "high", "low", "close", "volume"]].tail(20))


# ---------------------------------------------------------------------------
# portfolio
# ---------------------------------------------------------------------------
@main.group(help="Portfolio tracking from a holdings CSV.")
def folio() -> None:
    pass


@folio.command("show", help="Value holdings and print per-position + totals.")
@click.argument("holdings_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def folio_show(holdings_csv: Path) -> None:
    holdings = portfolio.load_holdings(holdings_csv)
    valued = portfolio.value_holdings(holdings)

    table = Table(title=f"Portfolio: {holdings_csv.name}")
    for col in ["symbol", "shares", "cost_basis", "price", "market_value", "gain", "return_pct"]:
        table.add_column(col, justify="right" if col != "symbol" else "left")
    for _, row in valued.iterrows():
        table.add_row(
            row["symbol"],
            f"{row['shares']:,.4f}",
            f"{row['cost_basis']:,.2f}",
            f"{row['price']:,.2f}",
            f"{row['market_value']:,.2f}",
            f"{row['gain']:,.2f}",
            f"{row['return_pct']:.2f}%",
        )
    console.print(table)

    summary = portfolio.summarize(valued)
    console.print(
        f"[bold]Total:[/bold] value={summary['market_value']:,.2f} "
        f"cost={summary['cost']:,.2f} gain={summary['gain']:,.2f} "
        f"return={summary['return_pct']:.2f}%"
    )


# ---------------------------------------------------------------------------
# expenses
# ---------------------------------------------------------------------------
@main.group(help="Expense and budget analysis from a transactions CSV.")
def expense() -> None:
    pass


@expense.command("by-category", help="Spend totals grouped by category.")
@click.argument("transactions_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def expense_by_category(transactions_csv: Path) -> None:
    df = expenses.load_transactions(transactions_csv)
    summary = expenses.summarize_by_category(df)
    table = Table(title="Spend by category")
    table.add_column("category")
    table.add_column("spend", justify="right")
    for _, row in summary.iterrows():
        table.add_row(row["category"], f"{row['spend']:,.2f}")
    console.print(table)


@expense.command("monthly", help="Income, expense, and net per month.")
@click.argument("transactions_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def expense_monthly(transactions_csv: Path) -> None:
    df = expenses.load_transactions(transactions_csv)
    summary = expenses.monthly_summary(df)
    table = Table(title="Monthly summary")
    for col in ["month", "income", "expense", "net"]:
        table.add_column(col, justify="right" if col != "month" else "left")
    for _, row in summary.iterrows():
        table.add_row(
            row["month"],
            f"{row['income']:,.2f}",
            f"{row['expense']:,.2f}",
            f"{row['net']:,.2f}",
        )
    console.print(table)


@expense.command("budget", help="Compare actual spend to a JSON budget file.")
@click.argument("transactions_csv", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("budget_json", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def expense_budget(transactions_csv: Path, budget_json: Path) -> None:
    df = expenses.load_transactions(transactions_csv)
    budgets = json.loads(budget_json.read_text())
    report = expenses.budget_report(df, budgets)
    table = Table(title="Budget report")
    for col in ["category", "budget", "actual", "remaining", "over"]:
        table.add_column(col)
    for _, row in report.iterrows():
        table.add_row(
            row["category"],
            f"{row['budget']:,.2f}",
            f"{row['actual']:,.2f}",
            f"{row['remaining']:,.2f}",
            "YES" if row["over"] else "no",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# calculators
# ---------------------------------------------------------------------------
@main.group(help="Financial calculators.")
def calculate() -> None:
    pass


@calculate.command("compound", help="Compound interest over time.")
@click.option("--principal", type=float, required=True)
@click.option("--rate", type=float, required=True, help="annual rate, e.g. 0.07 for 7%")
@click.option("--years", type=float, required=True)
@click.option("--n", type=int, default=12, show_default=True, help="compounding periods/year")
def calculate_compound(principal: float, rate: float, years: float, n: int) -> None:
    fv = calc.compound_interest(principal, rate, years, n)
    console.print(f"Future value: [bold]{fv:,.2f}[/bold]")


@calculate.command("loan", help="Loan payment + amortization schedule.")
@click.option("--principal", type=float, required=True)
@click.option("--rate", type=float, required=True, help="annual rate, e.g. 0.05")
@click.option("--years", type=float, required=True)
@click.option("--n", type=int, default=12, show_default=True)
@click.option("--schedule/--no-schedule", default=False, help="print full amortization table")
def calculate_loan(principal: float, rate: float, years: float, n: int, schedule: bool) -> None:
    pmt = calc.loan_payment(principal, rate, years, n)
    console.print(f"Periodic payment: [bold]{pmt:,.2f}[/bold]")
    if schedule:
        table = Table(title="Amortization")
        for col in ["period", "payment", "interest", "principal", "balance"]:
            table.add_column(col, justify="right")
        for r in calc.amortization_schedule(principal, rate, years, n):
            table.add_row(
                str(r.period),
                f"{r.payment:,.2f}",
                f"{r.interest:,.2f}",
                f"{r.principal:,.2f}",
                f"{r.balance:,.2f}",
            )
        console.print(table)


@calculate.command("npv", help="Net present value.")
@click.option("--rate", type=float, required=True)
@click.argument("cashflows", nargs=-1, type=float, required=True)
def calculate_npv(rate: float, cashflows: tuple[float, ...]) -> None:
    console.print(f"NPV: [bold]{calc.npv(rate, list(cashflows)):,.2f}[/bold]")


@calculate.command("irr", help="Internal rate of return.")
@click.argument("cashflows", nargs=-1, type=float, required=True)
def calculate_irr(cashflows: tuple[float, ...]) -> None:
    console.print(f"IRR: [bold]{calc.irr(list(cashflows)) * 100:.4f}%[/bold]")


@calculate.command("retire", help="Project retirement savings balance.")
@click.option("--current", type=float, required=True)
@click.option("--annual", type=float, required=True, help="annual contribution")
@click.option("--rate", type=float, required=True)
@click.option("--years", type=float, required=True)
def calculate_retire(current: float, annual: float, rate: float, years: float) -> None:
    fv = calc.retirement_target(current, annual, rate, years)
    console.print(f"Projected balance: [bold]{fv:,.2f}[/bold]")


if __name__ == "__main__":
    main()
