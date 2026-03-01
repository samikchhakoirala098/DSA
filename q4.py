
from typing import Dict, List, Tuple

# ---------------------------
# 1) SAMPLE DATASET (Hours 06–15)
# ---------------------------
hours = list(range(6, 16))  # 06 to 15

demand = {
    "A": [20, 22, 24, 28, 30, 26, 25, 27, 29, 31],
    "B": [15, 16, 18, 20, 21, 19, 17, 18, 20, 22],
    "C": [25, 28, 30, 32, 35, 33, 31, 30, 34, 36],
}

sources = [
    {"id": "S1", "type": "Solar",  "cap": 50, "from": 6,  "to": 18, "cost": 1.0},
    {"id": "S2", "type": "Hydro",  "cap": 40, "from": 0,  "to": 24, "cost": 1.5},
    {"id": "S3", "type": "Diesel", "cap": 60, "from": 17, "to": 23, "cost": 3.0},
]

# ---------------------------
# 2) HELPERS
# ---------------------------
def available_sources_for_hour(hour: int) -> List[dict]:
    """Return list of sources available at this hour, sorted by cheapest cost first."""
    avail = [s for s in sources if s["from"] <= hour <= s["to"]]
    return sorted(avail, key=lambda x: x["cost"])  # greedy: cheapest first


def allocate_hour_greedy(hour: int, demands: Dict[str, float], tol: float = 0.10):
    """
    Allocate energy for one hour with:
    - fairness constraint: each district gets between 90% and 110% of its demand
    - greedy: use cheapest source first
    Returns: (feasible, allocation_detail, hour_cost, diesel_used)
    """
    districts = list(demands.keys())

    # Lower and Upper bounds for each district
    low = {d: (1 - tol) * demands[d] for d in districts}
    high = {d: (1 + tol) * demands[d] for d in districts}

    # Sources available this hour
    avail_sources = available_sources_for_hour(hour)
    caps = {s["id"]: float(s["cap"]) for s in avail_sources}

    # First, we must satisfy minimum (low) if possible
    total_min_needed = sum(low.values())
    total_supply_available = sum(caps.values())

    if total_supply_available < total_min_needed:
        # Not enough to satisfy even minimum fairness
        return False, None, 0.0, False

    # We'll build allocations in this structure:
    # alloc[district][source_id] = kWh from that source
    alloc = {d: {s["id"]: 0.0 for s in avail_sources} for d in districts}

    # Step A: allocate MINIMUM (low) for each district using greedy sources
    remaining_need = {d: low[d] for d in districts}

    for s in avail_sources:
        sid = s["id"]
        cap_left = caps[sid]

        # fill districts in some order (A,B,C)
        for d in districts:
            if cap_left <= 0:
                break
            need = remaining_need[d]
            if need <= 0:
                continue

            take = min(need, cap_left)
            alloc[d][sid] += take
            remaining_need[d] -= take
            cap_left -= take

        caps[sid] = cap_left

    # Now all minimums should be met
    if any(remaining_need[d] > 1e-9 for d in districts):
        # theoretically shouldn't happen if total_min_needed feasible
        return False, None, 0.0, False

    # Step B: distribute remaining supply up to HIGH bounds, still greedy cheapest-first
    remaining_extra_cap = {d: high[d] - low[d] for d in districts}

    for s in avail_sources:
        sid = s["id"]
        cap_left = caps[sid]

        for d in districts:
            if cap_left <= 0:
                break
            extra = remaining_extra_cap[d]
            if extra <= 0:
                continue

            take = min(extra, cap_left)
            alloc[d][sid] += take
            remaining_extra_cap[d] -= take
            cap_left -= take

        caps[sid] = cap_left

    # Compute totals + costs
    hour_cost = 0.0
    diesel_used = False

    # total received per district
    received = {}
    for d in districts:
        received[d] = sum(alloc[d].values())

    # Verify fairness bounds
    for d in districts:
        if not (low[d] - 1e-9 <= received[d] <= high[d] + 1e-9):
            return False, None, 0.0, False

    # Cost computation
    cost_map = {s["id"]: s["cost"] for s in avail_sources}
    for d in districts:
        for sid, kwh in alloc[d].items():
            hour_cost += kwh * cost_map[sid]
            if sid == "S3" and kwh > 0:
                diesel_used = True

    return True, {"alloc": alloc, "received": received, "low": low, "high": high}, hour_cost, diesel_used


# ---------------------------
# 3) RUN ALL HOURS + PRINT REPORT
# ---------------------------
total_cost = 0.0
total_energy = 0.0
total_renewable = 0.0  # solar + hydro
diesel_hours = []

print("HOUR | District | Solar | Hydro | Diesel | TotalGiven | Demand | %Fulfilled | Note")
print("-" * 95)

for idx, h in enumerate(hours):
    demands_h = {
        "A": float(demand["A"][idx]),
        "B": float(demand["B"][idx]),
        "C": float(demand["C"][idx]),
    }

    feasible, detail, hour_cost, diesel_used = allocate_hour_greedy(h, demands_h, tol=0.10)

    if not feasible:
        print(f"{h:02d}   | ALL      |  -    |  -    |  -     |   -       |   -   |    -       | INFEASIBLE (min 90% not possible)")
        continue

    total_cost += hour_cost

    # For renewable %: solar + hydro count as renewable here
    for dist in ["A", "B", "C"]:
        solar = detail["alloc"][dist].get("S1", 0.0)
        hydro = detail["alloc"][dist].get("S2", 0.0)
        diesel = detail["alloc"][dist].get("S3", 0.0)

        given = detail["received"][dist]
        dem = demands_h[dist]
        pct = (given / dem) * 100.0

        note = ""
        if diesel > 0:
            note = "Used Diesel"

        print(f"{h:02d}   | {dist}        | {solar:5.1f} | {hydro:5.1f} | {diesel:6.1f} | {given:9.1f} | {dem:6.1f} | {pct:9.1f}% | {note}")

        total_energy += given
        total_renewable += (solar + hydro)

    if diesel_used:
        diesel_hours.append(h)

print("-" * 95)
renew_pct = (total_renewable / total_energy * 100.0) if total_energy > 0 else 0.0

print(f"TOTAL COST (Rs.): {total_cost:.2f}")
print(f"Renewable Energy % (Solar+Hydro): {renew_pct:.2f}%")
print(f"Diesel used in hours: {diesel_hours if diesel_hours else 'None (in 06-15 dataset)'}")