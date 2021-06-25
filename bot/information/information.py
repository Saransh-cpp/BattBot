def information(
    chemistry,
    model,
    solver,
    is_experiment,
    cycle,
    number,
    is_comparison
):
    """
    Generates tweet text.
    Parameters:
        chemistry: dict
        model: pybamm.BaseModel
        solver: pybamm.BaseSolver
        is_experiment: bool
        cycle: list
        number: numerical
        is_comparison: bool
    Returns
        tweet_text: str
    """

    if is_experiment:
        tweet_text = (
            str(cycle)
            + " * "
            + str(number)
            + " "
            + str(model.name)
            + " "
            + str(chemistry["citation"])
        )
        return tweet_text

    elif is_comparison:
        tweet_text = str(chemistry["citation"])
        return tweet_text
    else:
        tweet_text = (
            str(model.name)
            + " "
            + str(chemistry["citation"])
            + " "
            + str(solver)
        )
        return tweet_text
