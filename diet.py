import diet as d
import plotille as plt
from enum import Enum

def to_kg(lbs):
    return lbs * 0.453592

def to_lbs(kg):
    return kg / 0.453592

def arr_to_lbs(arr):
    return [to_lbs(x) for x in arr]

def to_inches(cm):
    return cm / 2.54

def to_cm(inches):
    return inches * 2.54

def calc_bmr(kg, cm=to_cm(77), age=43, sex='m'):
    """
    Basal Metabolic Rate using Miffin-St Jeor Equation
     
    kg: weight in kilograms
    cm: height
    sex: 'm' or 'f'
    age: in
    """
    if sex == 'm':
        return 10 * kg + 6.25 * cm - 5 * age + 5
        #return 13.7 * kg + 5 * cm - 6.8 * age + 66
    if sex == 'f':
        return 10 * kg + 6.25 * cm - 5 * age - 161
    raise ValueError('sex: m|f only')

class Activity(Enum):
    SEDENTARY = 1.2
    LIGHT = 1.375
    MODERATE = 1.55
    VERY = 1.725
    EXTRA = 1.9

def calc_tdee(bmr, activity=Activity.LIGHT.value):
    """
    Total Daily Energy Expenditure
    """
    return bmr * activity

def steady_state_weight(calories, activity, height=to_cm(77), gender='m', age=43):
    """
    Reverse BMR to find weight given calories
    """
    L = activity
    if gender=='m':
        wt = calories /  L - (6.25 * height - 5 * age + 5)
        wt = wt / 10
        return wt
    if gender == 'f':
        wt = calories /  L - (6.25 * height - 5 * age - 161)
        wt = wt / 10
        return wt
    raise ValueError('sex: m|f only')

bmr = calc_bmr(100, 200, 43, 'm')
print(f"Your BMR is {bmr} calories per day.")

tdee = calc_tdee(bmr, Activity.SEDENTARY.value)
print(f"Your TDEE is {tdee} calories per day.")

target_cal = tdee - 300
print(f"Your target calories is {target_cal} calories per day.")

ssw = to_lbs(steady_state_weight(tdee, Activity.SEDENTARY.value))
print(f"Your steady state weight w/ 1.2 and tdee calories is {ssw} lbs.")
ssw =to_lbs( steady_state_weight(tdee*1.1, Activity.SEDENTARY.value))
print(f"Your steady state weight w/ sedentary, tdee and a snack is {ssw} lbs.")

ssw = to_lbs(steady_state_weight(target_cal, Activity.LIGHT.value))
print(f"Your steady state weight w/ light activity is {ssw} lbs.")

ssw = to_lbs(steady_state_weight(target_cal, Activity.SEDENTARY.value))
print(f"Your steady state weight w/ sedentary is {ssw} lbs.")

ssw = to_lbs(steady_state_weight(target_cal*1.1, Activity.SEDENTARY.value))
print(f"Your steady state weight w/ sedentary and a snack is {ssw} lbs.")


boxing_cal = calc_tdee( calc_bmr(to_kg(205), 200, 35, 'm'), Activity.VERY.value)
print(f"Your boxing days calories is {boxing_cal} calories per day.")
boxing_cal = calc_tdee( calc_bmr(to_kg(205), to_cm(77), 35, 'm'), Activity.EXTRA.value)
print(f"Your boxing days calories may have been {boxing_cal} calories per day.")

def wt_change_kg(tdee, calories):
    return (calories - tdee) / 7700

def predict_wt(days, calories, ht, age, wt0, activity=Activity.SEDENTARY.value):
    """
    Given you want to cut calories by calorie_cut below your starting BMR, over
    the range of days, what will your weight be?
    """
    wts = [wt0]
    for _ in range(1, days):
        current_wt = wts[-1]
        bmr = calc_bmr(current_wt, ht, age, 'm')
        tdee = activity * bmr
        dwt = wt_change_kg(tdee, calories)
        wts.append( wts[-1] + dwt) 
    return wts

def plotxy(x,y):
    import plotille as plt
    fig = plt.Figure()
    fig.width = 40
    fig.height = 10
    fig.plot(x, y)
    print(fig.show())

wts = [ to_lbs(x) for x in predict_wt(365*3, 2100, to_cm(77), 43, to_kg(222))]
print("Predicted weight over 3 years, using predict_wt")
plotxy(range(0, 365*3), wts)

import numpy as np
def weight_over_time(days, calories, 
                     ht, age, wt0, 
                     activity=Activity.SEDENTARY.value):
    """
    Given you want to consume `calories` per day, over the range of days, what
    will your weight be?
    """
    SSW = steady_state_weight(calories, activity, ht, 'm', age)
    t = np.arange(0, days)
    exparr = np.exp(-10*activity/7700 * t)
    res = SSW + exparr * (wt0-SSW)
    return res

wtsde = [ to_lbs(x) for x  in weight_over_time(365*3, 2100, to_cm(77), 43, to_kg(222), Activity.SEDENTARY.value)]
print("Predicted weight over 3 years, using weight_over_time")
plotxy(range(0, 365*3), wtsde)
ssw = to_lbs(steady_state_weight(2100, Activity.SEDENTARY.value, to_cm(77), 'm', 43))

f1 = plt.Figure()
f1.width = 60
f1.height = 20
f1.set_y_limits(min_=.9*ssw, max_=230)
f1.set_x_limits(min_=0, max_=365*3)
f1.plot(range(0, 365*3), wtsde, lc='red', label='Weight (Predicted)')
f1.plot(range(0, 365*3), [ssw]*365*3, lc='blue', label='Steady State Weight')
print(f1.show(legend=True))


def predict_calories_to_lose(days, wt0, wt_target, ht, age, activity=Activity.SEDENTARY.value):
    """
    Given you want to lose `wt0 - wt_target` lbs in `days`, what should your
    daily calorie intake be?
    """
    C_e = np.exp(-10*activity/7700 * days)
    C_p = (6.25 * ht - 5 * age + 5) / 10
    return 10 * activity * (wt0 - (wt0 - wt_target) / (1 - C_e) + C_p)

caltolose = predict_calories_to_lose(365*3, to_kg(222), to_kg(200), to_cm(77), 43)
print(f"Calories to lose 22 lbs in 3 years: {caltolose}")
check_caltolose = weight_over_time(365*3, caltolose, to_cm(77), 43, to_kg(222))
print(f"Check: {check_caltolose[-5:-1]}")

caltolose = predict_calories_to_lose(90, to_kg(222), to_kg(200), to_cm(77), 43)
print(f"Calories to lose 22 lbs in 3 months: {caltolose}")
check_caltolose = weight_over_time(90, caltolose, to_cm(77), 43, to_kg(222))
print(f"Check: {check_caltolose[-5:-1]}")
plotxy(range(0, 90), check_caltolose)


## Compare activity levels

sed = arr_to_lbs(weight_over_time(300, 2100, to_cm(77), 43, to_kg(222), Activity.SEDENTARY.value))
lt  = arr_to_lbs(weight_over_time(300, 2100, to_cm(77), 43, to_kg(222), Activity.LIGHT.value))
md  = arr_to_lbs(weight_over_time(300, 2100, to_cm(77), 43, to_kg(222), Activity.MODERATE.value))

def approx_floor(min_, _):
    return f'>{int(min_)}'
f1 = plt.Figure()
f1.width = 60
f1.height = 20
f1.set_y_limits(min_=180, max_=230)
f1.set_x_limits(min_=0, max_=300)
f1.x_ticks_fkt = approx_floor
f1.y_ticks_fkt = approx_floor
f1.plot(range(0, 300), sed, lc='red', label='Sedentary')
f1.plot(range(0, 300, 30), sed[::30], lc='red', marker='o')
f1.plot(range(0, 300), lt, lc='blue', label='Light')
f1.plot(range(0, 300, 30), lt[::30], lc='blue', marker='+')
f1.plot(range(0, 300), md, lc='green', label='Moderate')
f1.plot(range(0, 300, 30), md[::30], lc='green', marker='x')
f1.plot(range(0, 300), [200]*300, lc='white', label='Goal')
print(f1.show(legend=False))


def predict_days_to_weight(wt_target, calories, wt0, 
                           ht, age, activity=Activity.SEDENTARY.value):
    """
    Given you want to hit `wt_target` lbs on a diet of `calories` per day and
    activity level `activity`, how many days will it take?
    """
    SSW = steady_state_weight(calories, activity, ht, 'm', age)
    numerator = wt_target - SSW
    denominator = wt0 - SSW
    return -7700/(10*activity) * np.log(numerator/denominator)

print("you have 158 days!")
Days=158
Start = to_kg(222)
End = to_kg(190)
Diff = End - Start
dayssed = predict_days_to_weight(End, 2100, Start, to_cm(77), 43, Activity.SEDENTARY.value)
print(f"SED Days to lose {to_lbs(Diff):0.1f} lbs on 2100 calories per day: {dayssed:0.2f}")
dayslight = predict_days_to_weight(End, 2100, Start, to_cm(77), 43, Activity.LIGHT.value)
print(f"LIGHT Days to lose {to_lbs(Diff):0.1f} lbs on 2100 calories per day: {dayslight:0.2f}")
daysmod = predict_days_to_weight(End, 2100, Start, to_cm(77), 43, Activity.MODERATE.value)
print(f"MOD Days to lose {to_lbs(Diff):0.1f} lbs on 2100 calories per day: {daysmod:0.2f}")
print()
dayssed = predict_days_to_weight(End, 1800, Start, to_cm(77), 43, Activity.SEDENTARY.value)
print(f"SED Days to lose {to_lbs(Diff):0.1f} lbs on 1800 calories per day: {dayssed:0.2f}")
dayslight = predict_days_to_weight(End, 1800, Start, to_cm(77), 43, Activity.LIGHT.value)
print(f"LIGHT Days to lose {to_lbs(Diff):0.1f} lbs on 1800 calories per day: {dayslight:0.2f}")
daysmod = predict_days_to_weight(End, 1800, Start, to_cm(77), 43, Activity.MODERATE.value)
print(f"MOD Days to lose {to_lbs(Diff):0.1f} lbs on 1800 calories per day: {daysmod:0.2f}")
print()
calsed = predict_calories_to_lose(158, Start, End, to_cm(77), 43, Activity.SEDENTARY.value)
calslight = predict_calories_to_lose(158, Start, End, to_cm(77), 43, Activity.LIGHT.value)
calsmod = predict_calories_to_lose(158, Start, End, to_cm(77), 43, Activity.MODERATE.value)
print(f"SED Calories to lose {to_lbs(Diff):0.1f} lbs in 158 days: {calsed:0.2f}")
print(f"LIGHT Calories to lose {to_lbs(Diff):0.1f} lbs in 158 days: {calslight:0.2f}")
print(f"MOD Calories to lose {to_lbs(Diff):0.1f} lbs in 158 days: {calsmod:0.2f}")



