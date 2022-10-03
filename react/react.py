import discord
import random
import os


async def reaction(ctx, roll_result, final_result=''):
    print(list_average(roll_result))
    if final_result != '':
        await call_ability_reaction(ctx, roll_result, final_result)
        return
    await call_reaction(ctx, roll_result)


async def call_ability_reaction(ctx, roll_result, final_result):
    if how_to_react(roll_result) == 0:
        return
    elif how_to_react(roll_result) == 'positive' and final_result == 'PASS':
        await positive_reaction(ctx, roll_result)
    elif how_to_react(roll_result) == 'negative' and final_result == 'FAIL':
        await negative_reaction(ctx, roll_result)
    else:
        return


def how_to_react(roll_result):
    # No reaction
    if avg_roll(roll_result):
        return 0
    return positive_negative(roll_result)


async def call_reaction(ctx, roll_result):
    if how_to_react(roll_result) == 0:
        return
    elif how_to_react(roll_result) == 'positive':
        await positive_reaction(ctx, roll_result)
    elif how_to_react(roll_result) == 'negative':
        await negative_reaction(ctx, roll_result)
    else:
        return


async def positive_reaction(ctx, roll_result):
    if insane_roll(roll_result):
        print('insane roll!')
        await send_positive_reaction(ctx)
        return
    if random.random() < 0.25:
        await send_positive_reaction(ctx)


async def send_positive_reaction(ctx):
    file = random.choice(os.listdir('react/positive'))
    await ctx.send(file=discord.File('react/positive/' + file))


async def negative_reaction(ctx, roll_result):
    if very_bad_roll(roll_result):
        print('very bad roll...')
        await send_negative_reaction(ctx)
        return
    if random.random() < 0.25:
        await send_negative_reaction(ctx)


async def send_negative_reaction(ctx):
    file = random.choice(os.listdir('react/negative'))
    await ctx.send(file=discord.File('react/negative/' + file))


def avg_roll(roll_result):
    if 5 <= list_average(roll_result) <= 15:
        if 1 not in roll_result and 20 not in roll_result:
            return True
    return False


def insane_roll(roll_result):
    if list_average(roll_result) < 5 and 1 in roll_result:
        return True
    return False


def very_bad_roll(roll_result):
    if list_average(roll_result) > 13.6 and 20 in roll_result:
        return True
    return False


def list_average(array):
    try:
        return round(sum(array) / len(array), 2)
    except ZeroDivisionError:
        return 0


def positive_negative(roll_result):
    if list_average(roll_result) < 5.8:
        return 'positive'
    elif list_average(roll_result) > 13:
        return 'negative'
