# parameters used in simplified SEIR model
# all durations in days

class Const():
    # incubation time 
    t_inc = 5.2

    # time a person is infectious before being quarantined
    t_inf = 3

    # time before patient is hospitalized
    t_hlag = 5

    # duration of a mild case
    t_mild = 11

    # time spend in hospital non-ic
    t_hosp = 7

    # time spend in ic
    t_ic = 21
    
    # time before patient dies of COVID19
    t_fatal = 21
    # proportion mild cases
    p_mild = 0.8

    # proportion of cases that require hospitalization
    p_hosp_0 = 0.145

    # proportion of cases that require ic
    p_ic_0 = 0.055

    # mortality rate
    p_fatal = 0.02

    # proportion of fatalities from ic
    p_fatal_ic = 0.5
