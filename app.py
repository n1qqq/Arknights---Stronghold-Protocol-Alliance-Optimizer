import streamlit as st
from scaffold import Character
from data import chara_pool
from ortools.sat.python import cp_model

# --- UI Header ---
st.title("Arknights: Stronghold Protocol Alliance II Optimizer")
st.markdown("Calculate the theoretical maximum faction light-ups for your squad!")

# --- User Input ---
# This creates a searchable dropdown for users to select who they DO NOT have/want
all_charas = list(chara_pool.keys())
ban_list = st.multiselect(
    "Select Operators to BAN (e.g., they are unavailable or you don't want to keep them in final line-ups):",
    options=all_charas,
    default=[] # set default bans here
)

# --- Data Cleaning ---
# Create a fresh copy of the pool for this specific run
current_pool = {name: chara for name, chara in chara_pool.items() if name not in ban_list}

# --- Core Function ---
TAGS = Character.TAGS
TAGS_DEF = Character.TAGS_DEF

MAJOR_FACTIONS = TAGS_DEF[:8]
ALLOWED_EXTRA_MINOR = TAGS_DEF[8:14]
ALLOWED_EXTRA_TAGS = MAJOR_FACTIONS + ALLOWED_EXTRA_MINOR

MINOR_FACTIONS = TAGS_DEF[8:17]
SPECIAL_MINOR = TAGS_DEF[17]
SOLO_FACTION = TAGS_DEF[18]

def solve_stronghold(chara_pool, max_deployment=9):
    model = cp_model.CpModel()

    # --- 1. Variables ---
    is_deployed = {name: model.NewBoolVar(f"deploy_{name}") for name in chara_pool}

    # extra_tag[name][tag]: 1 if character 'name' equips extra 'tag'
    extra_tag = {}
    for name in chara_pool:
        extra_tag[name] = {tag: model.NewBoolVar(f"extra_{name}_{tag}") for tag in ALLOWED_EXTRA_TAGS}

    tag_count = {tag_name: model.NewIntVar(0, max_deployment * 2, f"count_{tag_name}") for tag_name in TAGS_DEF}
    tag_active = {tag_name: model.NewBoolVar(f"active_{tag_name}") for tag_name in TAGS_DEF}

    # --- 2. Constraints ---
    model.Add(sum(is_deployed.values()) <= max_deployment)

    for name in chara_pool:
        # Each deployed character can have AT MOST one extra tag
        model.Add(sum(extra_tag[name].values()) <= is_deployed[name])
        # A character cannot pick a duplicating tag when they already possess it
        for t_name in ALLOWED_EXTRA_TAGS:
            if chara_pool[name].has_tag(TAGS[t_name]):
                model.Add(extra_tag[name][t_name] == 0)

    # Calculate total tag counts
    for tag_name in TAGS_DEF:
        innate_contrib = []
        extra_contrib = []

        for name, chara in chara_pool.items():
            if chara.has_tag(TAGS[tag_name]):
                innate_contrib.append(is_deployed[name])
            if tag_name in ALLOWED_EXTRA_TAGS:
                extra_contrib.append(extra_tag[name][tag_name])

        model.Add(tag_count[tag_name] == sum(innate_contrib) + sum(extra_contrib))

    # Activation Logic
    for tag_name in TAGS_DEF:
        if tag_name in MAJOR_FACTIONS:
            # Major: >= 3
            model.Add(tag_count[tag_name] >= 3).OnlyEnforceIf(tag_active[tag_name])
            model.Add(tag_count[tag_name] < 3).OnlyEnforceIf(tag_active[tag_name].Not())
        elif tag_name in MINOR_FACTIONS:
            # Normal Minor: >= 2
            model.Add(tag_count[tag_name] >= 2).OnlyEnforceIf(tag_active[tag_name])
            model.Add(tag_count[tag_name] < 2).OnlyEnforceIf(tag_active[tag_name].Not())
        elif tag_name == SPECIAL_MINOR:
            # Solitary: Exactly 1
            model.Add(tag_count[tag_name] == 1).OnlyEnforceIf(tag_active[tag_name])
            model.Add(tag_count[tag_name] != 1).OnlyEnforceIf(tag_active[tag_name].Not())
        elif tag_name == SOLO_FACTION:
            # Harmony: >= 1 (Muelsyse solo)
            model.Add(tag_count[tag_name] >= 1).OnlyEnforceIf(tag_active[tag_name])
            model.Add(tag_count[tag_name] == 0).OnlyEnforceIf(tag_active[tag_name].Not())

    # --- 3. Objective & Solve ---
    model.Maximize(sum(tag_active.values()))
    solver = cp_model.CpSolver()
    # solver.parameters.max_time_in_seconds = 60.0
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        st.success(f"### Theoretical Maximum Light-ups: {int(solver.ObjectiveValue())}")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Squad Deployment")
            for name in chara_pool:
                if solver.Value(is_deployed[name]):
                    extra = next((f" (+ {t})" for t, v in extra_tag[name].items() if solver.Value(v)), "")
                    st.write(f"**{name}**{extra}")

        with col2:
            st.subheader("Activated Factions")
            for tag_name in TAGS:
                if solver.Value(tag_active[tag_name]):
                    st.write(f"[ON] {tag_name} (Count: {solver.Value(tag_count[tag_name])})")

            st.subheader("Deactivated Factions")
            for tag_name in TAGS:
                if not solver.Value(tag_active[tag_name]):
                    st.write(f"[OFF] {tag_name} (Count: {solver.Value(tag_count[tag_name])})")
    else:
        st.error("No valid solution found.")

# --- Execution ---
if st.button("Run Optimizer"):
    with st.spinner("Calculating optimal squad..."):
        solve_stronghold(current_pool)
