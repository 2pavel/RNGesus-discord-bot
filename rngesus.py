import discord
import os
import random
import re
import math
import react.react as react

from dotenv import load_dotenv
from discord.ext import commands

from player_characters import puszek
from player_characters import wilk
from player_characters import mateo
from player_characters import jimmy
import modifiers

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

intents = discord.Intents.all()
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(
        f'{bot.user} has connected to the following server:\n'
        f'{guild.name}(id {guild.id})\n'
    )

    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Guild Members:\n - {members}')


@bot.command(name='roll')
async def roll(ctx):
    if len(ctx.message.content) > 5:
        roll_parameters = ctx.message.content[6:]
        await process_parameters(roll_parameters, ctx)
    else:
        roll_result = standard_roll()
        await ctx.send('`' + str(roll_result) + '`')
        await react.reaction(ctx, roll_result)


def standard_roll():
    roll_result = []
    for i in range(3):
        roll_result.append(random.randint(1, 20))
    return roll_result


async def process_parameters(roll_parameters, ctx):
    print(roll_parameters, '<- process_parameters')
    try:
        if type(int(roll_parameters[0])) == int:
            await custom_diceroll(roll_parameters, ctx)
    except ValueError:
        await process_ability_roll(roll_parameters, ctx)


async def custom_diceroll(roll_parameters, ctx):
    split_parameters = re.split('d', roll_parameters, 1)
    number_of_dice = int(split_parameters[0])
    try:
        number_of_sides = int(split_parameters[1])
    except IndexError as e:
        print(e)
        await ctx.send('Invalid parameters. List index out of range.')
        return

    await custom_diceroll_response(ctx, number_of_dice, number_of_sides)


async def custom_diceroll_response(ctx, number_of_dice, number_of_sides):
    dice_array = []
    if not 0 < number_of_dice <= 100 or not 0 < number_of_sides <= 1000:
        await ctx.send('Sam se to rollnij :clown:')
        return
    for dice in range(number_of_dice):
        dice_array.append(random.randint(1, number_of_sides))
    avg = list_average(dice_array)
    await ctx.send('`' + str(dice_array) + f'`\nAverage: {round(avg, 2)}')


async def process_ability_roll(roll_parameters, ctx):
    tested_ability = grab_ability(roll_parameters)
    ability_roll_data = []
    roll_result = standard_roll()
    player = await assign_player(ctx)
    for stat in player.abilities:
        for ability, ability_value in player.abilities[stat].items():
            if ability == tested_ability:
                modifier = grab_modifier(roll_parameters, ability_value, roll_result)
                ability_roll_data = [ability, ability_value, stat[:2], player.stats[stat[:2]], modifier, player]

    if not ability_roll_data:
        await ctx.send('Ability not found.')
        return

    await ability_diceroll(ability_roll_data, roll_result, ctx)


# Ability roll data = [ability, ability value, stat, stat value, modifier, player]
# Ex: [0]perswazja, [1]4, [2]ch, [3]15, [4]-5, Puszek means:
# 4 punkty perswazji, 15 punktów charakteru, modyfikator -5 (trudny), postać: Puszek


async def ability_diceroll(ability_roll_data, roll_result, ctx):
    print('ability diceroll was called')
    ability_name, ability_points = ability_roll_data[0], ability_roll_data[1]
    stat_name, stat_points = ability_roll_data[2], ability_roll_data[3]
    modifier = ability_roll_data[4]
    player = ability_roll_data[5]

    success_points = calculate_success_points(roll_result, stat_points, ability_points, modifier)
    total = total_positive_points(success_points)
    final_result = pass_check(success_points)
    difficulty_name = grab_difficulty_name(modifier)
    await ability_roll_message(ctx, player, difficulty_name, ability_name, ability_points, modifier,
                               stat_name, stat_points, roll_result, success_points, total, final_result)
    await react.reaction(ctx, roll_result, final_result)


async def ability_roll_message(ctx, player, difficulty_name, ability_name, ability_points, modifier,
                               stat_name, stat_points, roll_result, success_points, total, final_result):
    diff_slider = determine_diff_slider(ability_points, roll_result)
    plus = ''
    if modifier >= 0:
        plus = '+'
    if diff_slider == 0:
        await ctx.send(
            f'```{player.nickname} wykonuje {difficulty_name} test - {ability_name}:\n'
            f'{stat_name.upper()}: {stat_points}{plus}{modifier} = {stat_points + modifier}\n'
            f'{ability_name.upper()}: {ability_points}'
            f'\n\nRoll: {roll_result}\nSuccess rate: {success_points}\nTotal success points: {total}\n\n'
            f'RESULT:   {final_result}```'
        )
    else:

        if diff_slider < 0:
            up_down = 'w górę'
        else:
            up_down = 'w dół'
        await ctx.send(
            f'```{player.nickname} wykonuje {difficulty_name} test - {ability_name}:\n'
            f'{stat_name.upper()}: {stat_points}{plus}{modifier} = {stat_points + modifier}\n'
            f'{ability_name.upper()}: {ability_points}\n'
            f'Suwak o {abs(diff_slider)} {up_down}.'
            f'\n\nRoll: {roll_result}\nSuccess rate: {success_points}\nTotal success points: {total}\n\n'
            f'RESULT:   {final_result}```'
        )


async def assign_player(ctx):
    match ctx.message.author.id:
        case 123456789:
            return puszek
        case 111222333:
            return mateo
        case 999666333:
            return jimmy
        case 512321513:
            return wilk
        case _:
            return wilk


def calculate_success_points(roll_result, stat_points, ability_points, modifier):
    success_points = []
    for dice in roll_result:
        success_points.append(stat_points - dice + modifier)
    success_points = apply_ability_points(success_points, ability_points)
    return success_points


def apply_ability_points(success_points, ability_points):
    closest_to_success_index = find_closest_to_success(success_points)
    while ability_points > 0:
        success_points[closest_to_success_index] += 1
        ability_points -= 1
        closest_to_success_index = find_closest_to_success(success_points)
    return success_points


def find_closest_to_success(success_points):
    closest_to_success = 38  # Can't go lower: Lowest stat - highest modifier - worst roll = |6 - 24 - 20| = 38
    closest_to_success_index = 0
    for i, pts in enumerate(success_points):
        if pts >= 0:
            continue
        if closest_to_success > abs(pts):
            closest_to_success = abs(pts)
            closest_to_success_index = i
    return closest_to_success_index


def pass_check(success_points):
    success_dice = 0
    for points in success_points:
        if points >= 0:
            success_dice += 1
    if success_dice >= 2:
        return 'PASS'
    else:
        return 'FAIL'


def grab_modifier(roll_parameters, ability_points, roll_result):
    modifier = 'no_mod'
    if ' ' in roll_parameters:
        modifier = re.split(' ', roll_parameters, 1)[1]
    if modifier in modifiers.modifiers:
        diff_slider = determine_diff_slider(ability_points, roll_result)
        modifier = apply_diff_slider(modifier, diff_slider)
    else:
        modifier = 0
    return modifier


def determine_diff_slider(ability_points, roll_result):
    diff_slider = math.floor(ability_points / 4)
    if ability_points == 0:
        diff_slider -= 1
    for dice in roll_result:
        if dice == 1:
            diff_slider += 1
        elif dice == 20:
            diff_slider -= 1
    return diff_slider


def apply_diff_slider(modifier, diff_slider):
    diff_index = 0
    for i, val in enumerate(modifiers.modifiers_list):
        if val[0] == modifier:
            diff_index = i
    diff_index -= diff_slider
    if diff_index < 0:
        diff_index = 0
    modifier = modifiers.modifiers_list[diff_index][1]
    return modifier


def grab_difficulty_name(modifier):
    for diff_name, mod_value in modifiers.test_level.items():
        if modifier == mod_value:
            return diff_name
    return 'Failed to grab difficulty_name from test_level'


def grab_ability(roll_parameters):
    ability = re.split(' ', roll_parameters, 1)[0]
    return ability


def total_positive_points(success_points):
    total = 0
    for points in success_points:
        if points > 0:
            total += points
    return total


def list_average(array):
    try:
        return round(sum(array) / len(array), 2)
    except ZeroDivisionError:
        return 0


@bot.command(name='fight')
async def fight(ctx, ability='bijatyka'):
    roll_result = standard_roll()
    player = await assign_player(ctx)
    dexterity = player.stats['zr']
    ability_points = player.abilities['zr_abilities'][ability]
    success_points = []

    for dice in roll_result:
        success_points.append(dexterity - dice)
    await ctx.send(
        f'```{player.nickname} - fight commencing!\n\n'
        f'ZR: {dexterity}\n'
        f'{ability.upper()}: {ability_points}\n\n'
        f'Roll: {roll_result}\n'
        f'Success rate: {success_points}```'
    )


@bot.command(name='FIGHT')
async def fight_2(ctx):
    await fight(ctx, 'br')


@bot.command(name='flirt')
async def flirt(ctx):
    file = 'random_img/flirt.png'
    await ctx.send(file=discord.File(file))


@bot.listen()
@commands.dm_only()
async def on_message(ctx):
    if type(ctx.channel) == discord.channel.DMChannel:
        print(ctx.author.name, end=' ')
        print(ctx.author.id)
        print(ctx.content)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == 'hi':
        response = 'Hello!'
        await message.channel.send(response)

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('`Command not found.`')
        return
    if ctx.message.content[:9].lower() == f'{bot.command_prefix}fight' and len(ctx.message.content) > 8:
        await ctx.send('`No parameters available for fight, only rage and pain.`')


@bot.event
async def on_error(event, *args):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        elif event == 'roll':
            f.write(f'Unhandled roll: {args[0]}\n')
        else:
            raise


@bot.command(name='bot')
async def discord_help(ctx):
    await ctx.send(f'```Available commands:\n\n'
                   f'{bot.command_prefix}roll - standard 3d20 roll.\n'
                   f'{bot.command_prefix}roll XdY - roll X dice, Y sided each.\n'
                   f'{bot.command_prefix}roll [ability] [level].\n'
                   f'{bot.command_prefix}fight - bijatyka.\n'
                   f'{bot.command_prefix}FIGHT - broń ręczna.\n```')


bot.run(TOKEN)
print('RNGesus ready to mess with Players.')

# TODO: Overall cleanup, docstrings, look into methods with 3+ arguments and try refactoring using *args
