from random import sample, choice


def advchoice(items):
    item_list = sample(items, 2)
    item_choice = choice(item_list)
    return item_choice
