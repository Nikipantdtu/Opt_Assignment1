import pandas as pd
import matplotlib.pyplot as plt

def plot_hourly_flows_with_prices(df, scenario_name, duals=None,
                                  price=None, alpha=None, beta=None, ylim=(0,3)):
    rename = {
        "l": "Load",
        "p": "PV self-consumed",
        "e": "Grid imports",
        "s": "PV exported",
        "c": "PV curtailed",
    }
    df_named = df.rename(columns=rename)

    # Compute total PV generation
    df_named["PV generation"] = (
        df_named["PV self-consumed"] 
        + df_named["PV exported"] 
        + df_named["PV curtailed"]
    )

    hours = df_named.index
    width = 0.25
    bar_alpha = 0.85

    plt.rcParams.update({
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    })

    fig, ax1 = plt.subplots(figsize=(14,6))

    # --- Group 1: PV generation (stacked) ---
    ax1.bar(hours - width, df_named["PV self-consumed"], width,
            label="PV self-consumed", color="gold", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV exported"], width,
            bottom=df_named["PV self-consumed"], label="PV exported",
            color="forestgreen", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV curtailed"], width,
            bottom=df_named["PV self-consumed"]+df_named["PV exported"],
            label="PV curtailed", color="lightgray", alpha=bar_alpha)

    # --- PV frame (outline for total generation) ---
    ax1.bar(hours - width, df_named["PV generation"], width,
            fill=False, edgecolor="black", linewidth=0.5,
            label="Total PV generation")

    # --- Group 2: Load (center) ---
    ax1.bar(hours, df_named["Load"], width,
            label="Load", color="royalblue", alpha=bar_alpha)

    # --- Group 3: Imports (right) ---
    ax1.bar(hours + width, df_named["Grid imports"], width,
            label="Grid imports", color="firebrick", alpha=bar_alpha)

    # --- Axis formatting ---
    ax1.set_title(f"Energy flows and prices – {scenario_name}")
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("Energy (kWh)")
    ax1.set_ylim(ylim)
    ax1.set_xlim(-0.5, len(hours)-0.5)
    ax1.set_xticks(range(len(hours)))
    ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

    # --- Second axis: prices ---
    if duals is not None:
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)   # flip sign for internal price
        ax2.plot(hours, p_int, marker="x", linestyle="--",
                 color="purple", linewidth=2, label="Internal price (−λ)")

        if price is not None:
            ax2.plot(hours, price, marker="o", linestyle=":",
                     color="dimgray", linewidth=2, label="Market price π")
        if alpha is not None:
            ax2.plot(hours, alpha, linestyle="--",
                     color="red", linewidth=2, label="Import cost α")
        if beta is not None:
            ax2.plot(hours, beta, linestyle="-.",
                     color="green", linewidth=2, label="Export value β")

        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")

        # Merge legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labels1+labels2,
                   loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)
    else:
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)

    plt.tight_layout()
    plt.show()


def plot_scenarios_subplots_1a(scenario_results, titles, price_list, alpha_list, beta_list, duals_list):
    """
    scenario_results: list of DataFrames (from results_to_dataframe)
    titles:           list of scenario names
    price_list, alpha_list, beta_list: lists of arrays with price, alpha, beta per scenario
    duals_list:       list of duals arrays (λ_t) per scenario
    """

    fig, axes = plt.subplots(
        nrows=len(scenario_results), ncols=1,
        figsize=(14, 4*len(scenario_results)), sharex=True
    )

    if len(scenario_results) == 1:
        axes = [axes]  # ensure iterable

    for ax1, df, title, price, alpha, beta, duals in zip(
        axes, scenario_results, titles, price_list, alpha_list, beta_list, duals_list):

        # --- Rename and compute ---
        df_named = df.rename(columns={
            "l": "Load",
            "p": "PV self-consumed",
            "e": "Grid imports",
            "s": "PV exported",
            "c": "PV curtailed",
        })
        df_named["PV generation"] = (
            df_named["PV self-consumed"]
            + df_named["PV exported"]
            + df_named["PV curtailed"]
        )

        hours = df_named.index
        width = 0.25
        bar_alpha = 0.85

        # --- PV generation bars ---
        ax1.bar(hours - width, df_named["PV self-consumed"], width,
                label="PV self-consumed", color="gold", alpha=bar_alpha)
        ax1.bar(hours - width, df_named["PV exported"], width,
                bottom=df_named["PV self-consumed"], label="PV exported", color="forestgreen", alpha=bar_alpha)
        ax1.bar(hours - width, df_named["PV curtailed"], width,
                bottom=df_named["PV self-consumed"]+df_named["PV exported"], label="PV curtailed", color="lightgray", alpha=bar_alpha)
        ax1.bar(hours - width, df_named["PV generation"], width,
                fill=False, edgecolor="black", linewidth=0.5, label="Total PV generation")

        # --- Load ---
        ax1.bar(hours, df_named["Load"], width, label="Load", color="royalblue", alpha=bar_alpha)

        # --- Imports ---
        ax1.bar(hours + width, df_named["Grid imports"], width, label="Grid imports", color="firebrick", alpha=bar_alpha)

        ax1.set_title(title)
        ax1.set_ylabel("Energy (kWh)")

        # --- Axis limits depending on scenario ---
        if "Net metering" in title:
            ax1.set_ylim(0, 3.5)
        else:
            ax1.set_ylim(0, 3.5)

        # --- Force hourly ticks and labels on all subplots ---
        ax1.set_xticks(range(len(hours)))
        ax1.set_xticklabels(range(len(hours)))
        ax1.tick_params(labelbottom=True)

        # Only bottom subplot gets the xlabel
        if ax1 == axes[-1]:
            ax1.set_xlabel("Hour of day")

        ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

        # --- Prices (secondary axis) ---
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)   # flip sign
        ax2.plot(hours, p_int, marker="x", linestyle="--", color="purple", linewidth=2, label="Internal price (λ)")
        ax2.plot(hours, price, marker="o", linestyle=":", color="dimgray", linewidth=2, label="Market price π")
        ax2.plot(hours, alpha, linestyle="--", color="red", linewidth=2, label="Import cost α")
        ax2.plot(hours, beta, linestyle="-.", color="green", linewidth=2, label="Export value β")
        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")

        # Fix price axis limits for consistency
        ax2.set_ylim(0, 3)

        # Save reference for legend collection
        ax1.right_ax = ax2

    # --- Shared legend without creating duplicate axis ---
    handles1, labels1 = axes[0].get_legend_handles_labels()
    handles2, labels2 = axes[0].right_ax.get_legend_handles_labels()

    fig.legend(handles1+handles2, labels1+labels2,
               loc="lower center", bbox_to_anchor=(0.5, 0.01),
               ncol=5, frameon=False)

    plt.tight_layout(rect=[0, 0.05, 1, 1])  # leave space for legend
    plt.show()


def plot_hourly_flows_with_prices_1b(df, scenario_name, duals=None,
                                  price=None, alpha=None, beta=None, L_ref=None, # NEW: Add L_ref
                                  ylim=(0,3)):
    rename = {
        "l": "Load",
        "p": "PV self-consumed",
        "e": "Grid imports",
        "s": "PV exported",
        "c": "PV curtailed",
        "d+": "Upward deviation",
        "d-": "Downward deviation",
    }
    df_named = df.rename(columns=rename)

    # Compute total PV generation
    df_named["PV generation"] = (
        df_named["PV self-consumed"] 
        + df_named["PV exported"] 
        + df_named["PV curtailed"]
    )

    hours = df_named.index
    width = 0.25
    bar_alpha = 0.85

    plt.rcParams.update({
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    })

    fig, ax1 = plt.subplots(figsize=(14,6))

    # --- Group 1: PV generation (stacked) ---
    ax1.bar(hours - width, df_named["PV self-consumed"], width,
            label="PV self-consumed", color="gold", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV exported"], width,
            bottom=df_named["PV self-consumed"], label="PV exported",
            color="forestgreen", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV curtailed"], width,
            bottom=df_named["PV self-consumed"]+df_named["PV exported"],
            label="PV curtailed", color="lightgray", alpha=bar_alpha)

    # --- PV frame (outline for total generation) ---
    ax1.bar(hours - width, df_named["PV generation"], width,
            fill=False, edgecolor="black", linewidth=0.5,
            label="Total PV generation")

    # --- Group 2: Load (center) ---
    ax1.bar(hours, df_named["Load"], width,
            label="Load", color="royalblue", alpha=bar_alpha)

    # --- Group 3: Imports (right) ---
    ax1.bar(hours + width, df_named["Grid imports"], width,
            label="Grid imports", color="firebrick", alpha=bar_alpha)
    
    # --- Group 4: Deviations (stacked on top of Load) ---
    ax1.bar(hours, df_named["Upward deviation"], width,
            bottom=df_named["Load"], label="Upward deviation", color="cyan", alpha=bar_alpha)
    ax1.bar(hours, df_named["Downward deviation"], width,
            bottom=df_named["Load"] + df_named["Upward deviation"], label="Downward deviation",
            color="magenta", alpha=bar_alpha)
    
    # --- Plot reference load as a line ---
    if L_ref is not None:
        ax1.plot(hours, L_ref, color='darkorange', linestyle='-', drawstyle='steps-mid',
         linewidth=2.5, label='Reference Load')

    # --- Axis formatting ---
    ax1.set_title(f"Energy flows and prices – {scenario_name}")
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("Energy (kWh)")
    ax1.set_ylim(ylim)
    ax1.set_xlim(-0.5, len(hours)-0.5)
    ax1.set_xticks(range(len(hours)))
    ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

    # --- Second axis: prices ---
    if duals is not None:
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)   # flip sign for internal price
        ax2.plot(hours, p_int, marker="x", linestyle="--",
                 color="purple", linewidth=2, label="Internal price (−λ)")

        if price is not None:
            ax2.plot(hours, price, marker="o", linestyle=":",
                     color="dimgray", linewidth=2, label="Market price π")
        """
        if alpha is not None:
            ax2.plot(hours, alpha, linestyle="--",
                     color="red", linewidth=2, label="Import cost α")
        if beta is not None:
            ax2.plot(hours, beta, linestyle="-.",
                     color="green", linewidth=2, label="Export value β")
        """

        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")

        # Merge legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labels1+labels2,
                   loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)
    else:
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)

    plt.tight_layout()
    plt.show()

def plot_sensitivity_analysis_1b(sensitivity_df):
    """Plots the results of the kappa sensitivity analysis."""
    
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # --- AXIS 1: Total Cost ---
    ax1.plot(sensitivity_df.index, sensitivity_df["Objective"], 
             color="blue", marker="o", label="Total Cost (Objective)")
    ax1.set_xlabel("Discomfort Factor (κ)")
    ax1.set_ylabel("Total Cost (DKK)", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

    # --- AXIS 2: Energy Volumes ---
    ax2 = ax1.twinx()
    ax2.plot(sensitivity_df.index, sensitivity_df["Total Deviation"], 
             color="red", marker="x", linestyle="--", label="Total Deviation (kWh)")
    ax2.plot(sensitivity_df.index, sensitivity_df["Total Imports"], 
             color="purple", marker="s", linestyle=":", label="Total Imports (kWh)")
    ax2.set_ylabel("Energy (kWh)", color="black")
    ax2.tick_params(axis='y', labelcolor="black")
    
    fig.suptitle("Sensitivity Analysis of Discomfort Factor (κ)", fontsize=16)
    
    # Merge legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="best")
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def plot_scenarios_subplots_1b(
    scenario_results, titles, price_list, alpha_list, beta_list,
    duals_list, L_ref_list=None, ylim=(0,6.5)
):
    """
    Create vertically stacked subplots for all scenarios (no battery).
    """

    n_scen = len(scenario_results)
    fig, axes = plt.subplots(nrows=n_scen, ncols=1,
                             figsize=(14, 4*n_scen), sharex=True)

    if n_scen == 1:
        axes = [axes]

    for ax1, df, title, price, alpha, beta, duals, L_ref in zip(
        axes, scenario_results, titles, price_list, alpha_list, beta_list, duals_list,
        L_ref_list or [None]*n_scen):

        rename = {
            "l": "Load",
            "p": "PV to bus",
            "e": "Grid imports",
            "s": "PV exported",
            "c": "PV curtailed",
            "d+": "Upward deviation",
            "d-": "Downward deviation"
        }
        df_named = df.rename(columns=rename)

        # --- Derived values ---
        df_named["PV generation"] = (
            df_named.get("PV to bus", 0)
            + df_named.get("PV exported", 0)
            + df_named.get("PV curtailed", 0)
        )

        hours = df_named.index
        width = 0.25
        bar_alpha = 0.85

        # --- PV generation group (left bars) ---
        ax1.bar(hours - width, df_named.get("PV to bus", 0), width,
                label="PV to bus", color="gold", alpha=bar_alpha)
        ax1.bar(hours - width, df_named.get("PV exported", 0), width,
                bottom=df_named.get("PV to bus", 0),
                label="PV exported", color="forestgreen", alpha=bar_alpha)
        ax1.bar(hours - width, df_named.get("PV curtailed", 0), width,
                bottom=df_named.get("PV to bus", 0) + df_named.get("PV exported", 0),
                label="PV curtailed", color="lightgray", alpha=bar_alpha)
        ax1.bar(hours - width, df_named["PV generation"], width,
                fill=False, edgecolor="black", linewidth=0.5,
                label="Total PV generation")

        # --- Load + deviations (center bars) ---
        base_load = df_named.get("Load", 0)
        ax1.bar(hours, base_load, width,
                label="Load", color="royalblue", alpha=bar_alpha)

        ax1.bar(hours, df_named.get("Upward deviation", 0), width,
                bottom=base_load, label="Upward deviation", color="mediumvioletred", alpha=bar_alpha)
        ax1.bar(hours, df_named.get("Downward deviation", 0), width,
                bottom=base_load + df_named.get("Upward deviation", 0),
                label="Downward deviation", color="magenta", alpha=bar_alpha)

        # --- Imports (right bars) ---
        base_imports = df_named.get("Grid imports", 0)
        ax1.bar(hours + width, base_imports, width,
                label="Grid imports", color="firebrick", alpha=bar_alpha)

        # --- Optional: Reference load line ---
        if L_ref is not None:
            ax1.plot(hours, L_ref, color='darkorange', linestyle='-', drawstyle='steps-mid',
                     linewidth=2.5, label='Reference Load')

        # --- Formatting ---
        ax1.set_title(title)
        ax1.set_ylabel("Energy (kWh)")
        ax1.set_ylim(ylim)
        ax1.set_xlim(-0.5, len(hours)-0.5)
        ax1.set_xticks(range(len(hours)))
        ax1.set_xticklabels(range(len(hours)))
        ax1.tick_params(labelbottom=True)
        if ax1 == axes[-1]:
            ax1.set_xlabel("Hour of day")

        ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

        # --- Prices (right axis) ---
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)
        ax2.plot(hours, p_int, marker="x", linestyle="--",
                 color="purple", linewidth=2, label="Internal price (λ)")
        ax2.plot(hours, price, marker="o", linestyle=":",
                 color="dimgray", linewidth=2, label="Market price π")
        ax2.plot(hours, alpha, linestyle="--",
                 color="red", linewidth=2, label="Import cost α")
        ax2.plot(hours, beta, linestyle="-.",
                 color="green", linewidth=2, label="Export value β")
        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")
        ax2.set_ylim(0, 6)

        ax1.right_ax = ax2

    # --- Shared legend ---
    handles1, labels1 = axes[0].get_legend_handles_labels()
    handles2, labels2 = axes[0].right_ax.get_legend_handles_labels()
    fig.legend(handles1+handles2, labels1+labels2,
               loc="lower center", bbox_to_anchor=(0.5, -0.0125),
               ncol=5, frameon=False)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()

def plot_hourly_flows_with_prices_1c(df, scenario_name, duals=None,
                                  price=None, alpha=None, beta=None, L_ref=None, # NEW: Add L_ref
                                  ylim=(0,6.5),
                                  show_battery=True):
    rename = {
        "l": "Load",
        "p": "PV to bus",
        "e": "Grid imports",
        "s": "PV exported",
        "c": "PV curtailed",
        "d+": "Upward deviation",
        "d-": "Downward deviation",
        "b_ch": "Battery charge",
        "b_dis": "Battery discharge",
        "soc": "Battery SOC"
    }
    df_named = df.rename(columns=rename)

    # Compute total PV generation
    df_named["PV generation"] = (
        df_named.get("PV to bus", 0)
        + df_named.get("PV exported", 0)
        + df_named.get("PV curtailed", 0)
    )

    hours = df_named.index
    width = 0.25
    bar_alpha = 0.85

    plt.rcParams.update({
        "font.size": 14,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
    })

    fig, ax1 = plt.subplots(figsize=(14,6))

    # --- Group 1: PV generation (stacked) ---
    ax1.bar(hours - width, df_named["PV to bus"], width,
            label="PV to bus", color="gold", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV exported"], width,
            bottom=df_named["PV to bus"], label="PV exported",
            color="forestgreen", alpha=bar_alpha)
    ax1.bar(hours - width, df_named["PV curtailed"], width,
            bottom=df_named["PV to bus"]+df_named["PV exported"],
            label="PV curtailed", color="lightgray", alpha=bar_alpha)

    # --- PV frame (outline for total generation) ---
    ax1.bar(hours - width, df_named["PV generation"], width,
            fill=False, edgecolor="black", linewidth=0.5,
            label="Total PV generation")

    # --- Group 2: Load with deviations and battery charge stacked on top ---
    base_load = df_named["Load"]
    ax1.bar(hours, base_load, width,
            label="Load", color="royalblue", alpha=bar_alpha)
    
    # Stack upward deviation on top of load
    ax1.bar(hours, df_named.get("Upward deviation", 0), width,
            bottom=base_load, label="Upward deviation", color="cyan", alpha=bar_alpha)
    
    # Stack downward deviation on top of load + upward deviation
    ax1.bar(hours, df_named.get("Downward deviation", 0), width,
            bottom=base_load + df_named.get("Upward deviation", 0), 
            label="Downward deviation", color="magenta", alpha=bar_alpha)
    
    # Stack battery charge on top of everything else in the load bar
    total_deviations = df_named.get("Upward deviation", 0) + df_named.get("Downward deviation", 0)
    ax1.bar(hours, df_named.get("Battery charge", 0), width,
            bottom=base_load + total_deviations,
            label="Battery charge", color="deepskyblue", alpha=bar_alpha)

    # --- Group 3: Imports with battery discharge stacked on top ---
    base_imports = df_named["Grid imports"]
    ax1.bar(hours + width, base_imports, width,
            label="Grid imports", color="firebrick", alpha=bar_alpha)
    
    # Stack battery discharge on top of imports
    ax1.bar(hours + width, df_named.get("Battery discharge", 0), width,
            bottom=base_imports, label="Battery discharge", color="orange", alpha=bar_alpha)
    
    # --- Plot reference load as a line ---
    if L_ref is not None:
        ax1.plot(hours, L_ref, color='darkorange', linestyle='-', drawstyle='steps-mid',
         linewidth=2.5, label='Reference Load')

    # --- Battery SOC line (only if showing battery) ---
    if show_battery and "Battery SOC" in df_named.columns:
        ax1.plot(hours, df_named["Battery SOC"], color="black", linestyle="--", 
                 linewidth=2, label="Battery SOC (kWh)")

    # --- Axis formatting ---
    ax1.set_title(f"Energy flows and prices – {scenario_name}")
    ax1.set_xlabel("Hour of day")
    ax1.set_ylabel("Energy (kWh)")
    ax1.set_ylim(ylim)
    ax1.set_xlim(-0.5, len(hours)-0.5)
    ax1.set_xticks(range(len(hours)))
    ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

    # --- Second axis: prices ---
    if duals is not None:
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)   # flip sign for internal price
        ax2.plot(hours, p_int, marker="x", linestyle="--",
                 color="purple", linewidth=2, label="Internal price (−λ)")

        if price is not None:
            ax2.plot(hours, price, marker="o", linestyle=":",
                     color="dimgray", linewidth=2, label="Market price π")
        """
        if alpha is not None:
            ax2.plot(hours, alpha, linestyle="--",
                     color="red", linewidth=2, label="Import cost α")
        if beta is not None:
            ax2.plot(hours, beta, linestyle="-.",
                     color="green", linewidth=2, label="Export value β")
        """

        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")

        # Merge legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1+lines2, labels1+labels2,
                   loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)
    else:
        ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18),
                   ncol=5, frameon=False)

    plt.tight_layout()
    plt.show()


def plot_scenarios_subplots_1c(
    scenario_results, titles, price_list, alpha_list, beta_list,
    duals_list, L_ref_list=None, ylim=(0,6.5)
):
    """
    Create vertically stacked subplots for all scenarios, including battery behavior.
    """

    n_scen = len(scenario_results)
    fig, axes = plt.subplots(nrows=n_scen, ncols=1,
                             figsize=(14, 4*n_scen), sharex=True)

    if n_scen == 1:
        axes = [axes]

    for ax1, df, title, price, alpha, beta, duals, L_ref in zip(
        axes, scenario_results, titles, price_list, alpha_list, beta_list, duals_list,
        L_ref_list or [None]*n_scen):

        rename = {
            "l": "Load",
            "p": "PV to bus",
            "e": "Grid imports",
            "s": "PV exported",
            "c": "PV curtailed",
            "d+": "Upward deviation",
            "d-": "Downward deviation",
            "b_ch": "Battery charge",
            "b_dis": "Battery discharge",
            "soc": "Battery SOC"
        }
        df_named = df.rename(columns=rename)

        # --- Derived values ---
        df_named["PV generation"] = (
            df_named.get("PV to bus", 0)
            + df_named.get("PV exported", 0)
            + df_named.get("PV curtailed", 0)
        )

        hours = df_named.index
        width = 0.25
        bar_alpha = 0.85

        # --- PV generation group (left bars) ---
        ax1.bar(hours - width, df_named.get("PV to bus", 0), width,
                label="PV to bus", color="gold", alpha=bar_alpha)
        ax1.bar(hours - width, df_named.get("PV exported", 0), width,
                bottom=df_named.get("PV to bus", 0),
                label="PV exported", color="forestgreen", alpha=bar_alpha)
        ax1.bar(hours - width, df_named.get("PV curtailed", 0), width,
                bottom=df_named.get("PV to bus", 0) + df_named.get("PV exported", 0),
                label="PV curtailed", color="lightgray", alpha=bar_alpha)
        ax1.bar(hours - width, df_named["PV generation"], width,
                fill=False, edgecolor="black", linewidth=0.5,
                label="Total PV generation")

        # --- Load + deviations + battery charge (center bars) ---
        base_load = df_named.get("Load", 0)
        ax1.bar(hours, base_load, width,
                label="Load", color="royalblue", alpha=bar_alpha)

        ax1.bar(hours, df_named.get("Upward deviation", 0), width,
                bottom=base_load, label="Upward deviation", color="mediumvioletred", alpha=bar_alpha)
        ax1.bar(hours, df_named.get("Downward deviation", 0), width,
                bottom=base_load + df_named.get("Upward deviation", 0),
                label="Downward deviation", color="magenta", alpha=bar_alpha)
        total_dev = df_named.get("Upward deviation", 0) + df_named.get("Downward deviation", 0)
        ax1.bar(hours, df_named.get("Battery charge", 0), width,
                bottom=base_load + total_dev,
                label="Battery charge", color="deepskyblue", alpha=bar_alpha)

        # --- Imports + battery discharge (right bars) ---
        base_imports = df_named.get("Grid imports", 0)
        ax1.bar(hours + width, base_imports, width,
                label="Grid imports", color="firebrick", alpha=bar_alpha)
        ax1.bar(hours + width, df_named.get("Battery discharge", 0), width,
                bottom=base_imports,
                label="Battery discharge", color="orange", alpha=bar_alpha)

        # --- Optional: Reference load line ---
        if L_ref is not None:
            ax1.plot(hours, L_ref, color='darkorange', linestyle='-', drawstyle='steps-mid',
                     linewidth=2.5, label='Reference Load')

        # --- Optional: Battery SOC line ---
        if "Battery SOC" in df_named.columns:
            ax1.plot(hours, df_named["Battery SOC"], color="black", linestyle="--",
                     linewidth=2, label="Battery SOC (kWh)")

        # --- Formatting ---
        ax1.set_title(title)
        ax1.set_ylabel("Energy (kWh)")
        ax1.set_ylim(ylim)
        ax1.set_xlim(-0.5, len(hours)-0.5)
        ax1.set_xticks(range(len(hours)))
        ax1.set_xticklabels(range(len(hours)))
        ax1.tick_params(labelbottom=True)
        if ax1 == axes[-1]:
            ax1.set_xlabel("Hour of day")

        ax1.grid(True, which="both", axis="y", linestyle="--", alpha=0.6)

        # --- Prices (right axis) ---
        ax2 = ax1.twinx()
        p_int = -pd.Series(duals, index=hours)
        ax2.plot(hours, p_int, marker="x", linestyle="--",
                 color="purple", linewidth=2, label="Internal price (λ)")
        ax2.plot(hours, price, marker="o", linestyle=":",
                 color="dimgray", linewidth=2, label="Market price π")
        ax2.plot(hours, alpha, linestyle="--",
                 color="red", linewidth=2, label="Import cost α")
        ax2.plot(hours, beta, linestyle="-.",
                 color="green", linewidth=2, label="Export value β")
        ax2.set_ylabel("Price (DKK/kWh)")
        ax2.tick_params(axis='y', labelcolor="black")
        ax2.set_ylim(0, 6)

        ax1.right_ax = ax2

    # --- Shared legend ---
    handles1, labels1 = axes[0].get_legend_handles_labels()
    handles2, labels2 = axes[0].right_ax.get_legend_handles_labels()
    fig.legend(handles1+handles2, labels1+labels2,
               loc="lower center", bbox_to_anchor=(0.5, -0.0125),
               ncol=5, frameon=False)
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()