from itertools import permutations
import random
import collections
from functools import lru_cache

import pandas as pd
import numpy as np

import constants


def get_ideal_nl(category, type="max"):
    if category in ("squat", "hinge"):
        if type == "min":
            return 100
        return 200

    if category in ("push", "pull"):
        if type == "min":
            return 200
        return 300


# need to fix this to give more set variety
def calc_sets(values, one_rep_max):
    rel_intensities = {60: (4, 6), 70: (3, 6), 80: (2, 4), 90: (1, 2)}
    # reps x weight

    final_sets = []
    for lift, reps in values.items():
        starting_sets = []
        rep_min, rep_max = rel_intensities[calc_rel_intensity(lift, one_rep_max)]
        min_sets = int(reps / rep_max)
        max_sets = int(reps / rep_min)
        for x in range(min_sets):
            starting_sets.append((rep_max, lift))
        for x in range(max_sets):
            starting_sets.append((rep_min, lift))
        if min_sets == 0 or max_sets == 0:
            final_sets.append((reps, lift))
        elif min_sets == max_sets:
            for x in range(max_sets):
                final_sets.append(starting_sets.pop())
        else:
            random.shuffle(starting_sets)
            for x in range(random.choice(range(min_sets, max_sets))):
                final_sets.append(starting_sets.pop())
    random.shuffle(final_sets)
    return final_sets


def calc_weight_1rm(one_rep_max, percent):
    closest_weight = 0
    diff = 1
    for potential in constants.KB_WEIGHTS:
        prcnt_of_one_rm = potential / float(one_rep_max)
        amount_off = abs(prcnt_of_one_rm - percent)
        if amount_off < diff:
            diff = amount_off
            closest_weight = potential

    return closest_weight


def calc_rel_intensity(weight, one_rep_max):
    for x in range(60, 100, 10):
        if weight / one_rep_max - x < 10:
            return x


def row_jumps(row):
    prev = None
    diff = 0
    for value in row:
        if not prev:
            prev = value
            continue
        diff += abs(prev - value)
        prev = value
    return diff


@lru_cache
def percentages_possible(num_values=3):
    starter = list(range(15, 91, 1))
    perms = permutations(starter, num_values)
    if num_values == 2:
        return list(filter(lambda x: x[0] + x[1] == 100, perms))
    if num_values == 3:
        return list(filter(lambda x: x[0] + x[1] + x[2] == 100, perms))
    if num_values == 4:
        return list(filter(lambda x: x[0] + x[1] + x[2] + x[3] == 100, perms))
    if num_values == 5:
        return list(filter(lambda x: x[0] + x[1] + x[2] + x[3] + x[4] == 100, perms))
    else:
        return False


def monthly_percentages_possible():
    blank = (15, 22, 28, 35)
    perms = permutations(blank)
    return perms


def categorize_plans(exercises):

    categories = {}
    for e in exercises:
        ls = categories.get(e.category.title(), [])
        ls.append(e)
        categories[e.category.title()] = ls
    return categories


def get_lift_type(input_name):
    results = []
    for name, type_, category in constants.POTENTIAL_EXERCISES:
        results.append((name, type_))
    types = dict(results)
    return types[input_name]


def get_lift_category(input_name):
    results = []
    for name, type_, category in constants.POTENTIAL_EXERCISES:
        results.append((name, category))
    types = dict(results)
    print(types)
    return types[input_name]


class Plan:
    def __init__(self, exercise_plan):
        self.raw = exercise_plan

    def daily_targets(self):
        return self.raw["targets"]

    def daily_plan(self):
        results = []

        for (mo, wk, da), v in self.raw["targets"].items():
            for (nl, weight) in v:
                results.append((mo, wk, da, nl, weight))
        targets = pd.DataFrame(
            results, columns=["month", "week", "day", "reps", "weight"]
        )

        targets["volume"] = targets.reps * targets.weight

        return targets


class FullPlan:
    def __init__(self, exercises, days_per_week):
        self.exercises = exercises
        self.days_per_week = days_per_week
        self.categories = categorize_plans(exercises)

    def days(self):
        days = {}

        for category, raw_exercises in self.categories.items():
            candidate_category_exercises = {}
            for raw_exercise in raw_exercises:
                plan = raw_exercise.generate_plan(self.days_per_week)
                # TODO: this is where I would have to modify
                # I would have to generate the reps and sets for presses
                # then I think I would have to go to the exercise and find
                # some set combination that fits that.
                daily_sets = plan.daily_targets()

                for day_key, sets in daily_sets.items():
                    day_sets = candidate_category_exercises.get(day_key, [])
                    day_sets.append({(category, raw_exercise.name): sets})
                    candidate_category_exercises[day_key] = day_sets

            for day_key, exercises in candidate_category_exercises.items():
                actuals = days.get(day_key, [])
                actuals.append(random.choice(exercises))
                days[day_key] = actuals

        return days

    def daily_plan(self):
        results = []

        for (mo, wk, da), exers in self.days().items():
            for ex in exers:
                for ex_key, sets in ex.items():
                    for (reps, weight) in sets:
                        results.append(
                            (
                                mo,
                                wk,
                                da,
                                ex_key[0],
                                ex_key[1],
                                reps,
                                weight,
                            )
                        )
        targets = pd.DataFrame(
            results,
            columns=["month", "week", "day", "category", "exercise", "reps", "weight"],
        )
        targets["time"] = (
            targets["month"] + " - " + targets["week"] + " - " + targets["day"]
        )

        targets["volume"] = targets.reps * targets.weight

        return targets

    def weekly_plan_nl(self):
        df = (
            self.daily_plan().groupby(["month", "week", "category"]).sum().reset_index()
        )
        df["time"] = df["month"] + " - " + df["week"]
        grouped = df.groupby(["time", "category"]).reps.sum().reset_index()
        df = grouped.pivot(index="time", columns="category", values="reps")

        return df

    def weekly_plan_nl_percent(self):
        df = (
            self.daily_plan()
            .groupby(["month", "week", "category"])
            .reps.sum()
            .reset_index()
        )
        df2 = df.groupby(["month", "category"]).reps.sum().reset_index()

        df3 = pd.merge(df, df2, "inner", on=["month", "category"])
        df3["percent"] = df3["reps_x"] / df3["reps_y"]

        df3["time"] = df3["month"] + " - " + df3["week"]
        grouped = df3.groupby(["time", "category"]).percent.sum().reset_index()
        df3 = grouped.pivot(index="time", columns="category", values="percent")

        return df3

    def monthly_plan(self):
        return self.daily_plan().groupby(["month", "category"]).sum().reset_index()

    def weekly_benchmarks(self):
        # target percentages by week
        for ex in self.exercises:
            month_1 = ex.generate_target_percentages(self.days_per_week)[
                "month_1_percentages"
            ]
            month_2 = ex.generate_target_percentages(self.days_per_week)[
                "month_2_percentages"
            ]

            df = pd.merge(month_1, month_2, "inner", left_index=True, right_index=True)
            df.columns = ["month_1", "month_2"]
            return df
        #     targets = pd.DataFrame(
        #         self.raw["target_percentages"]["month_1_percentages"]
        #     ).reset_index()
        #     targets["month"] = "month_1"
        #     targets.columns = ["week", "benchmark_percent", "month"]
        #     targets_2 = pd.DataFrame(
        #         self.raw["target_percentages"]["month_2_percentages"]
        #     ).reset_index()
        #     targets_2["month"] = "month_2"
        #     targets_2.columns = ["week", "benchmark_percent", "month"]
        #     final = pd.concat([targets, targets_2])

        #     final["benchmark_nl_min"] = (
        #         self.raw["min_monthly_nl"] * final["benchmark_percent"]
        #     )

        #     final["benchmark_nl_max"] = (
        #         self.raw["max_monthly_nl"] * final["benchmark_percent"]
        #     )
        #     final["time"] = final["month"] + " - " + final["week"]

        #     return final[
        #         [
        #             "month",
        #             "week",
        #             "time",
        #             "benchmark_percent",
        #             "benchmark_nl_min",
        #             "benchmark_nl_max",
        #         ]
        #     ]
        pass

    def plan_to_benchmark(self):
        bench = self.weekly_benchmark()
        plan = self.weekly_plan()

        return pd.merge(bench, plan, "inner", on=["week", "month"]).drop(
            "weight", axis=1
        )


class Exercise:
    def __init__(self, name, one_rep_max=0):
        self.name = name
        self.lift_type = get_lift_type(name)
        self.category = get_lift_category(name)
        self.one_rep_max = one_rep_max

    def generate_plan(self, days_per_week):
        target_percent = self.generate_target_percentages(days_per_week)
        max_targets = {}
        min_targets = {}
        max_target_vol = {}
        min_target_vol = {}
        # this is day by day in the plan
        for key, pcnt in target_percent["daily_percent"].items():
            # don't let it drop below a certain amount
            min_lifts = max(15, int(pcnt * get_ideal_nl(self.category)))
            max_lifts = max(15, int(pcnt * get_ideal_nl(self.category)))
            # get around our HARI
            min_lifts_sample = np.random.normal(72.5, 6, min_lifts) / 100
            max_lifts_sample = np.random.normal(72.5, 6, max_lifts) / 100
            min_workout = collections.Counter(
                [calc_weight_1rm(self.one_rep_max, x) for x in min_lifts_sample]
            )
            max_workout = collections.Counter(
                [calc_weight_1rm(self.one_rep_max, x) for x in max_lifts_sample]
            )

            # get the sets that we should be running.
            max_sets = calc_sets(max_workout, self.one_rep_max)
            min_sets = calc_sets(min_workout, self.one_rep_max)

            # calculate what it should be
            max_vol = 0
            min_vol = 0
            max_nl = 0
            min_nl = 0
            for reps, weight in max_sets:
                max_vol += reps * weight
                max_nl += reps

            for reps, weight in min_sets:
                min_vol += reps * weight
                min_nl += reps

            max_targets[key] = max_sets
            min_targets[key] = min_sets
            max_target_vol[key] = max_vol
            min_target_vol[key] = min_vol

        return Plan(
            {
                "targets": max_targets,
                "target_percentages": target_percent,
                "max_monthly_nl": get_ideal_nl(self.category),
                "min_monthly_nl": get_ideal_nl(self.category),
            }
        )

    def set_one_rep_max(self, one_rm):
        self.one_rep_max = one_rm

    def generate_target_percentages(self, days_per_week):
        mo = self.generate_candidate_month_percentage()
        month_1 = mo.loc[random.choice(mo.index), :]
        month_2 = mo.loc[random.choice(mo.index), :]
        wk = self.generate_candidate_week_percentage(days_per_week)

        dailies = {}
        results = {
            "month_1_percentages": month_1,
            "month_2_percentages": month_2,
        }
        for week in month_1.index:
            day_vols = wk.loc[random.choice(wk.index), :]
            for day in day_vols.index:
                dailies[("month_1", week, day)] = month_1[week] * day_vols[day]

        for week in month_2.index:
            day_vols = wk.loc[random.choice(wk.index), :]
            for day in day_vols.index:
                dailies[("month_2", week, day)] = month_1[week] * day_vols[day]

        results["daily_percent"] = dailies
        return results

    def generate_candidate_month_percentage(self):
        possible = pd.DataFrame(
            monthly_percentages_possible(),
            columns=[f"week_{x}" for x in range(1, 4 + 1)],
        )
        mo = possible / 100
        # possible["var_rating"] = possible.apply(row_jumps, axis=1)
        return mo

    def generate_candidate_week_percentage(self, days_per_week):
        possible = pd.DataFrame(
            percentages_possible(days_per_week),
            columns=[f"day_{x}" for x in range(1, days_per_week + 1)],
        )
        possible = possible / 100
        # possible["weekly_var_rating"] = possible.apply(row_jumps, axis=1)
        return possible

    # def weekly_plan(self):
    #     return self.daily_plan().groupby(["month", "week"]).sum().reset_index()

    # def monthly_plan(self):
    #     return self.daily_plan().groupby(["month"]).sum().reset_index()

    # def weekly_benchmark(self):
    #     # target percentages by week
    #     targets = pd.DataFrame(
    #         self.raw["target_percentages"]["month_1_percentages"]
    #     ).reset_index()
    #     targets["month"] = "month_1"
    #     targets.columns = ["week", "benchmark_percent", "month"]
    #     targets_2 = pd.DataFrame(
    #         self.raw["target_percentages"]["month_2_percentages"]
    #     ).reset_index()
    #     targets_2["month"] = "month_2"
    #     targets_2.columns = ["week", "benchmark_percent", "month"]
    #     final = pd.concat([targets, targets_2])

    #     final["benchmark_nl_min"] = (
    #         self.raw["min_monthly_nl"] * final["benchmark_percent"]
    #     )

    #     final["benchmark_nl_max"] = (
    #         self.raw["max_monthly_nl"] * final["benchmark_percent"]
    #     )
    #     final["time"] = final["month"] + " - " + final["week"]

    #     return final[
    #         [
    #             "month",
    #             "week",
    #             "time",
    #             "benchmark_percent",
    #             "benchmark_nl_min",
    #             "benchmark_nl_max",
    #         ]
    #     ]

    # def plan_to_benchmark(self):
    #     bench = self.weekly_benchmark()
    #     plan = self.weekly_plan()

    #     return pd.merge(bench, plan, "inner", on=["week", "month"]).drop(
    #         "weight", axis=1
    #     )
