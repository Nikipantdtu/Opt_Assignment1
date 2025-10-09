import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def results_to_dataframe(results, T):
    """Convert results.variables into a tidy DataFrame."""
    df = pd.DataFrame(index=range(T))
    for var, value in results.variables.items():
        # var looks like "l[3]" or "e[10]"
        name, idx = var.split("[")
        t = int(idx.strip("]"))
        df.loc[t, name] = value
    return df.fillna(0.0)

def results_to_dataframe_2b(results, T):
    """
    Convert solver results into a DataFrame of time-series variables.
    Handles both indexed (x[t]) and scalar variables (like E_cap).
    """
    df = pd.DataFrame(index=range(T))

    scalar_vars = {}  # store non-time-dependent variables

    for var, value in results.variables.items():
        if "[" in var:
            name, idx = var.split("[")
            t = int(idx.strip("]"))
            df.loc[t, name] = value
        else:
            scalar_vars[var] = value  # e.g. "E_cap"

    return df.fillna(0)

def clean_net_metering_solution(df):
    """
    Post-process LP results for Net Metering scenario:
    If import and export occur simultaneously, allocate exports to self-consumption first,
    then use imports only for remaining load.
    """
    df_clean = df.copy()

    for t in df_clean.index:
        e = df_clean.loc[t, "e"]
        s = df_clean.loc[t, "s"]
        p = df_clean.loc[t, "p"]
        l = df_clean.loc[t, "l"]

        # If simultaneous import and export
        if e > 1e-6 and s > 1e-6:
            delta = min(e, s)
            # Replace simultaneous flows:
            df_clean.loc[t, "e"] = e - delta
            df_clean.loc[t, "s"] = s - delta
            df_clean.loc[t, "p"] = p + delta
            # Keep load balance consistent: l = p + e (should still hold)
            df_clean.loc[t, "l"] = df_clean.loc[t, "p"] + df_clean.loc[t, "e"]

    return df_clean

def collect_duals_from_problem(problem, T):
    """
    Collect relevant dual series (λ, ρ, κ, etc.) from the solved LP.
    Works for both battery and non-battery cases.
    """
    duals_raw = problem.results.duals
    out = {}

    # Standard structure: constr[0] = mu, next T = λ_t, next T = ρ_t
    out["mu"] = duals_raw.get("constr[0]", None)

    # λ (hourly load balance)
    lambdas = [duals_raw.get(f"constr[{i}]", np.nan) for i in range(1, T+1)]
    out["lambda"] = np.array(lambdas)

    # ρ (PV balance)
    rhos = [duals_raw.get(f"constr[{i}]", np.nan) for i in range(T+1, 2*T+1)]
    out["rho"] = np.array(rhos)

    # --- Additional named duals if present ---
    def try_series(prefix):
        vals = []
        for t in range(T):
            key = f"{prefix}[{t}]"
            if key in duals_raw:
                vals.append(duals_raw[key])
        return np.array(vals) if len(vals) > 0 else None

    out["kappa"] = try_series("soc_dyn")   # battery dynamic duals
    out["omega"] = try_series("soc_cap")   # capacity constraint duals
    out["alpha"] = try_series("pch")       # charge power duals
    out["beta"]  = try_series("pdis")      # discharge power duals

    return out

def collect_duals_by_index(problem, T):
    """Extract structured duals from problem.results.duals by known index positions."""
    all_duals = [problem.results.duals[f"constr[{i}]"] for i in range(len(problem.results.duals))]

    # Convert slices to numpy arrays to enable elementwise operations
    duals = {
        "lambda": np.array(all_duals[0:T]),                # load balance
        "rho": np.array(all_duals[T:2*T]),                 # PV split
        "nu": np.array(all_duals[2*T:3*T]),                # l_max
        "delta": np.array(all_duals[3*T:4*T]),             # load deviation
        "alpha": np.array(all_duals[4*T:5*T]),             # b_ch ≤ Pch_max
        "beta": np.array(all_duals[5*T:6*T]),              # b_dis ≤ Pdis_max
        "kappa": np.array(all_duals[6*T:7*T]),             # SOC dynamics
        "omega_up": np.array(all_duals[7*T:8*T]),          # SOC ≤ cap
        "omega_low": np.array(all_duals[8*T:9*T]),         # SOC ≥ 0
        "sigma": np.array(all_duals[9*T:])                 # final SOC
    }
    return duals

def duals_to_dataframe(duals_dict):
    """
    Convert structured duals (from collect_duals_by_index) into a readable DataFrame
    with 24 columns (one per hour).
    """
    df = pd.DataFrame({name: np.round(values, 4) for name, values in duals_dict.items()
                       if len(values) == len(duals_dict["lambda"])})
    # Transpose so dual types are rows, hours are columns
    df = df.T
    df.columns = [f"h{t}" for t in range(len(df.columns))]
    return df

def decompose_daily_costs(df, price, imp, exp, gamma_up=1.0, gamma_down=1.0):
    """
    Ex-post decompose the daily objective into:
      - cash_cost:      (price+imp)*e  - (price-exp)*s
      - discomfort_cost: gamma_up*price*d+ + gamma_down*price*d-
    df: dataframe of hourly variables (columns: e, s, d+, d-)
    price, imp, exp: arrays length T
    """
    e = df["e"].to_numpy() if "e" in df else 0
    s = df["s"].to_numpy() if "s" in df else 0
    d_up = df["d+"].to_numpy() if "d+" in df else 0
    d_dn = df["d-"].to_numpy() if "d-" in df else 0

    cash_cost = ((price + imp) * e - (price - exp) * s).sum()
    discomfort_cost = (gamma_up * price * d_up + gamma_down * price * d_dn).sum()
    total_objective = cash_cost + discomfort_cost

    return {
        "cash_cost": float(cash_cost),
        "discomfort_cost": float(discomfort_cost),
        "total_objective": float(total_objective),
    }