import numpy as np

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years

def retirement_corpus(expense_today, inflation, years_to_ret, post_ret_return):
    expense_at_ret = future_value(expense_today, inflation, years_to_ret)
    corpus = expense_at_ret / post_ret_return
    return corpus, expense_at_ret

def monte_carlo_simulation(initial_corpus, withdrawal, mean_return, std_dev, years, simulations=1000):
    success = 0

    for _ in range(simulations):
        corpus = initial_corpus
        for year in range(years):
            annual_return = np.random.normal(mean_return, std_dev)
            corpus = corpus * (1 + annual_return) - withdrawal
            if corpus <= 0:
                break
        if corpus > 0:
            success += 1

    return success / simulations
