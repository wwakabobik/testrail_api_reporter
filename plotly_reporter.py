import csv
from datetime import datetime

import plotly

# Set path to orca for plotly
plotly.io.orca.config.executable = '/usr/local/bin/orca'


class PlotlyReporter:
    def __init__(self, debug=True, pr_colors=None, pr_labels=None, ar_colors=None, lines=None):
        print("\nPlotly Reporter init")
        self.__debug = debug
        self.__pr_labels = pr_labels if pr_labels else ['Low', 'Medium', 'High', 'Critical']
        self.__pr_colors = pr_colors if pr_colors else ['rgb(173,216,230)', 'rgb(34,139,34)', 'rgb(255,255,51)',
                                                        'rgb(255, 153, 153)']
        self.__ar_colors = ar_colors if ar_colors else ['rgb(255, 153, 153)', 'rgb(255,255,51)', 'rgb(34,139,34)',
                                                        'rgb(173,216,230)', 'rgb(65,105,225)', 'rgb(192, 192, 192)']
        self.__lines = lines if lines else ({'color': 'rgb(0,0,51)', 'width': 1.5})

    def __load_history_data(self, filename, debug=None):
        debug = debug if debug is not None else self.__debug
        timestamps = []
        totals = []
        automateds = []
        not_automateds = []
        nas = []
        if debug:
            print('Loading history data from {}'.format(filename))
        with open(filename, 'r') as csvfile:
            for row in (csv.reader(csvfile)):
                timestamps.append(datetime(year=int(row[0]), month=int(row[1]), day=int(row[2])))
                totals.append(row[3])
                automateds.append(row[4])
                not_automateds.append(row[5])
                nas.append(row[6])
        return [timestamps, totals, automateds, not_automateds, nas]

    def draw_automation_state_report(self, filename, reports, state_markers=None, debug=None):
        debug = debug if debug is not None else self.__debug
        data = []
        axis_x = []
        axis_y_automated = []
        axis_y_not_automated = []
        axis_y_na = []

        for report in reports:
            axis_x.append(report.get_name())
            axis_y_automated.append(report.get_automated())
            axis_y_not_automated.append(report.get_not_automated())
            axis_y_na.append(report.get_na())

        if not state_markers:
            state_markers = {'Automated': {'marker': dict(color='rgb(34,139,34)',
                                                          line=dict(color='rgb(0,0,51)', width=1.5)),
                                           'opacity': 0.6, 'textposition': 'auto'},
                             'Not automated': {'marker': dict(color='rgb(255, 153, 153)',
                                                              line=dict(color='rgb(0,0,51)', width=1.5)),
                                               'opacity': 0.6, 'textposition': 'auto'},
                             'N/A': {'marker': dict(color='rgb(192, 192, 192)',
                                                    line=dict(color='rgb(0,0,51)', width=1.5)),
                                     'opacity': 0.6, 'textposition': 'auto'}}

        data.append(plotly.graph_objs.Bar(x=axis_x,
                                          y=axis_y_automated,
                                          text=axis_y_automated,
                                          name='Automated',
                                          textposition=state_markers['Automated']['textposition'],
                                          marker=state_markers['Automated']['marker'],
                                          opacity=state_markers['Automated']['opacity']
                                          )
                    )
        data.append(plotly.graph_objs.Bar(x=axis_x,
                                          y=axis_y_not_automated,
                                          text=axis_y_not_automated,
                                          name='Not automated',
                                          textposition=state_markers['Not automated']['textposition'],
                                          marker=state_markers['Not automated']['marker'],
                                          opacity=state_markers['Not automated']['opacity']
                                          )
                    )
        data.append(plotly.graph_objs.Bar(x=axis_x,
                                          y=axis_y_na,
                                          text=axis_y_na,
                                          name='N/A',
                                          textposition=state_markers['N/A']['textposition'],
                                          marker=state_markers['N/A']['marker'],
                                          opacity=state_markers['N/A']['opacity']
                                          )
                    )

        layout = plotly.graph_objs.Layout(barmode='stack')
        if debug:
            print('Drawing chart to file {}'.format(filename))
        fig = plotly.graph_objs.Figure(data=data, layout=layout)
        plotly.io.write_image(fig, filename)

    def draw_test_case_by_priority(self, filename, pr_values, pr_labels=None, pr_colors=None,
                                   lines=None, debug=None):
        pr_labels = pr_labels if pr_labels else self.__pr_labels
        pr_colors = pr_colors if pr_colors else self.__pr_colors
        debug = debug if debug is not None else self.__debug
        lines = lines if lines else self.__lines
        fig = {
            'data': [
                {
                    'values': pr_values,
                    'labels': pr_labels,
                    'domain': {'column': 0},
                    'name': 'Test cases by priority',
                    'hoverinfo': 'label+percent+name',
                    'textinfo': 'value+percent',
                    'type': 'pie',
                    'marker': {'colors': pr_colors,
                               'line': lines},
                },
            ]
        }
        if debug:
            print('Drawing chart to file {}'.format(filename))
        plotly.io.write_image(fig, filename)

    def draw_test_case_by_area(self, filename, cases, ar_colors=None, lines=None, debug=None):
        # priority distribution
        debug = debug if debug is not None else self.__debug
        ar_colors = ar_colors if ar_colors else self.__ar_colors
        lines = lines if lines else self.__lines
        # area distribution
        ar_labels = []
        ar_values = []
        for case in cases:
            ar_labels.append(case.get_name())
            ar_values.append(case.get_total())

        fig = {
            'data': [
                {
                    'values': ar_values,
                    'labels': ar_labels,
                    'domain': {'column': 0},
                    'name': 'Test cases by area',
                    'hoverinfo': 'label+percent+name',
                    'textinfo': 'value+percent',
                    'type': 'pie',
                    'marker': {
                        'colors': ar_colors,
                        'line': lines},
                },
            ]
        }

        if debug:
            print('Drawing chart to file {}'.format(filename))
        plotly.io.write_image(fig, filename)

    def draw_history_state_chart(self, chart_name, history_data=None, filename=None, debug=None, trace1_decor=None,
                                 trace2_decor=None):
        debug = debug if debug is not None else self.__debug
        filename = filename if filename else 'current_automation_{}.csv'.format(chart_name.replace(' ', '_'))
        trace1_decor = trace1_decor if trace1_decor else {'fill': 'tonexty',
                                                          'line': dict(width=0.5, color='rgb(255, 153, 153)')}
        trace2_decor = trace2_decor if trace2_decor else {'fill': 'tozeroy',
                                                          'line': dict(width=0.5, color='rgb(34,139,34)')}
        history_data = history_data if history_data else self.__load_history_data(filename=filename, debug=debug)
        trace1 = plotly.graph_objs.Scatter(
            x=history_data[0],
            y=history_data[1],
            fill=trace1_decor['fill'],
            name='Total',
            line=trace1_decor['line'],
        )
        trace2 = plotly.graph_objs.Scatter(
            x=history_data[0],
            y=history_data[2],

            fill=trace2_decor['fill'],
            name='Automated',
            line=trace2_decor['line'],
        )

        data = [trace1, trace2]
        fig = {'data': data}
        filename = '{}png'.format(filename[:-3])
        if debug:
            print('Drawing chart to file {}'.format(filename))
        plotly.io.write_image(fig, filename)
        return filename

    def draw_history_type_chart(self, filename, type_platforms, ar_colors=None, lines=None, debug=None):
        data = []
        ar_colors = ar_colors if ar_colors else self.__ar_colors
        lines = lines if lines else self.__lines
        debug = debug if debug is not None else self.__debug
        index = 0
        for platform in type_platforms:
            type_name = platform['name']
            history_filename = 'current_area_distribution_{}.csv'.format(type_name.replace(' ', '_'))
            history_data = self.__load_history_data(debug=debug, filename=history_filename)
            data.append(plotly.graph_objs.Scatter(
                    x=history_data[0],
                    y=history_data[1],
                    name=type_name,
                    marker=dict(color=ar_colors[index], line=lines)
            ))
            index += 1
        fig = {'data': data}
        if debug:
            print('Drawing chart to file {}'.format(filename))
        plotly.io.write_image(fig, filename)
