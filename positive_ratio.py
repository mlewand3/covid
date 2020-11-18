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
        ratio = 100 * float(positive) / float(tests)
    else:
        ratio = 0

    if tested_people != 0:
        ratio_tested_people = 100 * positive / tested_people
    else:
        ratio_tested_people = 0
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

    return text[text.find('},') + len('},'):], np.datetime64(data, 'D'), death_recovered_ratio


def draw_plot(x_vals, y_vals, x_axis_label, y_axis_label, label):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlabel(x_axis_label)
    ax.set_ylabel(y_axis_label)

    # data = [datas, ratios]
    ax.scatter(x_vals, y_vals, color='blue', s=4, label='Surowe dane')
    ax.plot(x_vals, moving_average(5, y_vals), color='red', alpha=1, label='Średnia z 5 dni')
    plt.axvline(x=np.datetime64('2020-11-04', 'D'), label='Konferencja ws lockdownu', c='black', linestyle=':')
    plt.axvline(x=np.datetime64('2020-07-01', 'D'), label='Koronawirus "w odwrocie"', c='orange', linestyle=':')
    plt.legend(bbox_to_anchor=(0., -0.4, 1., 0.), loc='lower left')

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
    fig.suptitle(label)
    plt.subplots_adjust(None, 0.27)


def moving_average(step, arr):
    averaged = []
    for i, val in enumerate(arr):
        if (i - step) > 0:
            # print(arr[i-step:i+1])
            subarray_avg = np.mean(arr[i - step:i + 1])
        else:
            # print(arr[0:i+1])
            subarray_avg = np.mean(arr[0:i + 1])

        averaged.append(subarray_avg)
    # print(averaged)
    # print(len(averaged))
    # print(len(tests_array))
    return averaged


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
print(response.text)
text = response.text.replace('null', '0')
begin = text.find('var populationData = [') + len('var populationData = [')
end = text.find('var startData = ')
text, d, deaths_recovered_ratio = get_deaths_recovered_values(text[begin:end])
dr_ratios = [deaths_recovered_ratio]
datas2 = [d]

while len(text) > 10:
    text, d, deaths_recovered_ratio = get_deaths_recovered_values(text)
    dr_ratios.append(deaths_recovered_ratio)
    datas2.append(d)

draw_plot(datas, ratios, 'Data', 'Udział wyników pozytywnych [%]', 'Stosunek testów pozytywnych do wszystkich testów')
draw_plot(datas, tests_array, 'Data', 'Liczba testów', 'Liczba dziennie wykonanych testów')
draw_plot(datas, new_cases, 'Data', 'Liczba zakażeń', 'Liczba dziennie wykrytych zakażeń')
draw_plot(datas2, dr_ratios, 'Data', 'Liczba zmarłych / liczba wyleczonych',
          'Stosunek liczby zmarłych do wyleczonych - dziennie')

plt.show()
