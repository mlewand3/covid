import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.dates as dates
import matplotlib.ticker as ticker

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
months_fmt = mdates.DateFormatter('%M')

def get_values(text):
    first_val = text[text.find('arg: "') + len('arg: "'): text.find('},')]
    data = first_val[0: first_val.find('"')]
    tests = first_val[first_val.find('p_testy: ') + len('p_testy: '): first_val.find('p_testyl') - 1]
    tested_people = first_val[first_val.find('p_testyl: ') + len('p_testyl: '): first_val.find('p_chorzy') - 1]
    positive = first_val[first_val.find('p_chorzy: ') + len('p_chorzy: '): first_val.find('},')]
    data2 = data.split('.')
    data = data2[2] + '-' + data2[1] + '-' + data2[0]

    if float(tests) != 0:
        ratio = 100*float(positive)/float(tests)
    else:
        ratio = 0

    if float(tested_people) != 0:
        ratio_tested_people = 100*float(positive)/float(tested_people)
    else:
        ratio_tested_people = 0
    print(data, tests, positive, ratio, ratio_tested_people)

    return text[text.find('},') + len('},'):], np.datetime64(data, 'D'), ratio, ratio_tested_people, tests


def draw_plot(x_vals, y_vals, x_axis_label, y_axis_label):
    fig, ax = plt.subplots()
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)

    # data = [datas, ratios]
    ax.scatter(x_vals, y_vals, s=4)

    # format the ticks
    ax.xaxis.set_major_locator(dates.MonthLocator())
    # 16 is a slight approximation since months differ in number of days.
    ax.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))

    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))

    # round to nearest years.
    datemin = np.datetime64(datas[0], 'D')
    datemax = np.datetime64(datas[-1], 'D') + np.timedelta64(3, 'D')
    ax.set_xlim(datemin, datemax)
    fig.autofmt_xdate()


url = "https://koronawirusunas.pl/u/polska-testy-nowe"
response = requests.get(url, timeout=10000)
text = response.text.replace('null', '0')
# print(text)
begin = text.find('var Data_przyrost_testy = [') + len('var Data_przyrost_testy = [')
end = text.find('var TstartData = ')
# print(text[begin:end])
text, d, r, r_tested_people, tests = get_values(text[begin:end])
ratios = [r]
datas= [d]
tests_array = [int(tests)]
while len(text) > 10:
    text, d, r, r_tested_people, tests = get_values(text)
    ratios.append(r)
    datas.append(d)
    tests_array.append(tests)




draw_plot(datas, ratios, 'Data','Stosunek testów pozytywnych do wszystkich testów')
draw_plot(datas, tests_array, 'Data', 'Liczba wykonanych testów')
plt.show()


plt.show()
