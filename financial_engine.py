import numpy as np
import pandas as pd

def future_value(present, inflation, years):
    return present * (1 + inflation) ** years


# ----------------------------
# Retirement Corpus (Growing SWP Model)
# ----------------------------
def retirement_corpus(expense_today, inflation, years_to_ret, post_ret_return, retirement_years=30):

    expense_at_ret = future_value(expense_today, inflation, years_to_ret)

    r = post_ret_return
    g = inflation

    if r == g:
        corpus = expense_at_ret * retirement_years
    else:
        corpus = expense_at_ret * (1 - ((1 + g) / (1 + r)) ** retirement_years) / (r - g)

    return corpus, expense_at_ret


# ----------------------------
# Year-by-Year Sustainability Table
# ----------------------------
def retirement_projection(corpus, expense_at_ret, inflation, post_ret_return, years=30):

    data = []
    current_corpus = corpus
    expense = expense_at_ret

    for year in range(1, years + 1):

        opening = current_corpus
        growth = opening * post_ret_return
        closing = opening + growth - expense

        data.append([year, opening, expense, growth, closing])

        current_corpus = closing
        expense *= (1 + inflation)

    df = pd.DataFrame(data, columns=["Year", "Opening Corpus", "Withdrawal", "Growth", "Closing Corpus"])
    return df


# ----------------------------
# Sequence Risk Model
# ----------------------------
def sequence_risk_projection(corpus, expense_at_ret, inflation, post_ret_return, years=30, shock=-0.20):

    data = []
    current_corpus = corpus
    expense = expense_at_ret

    for year in range(1, years + 1):

        opening = current_corpus

        if year == 1:
            growth = opening * shock
        else:
            growth = opening * post_ret_return

        closing = opening + growth - expense

        data.append([year, opening, expense, growth, closing])

        current_corpus = closing
        expense *= (1 + inflation)

    df = pd.DataFrame(data, columns=["Year", "Opening Corpus", "Withdrawal", "Growth", "Closing Corpus"])
    return df
