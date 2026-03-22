# app.py
import random

import streamlit as st
from scaffold import Protocol, Character
from data import chara_pool
from ortools.sat.python import cp_model

# --- UI Header ---
st.title("Stronghold Protocol Alliance 2: Faction Optimizer")
st.header("Arknights")
st.markdown("Calculate the theoretical maximum faction light-ups for your squad!")

# --- User Input ---
all_charas = list(chara_pool.keys())
ban_factions = st.multiselect(
    "Select Operators to BAN (e.g., they are unavailable or you don't want to keep them in your final line-up):",
    options=all_charas,
    default=[]  # set default bans here
)

# --- Data Cleaning ---
current_pool = {name: chara for name, chara in chara_pool.items() if name not in ban_factions}
p = Protocol(current_pool)

# --- Core Function ---
TAGS = Character.TAGS
TAGS_DEF = Character.TAGS_DEF

MAJOR_FACTIONS = TAGS_DEF[:8]
ALLOWED_EXTRA_MINOR = TAGS_DEF[8:14]
ALLOWED_EXTRA_TAGS = TAGS_DEF[:14]

MINOR_FACTIONS = TAGS_DEF[8:17]
SPECIAL_MINOR = TAGS_DEF[17]
SOLO_FACTION = TAGS_DEF[18]

PREP_ZONE_FACTIONS = TAGS_DEF[19:22]
PROMOTION_FACTION = TAGS_DEF[22]
GLOBAL_FACTIONS = TAGS_DEF[19:23]

global_status = {}
global_reqs = {
    'Foresight': 2,
    'Miracle': 2,
    'Investor': 3,
    'Skill': 0  # Always on
}
for tag, threshold in global_reqs.items():
    global_status[tag] = p.count_tag(TAGS[tag]) >= threshold


def solve_stronghold(chara_pool, max_deployment=9):
    model = cp_model.CpModel()

    # --- 1. Variables ---
    is_deployed = {name: model.NewBoolVar(f"deploy_{name}") for name in chara_pool}

    # extra_tag[name][tag]: 1 if character 'name' equips extra 'tag'
    extra_tag = {}
    for name in chara_pool:
        extra_tag[name] = {tag_name: model.NewBoolVar(f"extra_{name}_{tag_name}") for tag_name in ALLOWED_EXTRA_TAGS}

    tag_count = {tag_name: model.NewIntVar(0, max_deployment * 2, f"count_{tag_name}") for tag_name in TAGS_DEF}
    tag_active = {}

    for tag_name in TAGS_DEF:
        if tag_name in global_reqs:
            # These are constants! 1 if pre-calculated as True, else 0
            is_on = 1 if global_status[tag_name] else 0
            tag_active[tag_name] = model.NewConstant(is_on)
        else:
            # These remain as Booleans
            tag_active[tag_name] = model.NewBoolVar(f"active_{tag_name}")

    # --- 2. Constraints ---
    model.Add(sum(is_deployed.values()) <= max_deployment)

    for name in chara_pool:
        # Each deployed character can have AT MOST one extra tag
        model.Add(sum(extra_tag[name].values()) <= is_deployed[name])
        # A character cannot pick a duplicating tag when they already possess it
        for tag_name in ALLOWED_EXTRA_TAGS:
            if chara_pool[name].has_tag(TAGS[tag_name]):
                model.Add(extra_tag[name][tag_name] == 0)

    # Calculate total tag counts
    for tag_name in TAGS_DEF:
        innate_contrib = []
        extra_contrib = []

        for name, chara in chara_pool.items():
            if chara.has_tag(TAGS[tag_name]):
                innate_contrib.append(is_deployed[name])
            if tag_name in ALLOWED_EXTRA_TAGS:
                extra_contrib.append(extra_tag[name][tag_name])

        if tag_name == PROMOTION_FACTION:
            model.Add(tag_count[tag_name] == 2)
        elif tag_name in PREP_ZONE_FACTIONS:
            total_pool_count = p.count_tag(TAGS[tag_name])
            # Count = (Innate Deployed + Extra Deployed) + (Total Pool - Innate Deployed)
            #       = Extra Deployed + Total Pool
            model.Add(tag_count[tag_name] == sum(extra_contrib) + total_pool_count)
        else:
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
        icon_names = 'celebration', 'campaign', 'cloud_done', 'crown', 'trophy', \
                     'rocket_launch', 'task_alt', 'check', 'check_circle', 'data_check'
        st.badge("Success", icon=f":material/{random.choice(icon_names)}:", color="green")
        st.success(f"### Theoretical Maximum Light-ups: {int(solver.ObjectiveValue())}")

        deployed_names = [name for name in chara_pool if solver.Value(is_deployed[name])]
        prep_names = get_prep_zone_layout(chara_pool, deployed_names)

        active_factions, inactive_factions = [], []
        for tag_name in TAGS_DEF:
            count = solver.Value(tag_count[tag_name])
            if solver.Value(tag_active[tag_name]):
                icon = "☑" if tag_name in GLOBAL_FACTIONS else "✅"
                active_factions.append(f"{icon} **{tag_name}** ({count})")
            else:
                inactive_factions.append(f"❌ ~~{tag_name}~~ ({count})")

        col_assign, col_status = st.columns([1.3, 1])

        with col_assign:
            st.subheader("⚔️ Personnel Assignment 🛡️")

            st.caption("DEPLOY TO FIELD (SQUAD)")
            for name in deployed_names:
                # Check extra tag (at most 1)
                extra = next((f" (+ {t})" for t, v in extra_tag[name].items() if solver.Value(v)), "")
                st.info(f"**{name}**{extra}")

            st.divider()

            st.caption("PLACE IN PREPARATION ZONE (BENCH)")
            if not prep_names:
                st.write("No specific bench units required.")
            for name in prep_names:
                # Show which Prep Tags this character is satisfying
                tags_covered = [t for t in PREP_ZONE_FACTIONS if chara_pool[name].has_tag(TAGS[t])]
                st.warning(f"**{name}** \n*{', '.join(tags_covered)}*")

        with col_status:
            st.subheader("📋 Faction Status 🎯")

            for payload in active_factions:
                st.write(payload)

            if inactive_factions:
                st.divider()
                st.caption("DEACTIVATED / MISSED")
                for payload in inactive_factions:
                    st.write(payload)
    else:
        st.error("No valid solution found.")


def get_prep_zone_layout(full_pool, deployed_names):
    bench_names = [name for name in full_pool if name not in deployed_names]
    random.shuffle(bench_names)

    requirements = {}
    for tag, threshold in global_reqs.items():
        count_in_squad = sum(1 for name in deployed_names if full_pool[name].has_tag(TAGS[tag]))
        requirements[tag] = max(0, threshold - count_in_squad)

    prep_squad = set()

    for tag, needed in requirements.items():
        found = 0
        for name in bench_names:
            if found >= needed:
                break
            if name not in prep_squad and full_pool[name].has_tag(TAGS[tag]):
                prep_squad.add(name)
                found += 1

    return prep_squad


# --- Execution ---
if st.button("Run Optimizer"):
    with st.spinner("Calculating optimal squad..."):
        solve_stronghold(current_pool)
