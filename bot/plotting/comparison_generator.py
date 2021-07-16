import pybamm
import random
import logging
from utils.parameter_value_generator import parameter_value_generator
from plotting.plot_graph import plot_graph
from experiment.experiment_generator import experiment_generator


def comparison_generator(
    number_of_comp,
    models_for_comp,
    chemistry,
    provided_choice=None,
    provided_param_to_vary=None
):
    """
    Generates a random comparison plot.
    Parameters:
        number_of_comp: numerical
            Number of models be used in the comparison plot.
        models_for_comp: dict
            Different models that are to be used in the comparison plot.
        chemistry: dict
            A single chemistry value which will be used in the comparison
            plot.
        provided_choice: str
            default: None
            Should be used only during testing, using this one can test
            different parts of this function deterministically without relying
            on the random functions to execute that part.
        provided_param_to_vary: str
            default: None
            Should be used only during testing, using this one can test
            different parts of this function deterministically without relying
            on the random functions to execute that part.
    """
    parameter_values = pybamm.ParameterValues(chemistry=chemistry)
    parameter_values_for_comp = dict(list(enumerate([parameter_values])))
    comparison_dict = {}

    # logging configuration
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    while True:
        try:

            # generate a list of parameter values by varying a single parameter
            # if only 1 model is selected
            param_to_vary = None
            labels = []
            varied_values = []
            if number_of_comp == 1:

                param_to_vary_list = [
                    "Current function [A]",
                    "Electrode height [m]",
                    "Electrode width [m]",
                    "Negative electrode conductivity [S.m-1]",
                    "Negative electrode porosity",
                    "Negative electrode active material volume fraction",
                    "Negative electrode Bruggeman coefficient (electrolyte)",
                    "Negative electrode exchange-current density [A.m-2]",
                    "Positive electrode porosity",
                    "Positive electrode exchange-current density [A.m-2]",
                    "Positive electrode Bruggeman coefficient (electrolyte)",
                    "Ambient temperature [K]"
                ]

                if provided_param_to_vary is not None:
                    param_to_vary = provided_param_to_vary
                else:
                    param_to_vary = random.choice(param_to_vary_list)

                param_list = []
                diff_params = random.randint(2, 3)
                min_param_value = 100
                for i in range(0, diff_params):

                    # generate parameter values
                    if (
                        param_to_vary == "Electrode height [m]"
                        or param_to_vary == "Electrode width [m]"
                    ):
                        params, varied_value = parameter_value_generator(
                            parameter_values,
                            param_to_vary,
                            lower_bound=0
                        )
                    elif param_to_vary == "Ambient temperature [K]":
                        params, varied_value = parameter_value_generator(
                            parameter_values,
                            param_to_vary,
                            lower_bound=265,
                            upper_bound=355
                        )
                    else:
                        params, varied_value = parameter_value_generator(
                            parameter_values, param_to_vary
                        )
                    varied_values.append(varied_value)

                    logger.info(
                        param_to_vary + ": " + str(varied_value)
                    )

                    labels.append(param_to_vary + ": " + str(varied_value))

                    param_list.append(params.copy())

                    # find the minimum value if "Current function [A]"
                    # is varied
                    if param_to_vary == "Current function [A]":
                        if varied_value < min_param_value:
                            min_param_value = varied_value

                parameter_values_for_comp = dict(
                    list(enumerate(param_list))
                )

            # if testing, don't select simulations randomly
            if provided_choice is not None:
                choice = provided_choice
            else:
                choice_list = ["experiment", "no experiment"]
                choice = random.choice(choice_list)

            if choice == "no experiment":

                is_experiment = False

                # vary "Current function [A]" and "Ambient temperature [K]"
                # if comparing models with a constant discharge
                if number_of_comp != 1:
                    params, min_param_value = parameter_value_generator(
                        parameter_values, "Current function [A]"
                    )
                    (
                        final_params,
                        varied_value_temp
                    ) = parameter_value_generator(
                        params,
                        "Ambient temperature [K]",
                        lower_bound=265,
                        upper_bound=355
                    )
                    parameter_values_for_comp = dict(
                        list(enumerate([final_params]))
                    )

                batch_study = pybamm.BatchStudy(
                    models=models_for_comp,
                    parameter_values=parameter_values_for_comp,
                    permutations=True,
                )

                # if "Current function [A]" is varied, change the t_end
                if min_param_value != 100:
                    factor = min_param_value / parameter_values[
                        "Current function [A]"
                    ]
                    t_end = (1 / factor * 1.1) * 3600
                else:
                    # default t_end
                    t_end = 3700

                batch_study.solve([0, t_end])

            elif choice == "experiment":

                is_experiment = True

                # generate a random cycle and a number for experiment
                cycle = experiment_generator()
                number = random.randint(1, 3)

                # if testing, use the following configuration
                if provided_choice is not None:
                    cycle = [
                        (
                            "Discharge at C/10 for 10 hours "
                            + "or until 3.3 V",
                            "Rest for 1 hour",
                            "Charge at 1 A until 4.1 V",
                            "Hold at 4.1 V until 50 mA",
                            "Rest for 1 hour"
                        )
                    ]
                    number = 1

                experiment = dict(
                    list(
                        enumerate(
                            [
                                pybamm.Experiment(
                                    cycle * number
                                )
                            ]
                        )
                    )
                )

                batch_study = pybamm.BatchStudy(
                    models=models_for_comp,
                    parameter_values=parameter_values_for_comp,
                    experiments=experiment,
                    permutations=True,
                )

                if chemistry == pybamm.parameter_sets.Ai2020:
                    batch_study.solve(calc_esoh=False)
                else:
                    batch_study.solve()

            # find the max "Time [s]" from all the solutions for the GIF
            max_time = 0
            solution = batch_study.sims[0].solution
            for sim in batch_study.sims:
                if sim.solution["Time [s]"].entries[-1] > max_time:
                    max_time = sim.solution["Time [s]"].entries[-1]
                    solution = sim.solution

            # create the GIF
            if len(labels) == 0:
                plot_graph(
                    solution=solution, sim=batch_study.sims
                )
            else:
                plot_graph(
                    solution=solution, sim=batch_study.sims, labels=labels
                )

            comparison_dict.update({
                "model": models_for_comp,
                "chemistry": chemistry,
                "is_experiment": is_experiment,
                "cycle": cycle if is_experiment else None,
                "number": number if is_experiment else None,
                "is_comparison": True,
                "param_to_vary": param_to_vary,
                "varied_values": varied_values,
                "params": parameter_values_for_comp
            })

            return comparison_dict

        except Exception as e:  # pragma: no cover
            print(e)
