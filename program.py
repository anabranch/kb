from collections import Counter
from typing import Sequence, Tuple
import random
from itertools import permutations
import logging
from functools import lru_cache

import numpy as np
import pandas as pd

import constants

########## Planning


def monthly_percentages_possible():
    blank = (15, 22, 28, 35)
    perms = permutations(blank)
    return perms


def exercises_to_motions(exercises):
    motions = {
        "push": [],
        "pull": [],
        "hinge": [],
        "squat": [],
    }
    for x in exercises:
        motions[x.motion].append(x)

    final = {}
    for motion, exercises in motions.items():
        if exercises:
            final[motion] = Motion(exercises)

    return final


@lru_cache
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
    if num_values == 7:
        return list(
            filter(
                lambda x: x[0] + x[1] + x[2] + x[3] + x[4] + x[5] + x[6] == 100, perms
            )
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


class ExerciseConfig:
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


# break this out of its own class, it's useless
class Exercise:
    def __init__(self, conf: ExerciseConfig):
        self.exercise = conf
        # random.seed(constants.SEED)

    def __repr__(self):
        return self.exercise

    def _work_vol_distribution(self, num_lifts):
        return np.random.normal(constants.CENTER_WEIGHT_VOL, 6, num_lifts) / 100

    def _work_weight_distribution(self, vol_dist):
        return [
            self.exercise.convert_to_value(int(self.exercise.one_rep_max * prcnt))
            for prcnt in vol_dist
        ]

    def build_workout(self, num_reps: int) -> Sequence[Tuple[int, int]]:
        # TODO: potential for removing this all together
        num_lifts = max(constants.MIN_LIFTS_PER_EXERCISE, num_reps)
        # percentages of work
        work_vol_distribution = self._work_vol_distribution(num_lifts)
        # actual weights
        weight_distribution = self._work_weight_distribution(work_vol_distribution)

        sets = calc_sets(weight_distribution, self.exercise.one_rep_max)
        return sets


# break this out of its own class, it's useless
# Make it an exercise collection
# store some basic metadata in here
class Motion:
    def __init__(self, valid_exercises: Sequence[ExerciseConfig]):
        self.exercises: Sequence[Exercise] = [Exercise(x) for x in valid_exercises]
        # random.seed(constants.SEED)
        random.shuffle(self.exercises)

    def __repr__(self) -> str:
        return self.name()

    def build_workout(self, num_reps: int, num_exercises: int = 10):
        workout_exercises = []
        for ex_number in range(min(len(self.exercises), num_exercises)):
            workout_exercises.append(self.exercises[ex_number])

        programmed_exercises = []
        for ex in workout_exercises:
            programmed_exercises.append((ex.exercise, ex.build_workout(num_reps)))

        return programmed_exercises

    def ideal_monthly_nl(self):
        categories = []
        for e in self.exercises:
            categories.append(e.exercise.ideal_monthly_nl())

        return categories.pop()

    def name(self):
        categories = []
        for e in self.exercises:
            categories.append(e.exercise.motion)

        assert len(set(categories)) == 1

        return categories.pop()


class Program:
    def __init__(
        self,
        valid_motions: Sequence[Motion],
        months_in_program: int = 2,
        days_per_week: int = 3,
        workouts_per_day: int = 1,
    ):
        self.days_per_week = days_per_week
        self.month_in_program = months_in_program
        self.workouts_per_day = workouts_per_day
        self.motions = valid_motions

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
                            "week_percentage": week,
                            "day_percentage_in_week": day,
                            "day_percentage": day * week,
                        }
                    )

        return pd.DataFrame(actuals)

    def get_nl_plan(self):
        final = []
        for motion in self.motions:
            ideal_monthly_nl = motion.ideal_monthly_nl()
            motion_daily_percentages = self.get_percentage_plan()
            motion_daily_percentages["motion"] = motion.name()
            motion_daily_percentages["target_nl"] = (
                ideal_monthly_nl * motion_daily_percentages["day_percentage"]
            ).astype("int")
            motion_daily_percentages["sets"] = [
                motion.build_workout(x) for x in motion_daily_percentages["target_nl"]
            ]

            explode_v1 = motion_daily_percentages
            explode_v1["time"] = [
                f"month_{x[1].month} week_{x[1].week} day_{x[1].day}"
                for x in explode_v1.iterrows()
            ]
            explode_v1["one_rm"] = explode_v1.sets.apply(lambda x: x[0][0].one_rep_max)
            explode_v1["exercise"] = explode_v1.sets.apply(lambda x: x[0][0].name)

            explode_v1["sets"] = explode_v1.sets.apply(lambda x: x[0][1])
            explode_v2 = explode_v1.explode("sets")
            explode_v2["weight"] = explode_v2.sets.apply(lambda x: x[1])
            explode_v2["reps"] = explode_v2.sets.apply(lambda x: x[0])

            final.append(explode_v2)

        return pd.concat(final)[
            [
                "month",
                "week",
                "day",
                "time",
                "one_rm",
                "week_percentage",
                "day_percentage_in_week",
                "day_percentage",
                "motion",
                "exercise",
                "target_nl",
                "reps",
                "weight",
            ]
        ]
