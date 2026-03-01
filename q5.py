
import tkinter as tk
from tkinter import ttk, messagebox

# -----------------------------
# Sample tourist spots dataset
# -----------------------------
PLACES = [
    {"name": "Pashupatinath Temple", "rating": 9.5, "visit_min": 70},
    {"name": "Swayambhunath (Monkey Temple)", "rating": 9.2, "visit_min": 60},
    {"name": "Boudhanath Stupa", "rating": 9.0, "visit_min": 55},
    {"name": "Patan Durbar Square", "rating": 8.8, "visit_min": 75},
    {"name": "Bhaktapur Durbar Square", "rating": 9.1, "visit_min": 90},
    {"name": "Garden of Dreams", "rating": 8.0, "visit_min": 45},
    {"name": "Thamel Walk", "rating": 7.8, "visit_min": 50},
    {"name": "Nagarkot Viewpoint", "rating": 8.9, "visit_min": 120},
    {"name": "Kopan Monastery", "rating": 8.2, "visit_min": 60},
    {"name": "Chandragiri Hills", "rating": 8.7, "visit_min": 110},
]

# Simple travel-time matrix (minutes) - here we use a simplified model:
# - If same area group -> smaller travel
# - else larger travel
AREA = {
    "Pashupatinath Temple": "East",
    "Boudhanath Stupa": "East",
    "Kopan Monastery": "East",
    "Swayambhunath (Monkey Temple)": "West",
    "Patan Durbar Square": "South",
    "Bhaktapur Durbar Square": "East",
    "Garden of Dreams": "Central",
    "Thamel Walk": "Central",
    "Nagarkot Viewpoint": "Outskirts",
    "Chandragiri Hills": "Outskirts",
}

def travel_time(a, b):
    if a == b:
        return 0
    if AREA.get(a) == AREA.get(b):
        return 15
    # Central is relatively connected
    if AREA.get(a) == "Central" or AREA.get(b) == "Central":
        return 25
    # Outskirts are farther
    if AREA.get(a) == "Outskirts" or AREA.get(b) == "Outskirts":
        return 45
    return 35


# -----------------------------
# Heuristic Planner
# -----------------------------
def plan_itinerary(start_place, time_budget_min, selected_names):
    """
    Greedy heuristic:
    pick next place that maximizes score = rating / (visit_time + travel_time)
    while staying under time budget.
    """
    places = [p for p in PLACES if p["name"] in selected_names]

    # Ensure start exists in selected
    if start_place not in selected_names:
        raise ValueError("Start place must be selected in the list.")

    remaining = {p["name"]: p for p in places}
    itinerary = []

    current = start_place
    total_time = 0

    # Add start place first (no travel to start)
    start_obj = remaining.pop(start_place)
    itinerary.append({"name": start_obj["name"], "travel": 0, "visit": start_obj["visit_min"], "rating": start_obj["rating"]})
    total_time += start_obj["visit_min"]

    while True:
        best_choice = None
        best_score = -1

        for name, p in remaining.items():
            t_travel = travel_time(current, name)
            t_visit = p["visit_min"]
            next_total = total_time + t_travel + t_visit

            if next_total <= time_budget_min:
                score = p["rating"] / (t_travel + t_visit)
                if score > best_score:
                    best_score = score
                    best_choice = (name, t_travel, t_visit, p["rating"])

        if best_choice is None:
            break

        name, t_travel, t_visit, rating = best_choice
        itinerary.append({"name": name, "travel": t_travel, "visit": t_visit, "rating": rating})
        total_time += t_travel + t_visit
        current = name
        remaining.pop(name)

    return itinerary, total_time


# -----------------------------
# GUI
# -----------------------------
class ItineraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tourist Itinerary Planner (Heuristic)")
        self.geometry("1000x600")

        self.selected = tk.StringVar(value=[p["name"] for p in PLACES])

        # Top controls
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Time Budget (minutes):").pack(side="left")
        self.budget_entry = ttk.Entry(top, width=10)
        self.budget_entry.insert(0, "360")  # 6 hours
        self.budget_entry.pack(side="left", padx=8)

        ttk.Label(top, text="Start Location:").pack(side="left", padx=(20, 0))
        self.start_combo = ttk.Combobox(top, values=[p["name"] for p in PLACES], width=35, state="readonly")
        self.start_combo.set("Thamel Walk")
        self.start_combo.pack(side="left", padx=8)

        ttk.Button(top, text="Generate Plan", command=self.on_generate).pack(side="left", padx=10)
        ttk.Button(top, text="Select All", command=self.select_all).pack(side="left")
        ttk.Button(top, text="Clear", command=self.clear_all).pack(side="left", padx=8)

        # Main panels
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # Left: listbox of places
        left = ttk.LabelFrame(main, text="Available Places (Select multiple)", padding=10)
        left.pack(side="left", fill="both", expand=True)

        self.listbox = tk.Listbox(left, listvariable=self.selected, selectmode="multiple", height=20)
        self.listbox.pack(fill="both", expand=True)

        # Preselect all
        self.select_all()

        # Right: output
        right = ttk.LabelFrame(main, text="Generated Itinerary", padding=10)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))

        self.output = tk.Text(right, height=25, wrap="word")
        self.output.pack(fill="both", expand=True)

        self.output.insert("end",
                           "Steps will appear here.\n"
                           "The heuristic chooses the next location with the highest rating/(travel+visit).\n")

    def get_selected_places(self):
        idxs = self.listbox.curselection()
        names = []
        all_names = [p["name"] for p in PLACES]
        for i in idxs:
            names.append(all_names[i])
        return names

    def select_all(self):
        self.listbox.select_set(0, "end")

    def clear_all(self):
        self.listbox.selection_clear(0, "end")

    def on_generate(self):
        try:
            budget = int(self.budget_entry.get())
            if budget <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Time budget must be a positive integer (minutes).")
            return

        start = self.start_combo.get().strip()
        selected_names = self.get_selected_places()

        if len(selected_names) == 0:
            messagebox.showerror("No Selection", "Please select at least one place.")
            return

        if start not in selected_names:
            messagebox.showerror("Start Not Selected", "Start location must be included in selected places.")
            return

        itinerary, total_time = plan_itinerary(start, budget, selected_names)

        total_rating = sum(step["rating"] for step in itinerary)
        self.output.delete("1.0", "end")

        self.output.insert("end", f"Time Budget: {budget} minutes\n")
        self.output.insert("end", f"Start Location: {start}\n")
        self.output.insert("end", "-" * 60 + "\n")

        current = start
        for idx, step in enumerate(itinerary, start=1):
            name = step["name"]
            t_travel = step["travel"]
            t_visit = step["visit"]
            rating = step["rating"]

            self.output.insert("end",
                               f"{idx}. {name}\n"
                               f"   Travel Time: {t_travel} min | Visit Time: {t_visit} min | Rating: {rating}\n")
            current = name

        self.output.insert("end", "-" * 60 + "\n")
        self.output.insert("end", f"Total Time Used: {total_time} minutes\n")
        self.output.insert("end", f"Total Rating Score (sum): {total_rating:.1f}\n")
        self.output.insert("end", "\nNote: This is a greedy heuristic (fast and practical), not guaranteed globally optimal.\n")


if __name__ == "__main__":
    app = ItineraryApp()
    app.mainloop()