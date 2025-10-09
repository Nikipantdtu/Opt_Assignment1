import json 
import numpy as np

def load_inputs(data_dir):
    with open(data_dir / "appliance_params.json") as f:
        appliance_params = json.load(f)
    with open(data_dir / "bus_params.json") as f:
        bus_params = json.load(f)[0]
    with open(data_dir / "consumer_params.json") as f:
        consumer_params = json.load(f)[0]
    with open(data_dir / "DER_production.json") as f:
        der_prod = json.load(f)[0]
    with open(data_dir / "usage_preferences.json") as f:
        usage_pref = json.load(f)[0]
    return appliance_params, bus_params, consumer_params, der_prod, usage_pref

def make_scenarios(base):
    scenarios = {}
    # Base
    scenarios["Base"] = dict(price=base["price"], imp=base["imp_tariff"], exp=base["exp_tariff"])
    # Constant price
    scenarios["Const price"] = dict(price=np.full(base["T"], base["price"].mean()),
                                    imp=base["imp_tariff"], exp=base["exp_tariff"])
    # Net metering
    scenarios["Net metering"] = dict(price=base["price"], imp=np.zeros(base["T"]), exp=np.zeros(base["T"]))
    # No profitable export
    scenarios["No export"] = dict(price=base["price"], imp=base["imp_tariff"],
                                  exp=base["price"]+0.01)
    # Evening spike
    spike = base["price"].copy()
    spike[18:22] *= 2.0
    scenarios["Spike"] = dict(price=spike, imp=base["imp_tariff"], exp=base["exp_tariff"])
    return scenarios

def prepare_base_inputs(appliance_params, bus_params, der_prod, usage_pref, task="a"):
    T = len(bus_params["energy_price_DKK_per_kWh"])
    price = np.array(bus_params["energy_price_DKK_per_kWh"])
    imp_tariff = np.full(T, bus_params["import_tariff_DKK/kWh"])
    exp_tariff = np.full(T, bus_params["export_tariff_DKK/kWh"])

    pv_power = next(d["max_power_kW"] for d in appliance_params["DER"] if d["DER_type"] == "PV")
    pv_profile = np.array(der_prod["hourly_profile_ratio"])
    P_pv = pv_power * pv_profile

    load_prefs = usage_pref["load_preferences"][0]
    l_max = appliance_params["load"][0]["max_load_kWh_per_hour"]

    # ensure we have an array of hourly max values
    if np.isscalar(l_max):
        l_max_hour = np.full(T, l_max)
    else:
        l_max_hour = np.array(l_max)
    
    if task=="a":
        L_min = load_prefs["min_total_energy_per_day_hour_equivalent"] * l_max

        return dict(T=T, price=price, imp_tariff=imp_tariff, exp_tariff=exp_tariff,
                    P_pv=P_pv, L_min=L_min, l_max_hour=l_max_hour)
    elif task=="b":
        l_max_hour = next(l["max_load_kWh_per_hour"] for l in appliance_params["load"])
        # MODIFIED for b): Calculate L_ref by multiplying the hourly ratio by the max hourly load
        load_prefs = usage_pref["load_preferences"][0]
        hourly_ratios = np.array(load_prefs["hourly_profile_ratio"])
        L_ref = hourly_ratios * l_max_hour

        return dict(T=T, price=price, imp_tariff=imp_tariff, exp_tariff=exp_tariff,
                P_pv=P_pv, l_max_hour=l_max_hour, L_ref=L_ref)
    else: # c and 2b
        # Load parameters
        l_max_hour = next(l["max_load_kWh_per_hour"] for l in appliance_params["load"])
        
        # Calculate L_ref by multiplying the hourly ratio by the max hourly load
        load_prefs = usage_pref["load_preferences"][0]
        hourly_ratios = np.array(load_prefs["hourly_profile_ratio"])
        L_ref = hourly_ratios * l_max_hour
        
        # Battery storage parameters for Task 1c
        battery_params = {}
        if appliance_params["storage"] is not None:
            storage = appliance_params["storage"][0]  # Assume first storage device
            battery_params = {
                "capacity_kWh": storage["storage_capacity_kWh"],
                "max_charge_power_kW": storage["storage_capacity_kWh"] * storage["max_charging_power_ratio"],
                "max_discharge_power_kW": storage["storage_capacity_kWh"] * storage["max_discharging_power_ratio"],
                "charge_efficiency": storage["charging_efficiency"],
                "discharge_efficiency": storage["discharging_efficiency"]
            }
            
            # Battery preferences (initial and final SOC)
            storage_prefs = usage_pref["storage_preferences"][0]
            battery_params.update({
                "initial_soc_ratio": storage_prefs["initial_soc_ratio"],
                "final_soc_ratio": storage_prefs["final_soc_ratio"]
            })
        
        return dict(T=T, price=price, imp_tariff=imp_tariff, exp_tariff=exp_tariff,
                    P_pv=P_pv, l_max_hour=l_max_hour, L_ref=L_ref, 
                    battery_params=battery_params)