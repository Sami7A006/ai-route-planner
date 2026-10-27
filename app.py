"""Optional Streamlit UI:  pip install streamlit  &&  streamlit run app.py"""
from pathlib import Path

import pandas as pd
import streamlit as st

from routeai import Profile, load_places, plan_trip
from routeai.models import hhmm_to_min, min_to_hhmm

places = load_places(Path(__file__).parent / "data" / "places.json")
cats = sorted({p.category for p in places})

st.title("AI Tourist Route Planner")
st.caption("A* search + rule-based expert system + simulated annealing. No machine learning.")

with st.sidebar:
    interests = st.multiselect("Interests", cats, default=["heritage", "food"])
    group = st.selectbox("Group", ["solo", "couple", "family", "friends"])
    kids = st.checkbox("Travelling with kids")
    senior = st.checkbox("Senior travellers")
    level = st.selectbox("Budget level", ["low", "medium", "high"], index=1)
    days = st.slider("Days", 1, 5, 1)
    budget = st.number_input("Total budget (INR)", 500, 100000, 3000, step=500)
    mode = st.selectbox("Transport", ["cab", "auto", "bike", "walk"])
    t0 = st.text_input("Day start", "09:00")
    t1 = st.text_input("Day end", "20:00")
    must = st.multiselect("Must visit", [p.id for p in places])
    avoid = st.multiselect("Avoid", [p.id for p in places])
    go = st.button("Plan my trip", type="primary")

if go:
    profile = Profile(interests, group, kids, senior, level, must, avoid)
    plans = plan_trip(places, profile, {"name": "Hotel", "lat": 17.3894, "lon": 78.4740},
                      days=days, day_start=hhmm_to_min(t0), day_end=hhmm_to_min(t1),
                      budget=budget, mode=mode)
    for i, plan in enumerate(plans, 1):
        st.subheader(f"Day {i} - Rs.{plan.spent:.0f}, {plan.travel_km:.1f} km")
        if not plan.stops:
            st.write("Nothing feasible.")
            continue
        st.dataframe(pd.DataFrame([{
            "Time": f"{min_to_hhmm(s.start)}-{min_to_hhmm(s.depart)}",
            "Place": s.place.name, "Category": s.place.category,
            "Cost": s.place.cost, "Why": "; ".join(s.reasons)} for s in plan.stops]),
            use_container_width=True)
        st.map(pd.DataFrame([{"lat": s.place.lat, "lon": s.place.lon} for s in plan.stops]))
