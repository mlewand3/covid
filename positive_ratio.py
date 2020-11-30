import datetime
import requests
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.dates as dates
import matplotlib.ticker as ticker


def get_tests_values(text):
    first_val = text[text.find('arg: "') + len('arg: "'): text.find('},')]
    data = first_val[0: first_val.find('"')]
    tests = int(first_val[first_val.find('p_testy: ') + len('p_testy: '): first_val.find('p_testyl') - 1])
    tested_people = int(first_val[first_val.find('p_testyl: ') + len('p_testyl: '): first_val.find('p_chorzy') - 1])
    positive = int(first_val[first_val.find('p_chorzy: ') + len('p_chorzy: '): first_val.find('},')])
    data2 = data.split('.')
    data = data2[2] + '-' + data2[1] + '-' + data2[0]

    if tests != 0:
        ratio = 100.0 * float(positive) / float(tests)
    else:
        ratio = 0.0

    if tested_people != 0:
        ratio_tested_people = 100.0 * positive / tested_people
    else:
        ratio_tested_people = 0.0
    print(data, tests, positive, ratio, ratio_tested_people)

    return text[text.find('},') + len('},'):], np.datetime64(data, 'D'), ratio, ratio_tested_people, tests, positive


def get_deaths_recovered_values(text):
    first_val = text[text.find('arg: "') + len('arg: "'): text.find('},')]
    data = first_val[0: first_val.find('"')]
    sick = int(first_val[first_val.find('p_chorzy: ') + len('p_chorzy: '): first_val.find('p_zgony') - 1])
    deaths = int(first_val[first_val.find('p_zgony: ') + len('p_zgony: '): first_val.find('p_wyleczeni') - 1])
    recovered = int(first_val[first_val.find('p_wyleczeni: ') + len('p_wyleczeni: '): first_val.find('},')])
    data_arr = data.split('.')
    data = data_arr[2] + '-' + data_arr[1] + '-' + data_arr[0]

    if recovered != 0:
        death_recovered_ratio = 100 * float(deaths) / int(recovered)
    else:
        death_recovered_ratio = 0

    print(data, sick, deaths, recovered, death_recovered_ratio)

    return text[text.find('},') + len('},'):], np.datetime64(data, 'D'), death_recovered_ratio, deaths


def draw_plot(x_vals, y_vals, x_axis_label: str, y_axis_label: str, label: str, ax: plt.Axes):
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)

    ax.scatter(x_vals, y_vals, color='blue', s=4, label='Surowe dane')
    ax.plot(x_vals, moving_average(y_vals), color='red', alpha=1, label='Średnia z 5 dni')
    ax.axvline(x=np.datetime64('2020-11-04', 'D'), label='Konferencja ws lockdownu', c='black', linestyle=':')
    ax.axvline(x=np.datetime64('2020-07-01', 'D'), label='Koronawirus "w odwrocie"', c='orange', linestyle=':')
    ax.legend(bbox_to_anchor=(0., -0.4, 1., 0.), loc='upper left')

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
    ax.set_title(label)



def moving_average(arr, step=5):
    return np.convolve(arr, np.ones(step)/step, 'same')


years = mdates.YearLocator()  # every year
months = mdates.MonthLocator()  # every month
months_fmt = mdates.DateFormatter('%M')

url = "https://koronawirusunas.pl/u/polska-testy-nowe"
response = requests.get(url, timeout=10000)
text = response.text.replace('null', '0')
begin = text.find('var Data_przyrost_testy = [') + len('var Data_przyrost_testy = [')
end = text.find('var TstartData = ')

text, d, r, r_tested_people, tests, positive = get_tests_values(text[begin:end])

ratios = [r]
datas = [d]
tests_array = [tests]
new_cases = [positive]

while len(text) > 10:
    text, d, r, r_tested_people, tests, positive = get_tests_values(text)
    ratios.append(r)
    datas.append(d)
    tests_array.append(tests)
    new_cases.append(positive)

url_deaths = "https://koronawirusunas.pl/u/polska-nowe"
response = requests.get(url_deaths, timeout=10000)
text = response.text.replace('null', '0')
begin = text.find('var populationData = [') + len('var populationData = [')
end = text.find('var startData = ')
text, d, deaths_recovered_ratio, deaths = get_deaths_recovered_values(text[begin:end])
dr_ratios = [deaths_recovered_ratio]
death_daily = [deaths]
datas2 = [d]

while len(text) > 10:
    text, d, deaths_recovered_ratio, deaths = get_deaths_recovered_values(text)
    dr_ratios.append(deaths_recovered_ratio)
    datas2.append(d)
    death_daily.append(deaths)

fig, axes = plt.subplots(figsize=(12, 12), nrows=3, ncols=2)
draw_plot(datas, ratios, 'Data', 'Udział wyników pozytywnych [%]', 'Stosunek testów pozytywnych do wszystkich testów',
          axes[0, 0])
draw_plot(datas, tests_array, 'Data', 'Liczba testów', 'Liczba dziennie wykonanych testów', axes[0, 1])
draw_plot(datas, new_cases, 'Data', 'Liczba zakażeń', 'Liczba dziennie wykrytych zakażeń', axes[1, 0])
draw_plot(datas2, dr_ratios, 'Data', 'Liczba zmarłych / liczba wyleczonych',
          'Stosunek liczby zmarłych do wyleczonych - dziennie', axes[1, 1])
draw_plot(datas2, death_daily, 'Data', 'Liczba zgonów',
          'Liczba zgonów - dziennie', axes[2, 0])

fig.autofmt_xdate()

txt = (f'Dane z {datas[-1]}\n'
       f'Liczba testów: {tests_array[-1]}\n'
       f'Liczba zakażeń: {new_cases[-1]}\n'
       f'Liczba zgonów: {death_daily[-1]}\n'
       f'Stosunek wyników pozytywnych: {ratios[-1]:.3f}%\n'
       f'Stosunek zgonów do wyzdrowień: {dr_ratios[-1]:.3f}\n'
       )

axes[2, 1].text(0.1, 0.9, txt, verticalalignment='top', transform=axes[2, 1].transAxes)

#plt.subplots_adjust(None, 0.27)

now = str(datetime.datetime.now())
for c in [':', '.', '-']:
    now = now.replace(c, '')
now = now.replace(' ', '_')
plt.savefig(f'corona_{now}.png', bbox_inches='tight')
#plt.show()

