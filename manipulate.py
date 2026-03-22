# manipulate.py
from scaffold import Protocol, Character
from data import *
from ortools.sat.python import cp_model

TAGS = Character.TAGS
TAGS_DEF = Character.TAGS_DEF

ban_list = 'Leizi', 'Mwynar'
for chara in ban_list:
    if chara in chara_pool:
        del chara_pool[chara]

##### TEST INITIAL DATA HERE #####
test_init = False

p = Protocol(chara_pool)
if test_init:
    for tag in TAGS.values():
        print(tag, p.count_tag(tag))
##### INITIAL DATA TESTS END #####

MAJOR_FACTIONS = TAGS_DEF[:8]
ALLOWED_EXTRA_MINOR = TAGS_DEF[8:14]
ALLOWED_EXTRA_TAGS = MAJOR_FACTIONS + ALLOWED_EXTRA_MINOR

MINOR_FACTIONS = TAGS_DEF[8:17]
SPECIAL_MINOR = TAGS_DEF[17]
SOLO_FACTION = TAGS_DEF[18]

def solve_maximum_lightups(chara_pool, max_deployment=9):
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
        print(f"Theoretical Max Light-ups: {int(solver.ObjectiveValue())}")

        print("\n--- Squad Deployment ---")
        for name in chara_pool:
            if solver.Value(is_deployed[name]):
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


solve_maximum_lightups(chara_pool)
