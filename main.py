import streamlit as st
import pandas as pd

import st_utils as stu
import programming as p
import constants

pd.options.plotting.backend = "plotly"

st.title("Plan Strong - Program Generator")

### Sidebar Core Configs
#######
#####
###
st.sidebar.header("Exercise Configurator")
# TRAINING_PLAN_AGGRESSION = st.sidebar.selectbox(
#     "Training Plan Aggression", ["starter", "moderate", "intense", "get after it"]
# )
DAYS_PER_WEEK = int(st.sidebar.number_input("Training Days per week", 1, 7, 3))
EXERCISES_IN_PROGRAM = st.sidebar.multiselect(
    "Exercises in Program", [x[0] for x in constants.POTENTIAL_EXERCISES]
)

one_rep_maxes = {}
st.sidebar.subheader("One Rep Maxes [KG]")
for ex in EXERCISES_IN_PROGRAM:
    one_rep_maxes[ex] = st.sidebar.slider("1RM - " + ex, 4, 160, step=4)
    st.sidebar.write("1RM - " + ex + f" Pounds ~= {int(one_rep_maxes[ex]*2.2)}")
###
#####
#######
### End Sidebar Core Configs

### Full Plan
#######
#####
###
fp = p.FullPlan(
    [p.Exercise(name, one_rep_maxes[name]) for name in EXERCISES_IN_PROGRAM],
    days_per_week=DAYS_PER_WEEK,
)

with st.form("my_form", clear_on_submit=False):
    st.header("Training Plan")
    st.write(fp.daily_plan()[["time", "category", "exercise", "reps", "weight"]])
    submit = st.form_submit_button(
        "Download training plan", on_click=stu.plan_downloader(fp.daily_plan())
    )
st.subheader("By Week and Category")
###
#####
#######
### End Full Plan

st.header("Program Analysis")
st.markdown(
    """This program is randomly generated given the constraints that 
(a) you apply on the left and 
(b) the constraints from the Plan Strong guide. It follows the delta 20% principle."""
)

st.subheader("Weekly NL Volume")
st.markdown(
    """
This is a little off right now because rather than doing planning by motion (e.g., press, pull) I am doing it by exercise and then randomly sampling
the sets from that exercise. This leads to inconsistencies in expected weekly volume. However, it seems to grow ok, so I don't know how much of an issue it actually is.
"""
)
st.plotly_chart(fp.weekly_plan_nl().plot())

st.subheader("Cumulative NL Volume")
st.plotly_chart(fp.weekly_plan_nl().cumsum().plot())

# weekly = fp.weekly_plan()
# weekly["time"] = weekly["month"] + " - " + weekly["week"]
# st.plotly_chart(
#     weekly.groupby(["time", "category"])
#     .reps.sum()
#     .reset_index()
#     .pivot(index="time", columns="category", values="reps")
#     .plot()
# )
# categories = weekly.category.unique()
# for cat in categories:
#     st.subheader(cat)

#     st.table(
#         weekly[weekly.category == cat].groupby(["month", "week"]).reps.sum().cumsum()
#     )


# # st.plotly_chart(
# #     overall_plan.groupby(["time", "category"])["reps"]
# #     .sum()
# #     .reset_index()
# #     .drop("category", axis=1)
# #     .set_index("time")
# #     .cumsum()
# #     .plot()
# # )
# # st.subheader("Detailed Plan")

# # st.table(
# #     overall_plan.drop(["volume", "time"], axis=1).set_index(["month", "week", "day"])
# # )
