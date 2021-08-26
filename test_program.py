import logging

import program as p

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


def test_build_workout():
    _ex = p.ExerciseConfig("dips", "bw", "push", 16)
    _ex2 = p.ExerciseConfig("Overhead Press", "kb", "push", 16)
    ex = p.Exercise(_ex)
    ex2 = p.Exercise(_ex2)
    mo = p.Motion([_ex, _ex2])

    assert ex.build_workout(5) is not None
    for reps, weight in ex.build_workout(5):
        assert reps < 7

    total_reps = 0

    for reps, weight in ex2.build_workout(20):
        assert weight % 4 == 0
        total_reps += reps
        print(reps, weight)

    assert total_reps >= 20
    # this needs fixing

    assert mo.build_workout(10) is not None
    print(mo.build_workout(10))


def test_debug_test_workout():
    e1 = p.ExerciseConfig("Overhead Press", "kb", "push", 16)
    e = p.Exercise(e1)

    sets = e.build_workout(20)
    print(sets)
    for reps, weight in sets:
        assert weight % 4 == 0

    print(e._work_vol_distribution(20))


def test_relative_intensity():
    weight = 16
    rel_intensity = 0.75
    rel_int_weight = 12

    assert p.calc_intensity_percentage(rel_int_weight, weight) == rel_intensity

    assert p.calc_weight_at_percentage(rel_int_weight, weight) == rel_intensity


def test_kb_conversion():
    assert p.convert_to_kettlebell(16) == 16
    assert p.convert_to_kettlebell(17) == 16
    assert p.convert_to_kettlebell(18) == 20
    assert p.convert_to_kettlebell(19) == 20

    assert p.convert_to_kettlebell(12) == 12
    assert p.convert_to_kettlebell(13) == 12
    assert p.convert_to_kettlebell(15) == 16
    assert p.convert_to_kettlebell(14) == 16


def test_program():
    _ex = p.ExerciseConfig("dips", "bw", "push", 16)
    _ex2 = p.ExerciseConfig("Overhead Press", "kb", "push", 16)
    ex = p.Exercise(_ex)
    ex2 = p.Exercise(_ex2)
    mo = p.Motion([_ex, _ex2])
    pr = p.Program([mo])

    pr.get_percentage_plan()

    print(pr.get_nl_plan())


def test_program_2():
    _ex = p.ExerciseConfig("dips", "bw", "push", 16)
    _ex2 = p.ExerciseConfig("Overhead Press", "kb", "pull", 16)
    mo = p.Motion([_ex])
    mo2 = p.Motion([_ex2])
    pr = p.Program([mo, mo2])

    pr.get_percentage_plan()

    p2 = pr.get_nl_plan()
    print(p2.columns)
    print(p2.head())
