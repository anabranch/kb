import streamlit as st
import pandas as pd

import st_utils as stu
import program as p
import constants

pd.options.plotting.backend = "plotly"

st.title("Plan Strong - Program Generator")


POTENTIAL_EXERCISES = [
    p.ExerciseConfig("Dips", "kb", "push"),
    p.ExerciseConfig("Overhead Press", "bb", "push"),
    p.ExerciseConfig("Bench", "bb", "push"),
    p.ExerciseConfig("Pull ups", "bw", "pull"),
    p.ExerciseConfig("Chin Ups", "bw", "pull"),
    p.ExerciseConfig("Deadlift", "bb", "hinge"),
    p.ExerciseConfig("KB Swing", "kb", "hinge"),
    p.ExerciseConfig("KB Snatch", "kb", "hinge"),
    p.ExerciseConfig("Zercher Squat", "bb", "squat"),
    p.ExerciseConfig("Goblet Squat", "kb", "squat"),
]
EXERCISE_NAMES = [x.name for x in POTENTIAL_EXERCISES]
EXERCISE_LOOKUP = dict(zip(EXERCISE_NAMES, POTENTIAL_EXERCISES))


### Sidebar Core Configs
#######
#####
###
st.sidebar.header("Exercise Configurator")
MONTHS = int(st.sidebar.number_input("Months", 1, 4, 2))
DAYS_PER_WEEK = int(st.sidebar.number_input("Training Days per week", 1, 7, 3))

EXERCISE_NAMES_IN_PROGRAM = st.sidebar.multiselect(
    "Exercises in Program", EXERCISE_LOOKUP.keys()
)

one_rep_maxes = {}
st.sidebar.subheader("One Rep Maxes [KG]")
for name in EXERCISE_NAMES_IN_PROGRAM:
    ex = EXERCISE_LOOKUP[name]
    ex.set_one_rep_max(st.sidebar.slider("1RM - " + name, 4, 160, step=4))
    st.sidebar.write("1RM - " + name + f" Pounds ~= {int(ex.one_rep_max*2.2)}")


EXERCISES_IN_PROGRAM = [EXERCISE_LOOKUP[x] for x in EXERCISE_NAMES_IN_PROGRAM]

MOTIONS = p.exercises_to_motions(EXERCISES_IN_PROGRAM)
if MOTIONS:
    fp = p.Program(MOTIONS.values())
    plan = fp.get_nl_plan()
    st.header("Plan")
    st.markdown(
        """
    This plan was automatically generated.
    """
    )
    for m in MOTIONS.keys():
        st.header(m.title() + " Lift Goals, Targets, and Plan")
        st.subheader("Lift Targets & Planned")
        st.table(
            pd.merge(
                plan.groupby(["time", "motion", "exercise"])
                .reps.sum()
                .reset_index()
                .rename({"reps": "actual_nl"}, axis=1),
                plan[["time", "motion", "exercise", "target_nl"]].drop_duplicates(),
                how="inner",
                on=["time", "motion", "exercise"],
            )
        )
        st.subheader("Week Volume Target Percentages")
        st.table(
            plan[plan.motion == m][
                ["time", "week_percentage", "day_percentage_in_week", "day_percentage"]
            ].drop_duplicates()
        )
        st.subheader("Cumulative Plan Percentages")

    # print(plan)
    # st.table(plan)


# print
# ###
#####
#######
### End Sidebar Core Configs

# plan = p.Program()

# ### Full Plan
# #######
# #####
# ###
# fp = p.FullPlan(
#     [p.Exercise(name, one_rep_maxes[name]) for name in EXERCISES_IN_PROGRAM],
#     days_per_week=DAYS_PER_WEEK,
# )

# with st.form("my_form", clear_on_submit=False):
#     st.header("Training Plan")
#     st.write(fp.daily_plan()[["time", "category", "exercise", "reps", "weight"]])
#     submit = st.form_submit_button(
#         "Download training plan", on_click=stu.plan_downloader(fp.daily_plan())
#     )
# st.subheader("By Week and Category")
# ###
# #####
# #######
# ### End Full Plan

# st.header("Program Analysis")
# st.markdown(
#     """This program is randomly generated given the constraints that
# (a) you apply on the left and
# (b) the constraints from the Plan Strong guide. It follows the delta 20% principle."""
# )

# st.subheader("Weekly NL Volume")
# st.markdown(
#     """
# This is a little off right now because rather than doing planning by motion (e.g., press, pull) I am doing it by exercise and then randomly sampling
# the sets from that exercise. This leads to inconsistencies in expected weekly volume. However, it seems to grow ok, so I don't know how much of an issue it actually is.
# """
# )
# st.plotly_chart(fp.weekly_plan_nl().plot())

# st.subheader("Cumulative NL Volume")
# st.plotly_chart(fp.weekly_plan_nl().cumsum().plot())

# # weekly = fp.weekly_plan()
# # weekly["time"] = weekly["month"] + " - " + weekly["week"]
# # st.plotly_chart(
# #     weekly.groupby(["time", "category"])
# #     .reps.sum()
# #     .reset_index()
# #     .pivot(index="time", columns="category", values="reps")
# #     .plot()
# # )
# # categories = weekly.category.unique()
# # for cat in categories:
# #     st.subheader(cat)

# #     st.table(
# #         weekly[weekly.category == cat].groupby(["month", "week"]).reps.sum().cumsum()
# #     )


# # # st.plotly_chart(
# # #     overall_plan.groupby(["time", "category"])["reps"]
# # #     .sum()
# # #     .reset_index()
# # #     .drop("category", axis=1)
# # #     .set_index("time")
# # #     .cumsum()
# # #     .plot()
# # # )
# # # st.subheader("Detailed Plan")

# # # st.table(
# # #     overall_plan.drop(["volume", "time"], axis=1).set_index(["month", "week", "day"])
# # # )
