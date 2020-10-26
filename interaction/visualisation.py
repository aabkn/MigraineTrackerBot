import datetime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import calendar
from config import messages


def generate_calendar(chat_id, lang, full_data, month, year):
    plt.switch_backend('Agg')
    fig, ax = plt.subplots(figsize=(6, 5.5))
    start = datetime.datetime(year, month, 1)
    dates = [start + datetime.timedelta(days=i) for i in range(calendar.monthrange(year, month)[1])]
    weeks, days = zip(*[d.isocalendar()[1:] for d in dates])
    first_week = min(weeks)
    weeks = np.array(weeks) - first_week
    days = np.array(days) - 1
    nweeks = max(weeks) + 1

    calendar_grid = np.nan * np.zeros((nweeks, 7))
    calendar_grid_unfilled = np.nan * np.zeros((nweeks, 7))

    for entry in full_data:
        week, day = entry['date'].isocalendar()[1:]
        if entry.get('intensity') is None:
            calendar_grid_unfilled[week - first_week, day - 1] = -1
        else:
            calendar_grid[week - first_week, day - 1] = entry['intensity']

    calendar_heatmap(ax, dates, weeks, days, calendar_grid, calendar_grid_unfilled)

    fig.suptitle(f'{messages.month_names[lang][month]} {year}')
    file_name = f'/tmp/{chat_id}_calendar_{month}_{year}'
    fig.savefig(file_name, bbox_inches='tight')
    return f'{file_name}.png'


def calendar_heatmap(ax, dates, weeks, days, calendar_grid, calendar_grid_unfilled):
    colors_range = [(0, '#900A22'), (0.3, '#f00b07'), (0.5, '#ff880b'), (0.6, '#FCE205'), (1., '#9dff49')]
    cm = LinearSegmentedColormap.from_list('RdGn', colors_range)
    cm_unfilled = ListedColormap(['#b0bec5'])

    ax.imshow(calendar_grid_unfilled, cmap=cm_unfilled)
    im = ax.imshow(calendar_grid, interpolation='none', vmin=0, vmax=10, cmap=cm.reversed('RdGn')) #'RdYlGn_r')

    label_days(ax, dates, weeks, days, calendar_grid)
    ax.figure.colorbar(im, orientation='horizontal', pad=0.05, shrink=0.9)


def label_days(ax, dates, weeks, days, calendar_grid):
    ni, nj = calendar_grid.shape
    day_of_month = np.nan * np.zeros((ni, 7))
    day_of_month[weeks, days] = [d.day for d in dates]

    for (i, j), day in np.ndenumerate(day_of_month):
        if np.isfinite(day):
            ax.text(j, i, int(day), ha='center', va='center')

    ax.set(xticks=np.arange(7),
           xticklabels=['M', 'T', 'W', 'R', 'F', 'S', 'S'])
    ax.xaxis.tick_top()
    ax.tick_params(which="major", top=False, left=False, right=False, bottom=False)
    ax.tick_params(which="minor", top=False, left=False, right=False, bottom=False)

    ax.set_xticks(np.arange(calendar_grid.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(calendar_grid.shape[0] + 1) - .5, minor=True)
    ax.set_yticklabels([])
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)

    ax.spines['bottom'].set_color('w')
    ax.spines['top'].set_color('w')
    ax.spines['right'].set_color('w')
    ax.spines['left'].set_color('w')
