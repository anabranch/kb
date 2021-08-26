from collections import Counter
from typing import Sequence, Tuple
import random
from itertools import permutations
import logging
from functools import lru_cache

import numpy as np
import pandas as pd

import constants

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
########## Planning


def monthly_percentages_possible():
    blank = (15, 22, 28, 35)
    perms = permutations(blank)
    return perms


@lru_cache(maxsize=4000)
def percentages_possible(num_values=3):
    starter = list(range(16, 92, 2))  # can tweak this number
    perms = permutations(starter, num_values)
    if num_values == 2:
        return list(filter(lambda x: x[0] + x[1] == 100, perms))
    if num_values == 3:
        return list(filter(lambda x: x[0] + x[1] + x[2] == 100, perms))
    if num_values == 4:
        return list(filter(lambda x: x[0] + x[1] + x[2] + x[3] == 100, perms))
    if num_values == 5:
        return list(filter(lambda x: x[0] + x[1] + x[2] + x[3] + x[4] == 100, perms))
    if num_values == 6:
        return list(
            filter(lambda x: x[0] + x[1] + x[2] + x[3] + x[4] + x[5] == 100, perms)
        )
    else:
        assert False, "unsupported day count"


########## Functions


def calc_weight_at_percentage(one_rep_max, rel_intensity):
    return one_rep_max / rel_intensity


def calc_intensity_percentage(weight, one_rep_max):
    return weight / one_rep_max


def convert_to_kettlebell(weight):
    remainder = weight % 4
    if remainder == 1:
        return weight - 1
    if remainder == 2:
        return weight + 2
    if remainder == 3:
        return weight + 1

    return weight


# TODO: need to fix this to give more set variety
# TODO: also to hit the target reps
def calc_sets(values: Sequence[float], one_rep_max: int) -> Sequence[Tuple[int, int]]:
    rel_intensities = {60: (4, 6), 70: (3, 6), 80: (2, 4), 90: (1, 2)}
    # reps x weight
    # random.seed(constants.SEED)
    final_sets = []
    values = Counter(values)
    for lift, reps in values.items():
        starting_sets = []

        relative_intensity = int(calc_intensity_percentage(lift, one_rep_max) * 10) * 10
        if relative_intensity not in rel_intensities:
            continue
        rep_min, rep_max = rel_intensities[relative_intensity]
        min_sets = int(reps / rep_max)
        max_sets = int(reps / rep_min)
        for x in range(min_sets):
            starting_sets.append((random.choice(range(rep_min, rep_max + 1)), lift))
        for x in range(max_sets):
            starting_sets.append((random.choice(range(rep_min, rep_max + 1)), lift))
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


########## Classes


class Exercise:
    def __init__(self, name: str, category: str, motion: str, one_rep_max: int = 0):
        self.name = name
        self.one_rep_max = one_rep_max
        self.category = category
        self.motion = motion

    def __repr__(self):
        return self.name

    def set_one_rep_max(self, value):
        self.one_rep_max = value
        return self

    def _work_vol_distribution(self, num_lifts):
        return np.random.normal(constants.CENTER_WEIGHT_VOL, 6, num_lifts) / 100

    def _work_weight_distribution(self, vol_dist):
        return [
            self.convert_to_value(int(self.one_rep_max * prcnt)) for prcnt in vol_dist
        ]

    def convert_to_value(self, raw_value: int):
        if self.category == "kb":
            return convert_to_kettlebell(raw_value)
        elif self.category == "bw":
            return int(raw_value)
        elif self.category == "bb":
            return int(raw_value)
        assert False, "We should never reach this spot"

    def ideal_monthly_nl(self):
        # random.seed(constants.SEED)
        if self.motion in ("squat", "hinge"):
            return random.choice(list(range(100, 200)))

        if self.motion in ("push", "pull"):
            return random.choice(list(range(200, 300)))

    def build_workout(self, num_reps: int) -> Sequence[Tuple[int, int]]:
        num_lifts = max(constants.MIN_LIFTS_PER_EXERCISE, num_reps)
        # percentages of work
        work_vol_distribution = self._work_vol_distribution(num_lifts)
        # actual weights
        weight_distribution = self._work_weight_distribution(work_vol_distribution)

        sets = calc_sets(weight_distribution, self.one_rep_max)
        return sets


class Program:
    def __init__(
        self,
        exercises: Sequence[Exercise],
        months_in_program: int = 2,
        days_per_week: int = 3,
        workouts_per_day: int = 1,
    ):
        self.days_per_week = days_per_week
        self.month_in_program = months_in_program
        self.workouts_per_day = workouts_per_day
        self.exercises = exercises

    def get_percentage_plan(self):
        possible_weeks = (
            pd.DataFrame(
                monthly_percentages_possible(),
                columns=[f"week_{x}" for x in range(1, 4 + 1)],
            )
            / 100
        )

        possible_days_in_week = (
            pd.DataFrame(
                percentages_possible(self.days_per_week),
                columns=[f"day_{x}" for x in range(1, self.days_per_week + 1)],
            )
            / 100
        )

        actuals = []
        # TODO: This is where we'd control intensity
        for month_no, month in enumerate(range(self.month_in_program)):
            idx, weeks = random.choice(list(possible_weeks.iterrows()))
            for week_no, week in enumerate(weeks):
                idx, days = random.choice(list(possible_days_in_week.iterrows()))
                for day_no, day in enumerate(days):
                    actuals.append(
                        {
                            "month": month_no + 1,
                            "week": week_no + 1,
                            "day": day_no + 1,
                            "time": f"month_{month} - week_{week} - day_{day}",
                            "week_percentage": week,
                            "day_in_week_percentage": day,
                            "day_in_month_percentage": day * week,
                        }
                    )

        return {"percentages": actuals}

    def get_nl_plan(self):
        motions = {}
        for ex in self.exercises:
            tmp = motions.get(ex.motion, [])
            tmp.append(ex)
            motions[ex.motion] = tmp
        print(self.exercises)
        print(motions)
        motion_percentages = dict(
            [(m, self.get_percentage_plan()["percentages"]) for m in motions.keys()]
        )
        motion_percentages_lookup = {}
        for m, plan in motion_percentages.items():
            for row in plan:
                motion_percentages_lookup[
                    (m, row["month"], row["week"], row["day"])
                ] = row["day_in_month_percentage"]

        plan = []

        for month in range(self.month_in_program):

            for week in range(4):

                for day in range(self.days_per_week):
                    for motion, exercises in motions.items():

                        prcnt = motion_percentages_lookup[
                            (m, month + 1, week + 1, day + 1)
                        ]

                        for exercise in exercises:
                            target_nl = int(exercise.ideal_monthly_nl() * prcnt)
                            workout = exercise.build_workout(target_nl)
                            print(workout)
                            for reps, weight in workout:

                                plan.append(
                                    {
                                        "month": month,
                                        "week": week,
                                        "day": day,
                                        "time": f"month_{month} - week_{week} - day_{day}",
                                        "motion": motion,
                                        "exercise": exercise,
                                        "target_nl_workout": target_nl,
                                        "reps": reps,
                                        "weight": weight,
                                    }
                                )
        return {"plan": plan, "motion": motion_percentages}
