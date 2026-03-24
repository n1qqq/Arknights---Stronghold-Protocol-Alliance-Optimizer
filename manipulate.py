# manipulate.py
import random

from scaffold import Protocol, Character
from data import *
from ortools.sat.python import cp_model

TAGS = Character.TAGS
TAGS_DEF = Character.TAGS_DEF


# --- SET BANNED OPERATORS HERE ---
ban_list = 'Leizi', 'Mwynar'
# --- END BANNED OPERATORS LIST ---


for chara in ban_list:
    if chara in chara_pool:
        del chara_pool[chara]


# --- TEST INITIAL DATA HERE  ---
test_init = False

if test_init:
    for tag in TAGS.values():
        print(tag, Protocol(chara_pool).count_tag(tag))
# --- INITIAL DATA TESTS END  ---


MAJOR_FACTIONS = TAGS_DEF[:8]
ALLOWED_EXTRA_MINOR = TAGS_DEF[8:14]
ALLOWED_EXTRA_TAGS = TAGS_DEF[:14]

MINOR_FACTIONS = TAGS_DEF[8:17]
SPECIAL_MINOR = TAGS_DEF[17]
SOLO_FACTION = TAGS_DEF[18]

PREP_ZONE_FACTIONS = TAGS_DEF[19:22]
PROMOTION_FACTION = TAGS_DEF[22]
GLOBAL_FACTIONS = TAGS_DEF[19:23]

global_reqs = {
    "Foresight": 2,
    "Miracle": 2,
    "Investor": 3,
    "Skill": 0      # Always on (later flipped off if character pool is too scarce, i.e. < 2 people)
}


def solve_maximum_lightups(chara_pool, max_deployment=9):
    model = cp_model.CpModel()

    # --- 1. Variables ---
    p = Protocol(chara_pool)

    global_status = {}
    for tag, threshold in global_reqs.items():
        global_status[tag] = p.count_tag(TAGS[tag]) >= threshold
    # Can't have 2 promotions if you don't even have 2 people!
    global_status["Skill"] = len(chara_pool) >= 2

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
            model.Add(tag_count[tag_name] == min(len(chara_pool), 2))
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
        print(f"Theoretical Max Light-ups: {int(solver.ObjectiveValue())}")

        deployed_names = [name for name in chara_pool if solver.Value(is_deployed[name])]
        prep_names = get_prep_zone_layout(chara_pool, deployed_names)

        print("\n--- Squad Deployment ---")
        for name in deployed_names:
            extra = next((f" (+ {t})" for t, v in extra_tag[name].items() if solver.Value(v)), "")
            print(f"- {name}{extra}")

        print("\n--- Preparation Zone ---")
        for name in prep_names:
            extra = next((f" (+ {t})" for t, v in extra_tag[name].items() if solver.Value(v)), "")
            print(f"- {name}{extra}")

        print("\n--- Activated Factions ---")
        for tag_name in TAGS:
            if solver.Value(tag_active[tag_name]):
                print(f"[ON] {tag_name} (Count: {solver.Value(tag_count[tag_name])})")

        print("\n--- Deactivated Factions ---")
        for tag_name in TAGS:
            if not solver.Value(tag_active[tag_name]):
                print(f"[OFF] {tag_name} (Count: {solver.Value(tag_count[tag_name])})")
    else:
        print("No valid solution found.")


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


solve_maximum_lightups(chara_pool)
