import pandas as pd
import numpy as np
from datetime import datetime

def build_cashflows(settlement, maturity, face, coupon_rate, freq):
    """
    settlement, maturity: 'YYYY-MM-DD' strings
    face: face value (e.g. 100000)
    coupon_rate: annual coupon rate (e.g. 0.05 for 5%)
    freq: payments per year (1=annual, 2=semiannual)
    """
    settlement = pd.to_datetime(settlement)
    maturity = pd.to_datetime(maturity)

    # months between payments (e.g. 6 months for semiannual)
    months = 12 // freq

    # generate payment dates
    dates = pd.date_range(
        start=settlement + pd.DateOffset(months=months),
        end=maturity,
        freq=f'{months}M'
    )
    n = len(dates)

    coupon_payment = face * coupon_rate / freq
    interest = np.full(n, coupon_payment, dtype=float)
    principal = np.zeros(n, dtype=float)
    principal[-1] = face  # bullet maturity; last payment returns principal

    total_cf = interest + principal

    df = pd.DataFrame({
        "Period": np.arange(1, n + 1),
        "PaymentDate": dates,
        "Interest": interest,
        "Principal": principal,
        "TotalCashFlow": total_cf
    })

    return df

def add_pv(df, yield_rate, freq):
    """
    Adds discount factor and PV of each cash flow.
    yield_rate: annual yield (e.g. 0.035 for 3.5%)
    """
    per_period_yield = yield_rate / freq
    periods = df["Period"].values
    discount_factors = 1 / (1 + per_period_yield) ** periods
    df["DiscountFactor"] = discount_factors
    df["PVCashFlow"] = df["TotalCashFlow"] * df["DiscountFactor"]
    df["CumPVCashFlow"] = df["PVCashFlow"].cumsum()
    return df

if __name__ == "__main__":
    # Example: 5% coupon, semiannual, 10-year bond
    cashflows = build_cashflows(
        settlement="2025-01-01",
        maturity="2035-01-01",
        face=100000,
        coupon_rate=0.05,
        freq=2
    )
    cashflows = add_pv(cashflows, yield_rate=0.035, freq=2)

    print(cashflows)
    print("\nPrice (PV) at 3.5% yield:", round(cashflows["PVCashFlow"].sum(), 2))

    # Export to Excel so you can compare in your Excel model
    cashflows.to_excel("bond_cashflows_example.xlsx", index=False)
