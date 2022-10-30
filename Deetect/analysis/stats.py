import numpy as np

from matplotlib import pyplot as plt
import seaborn as sns
from statannotations.Annotator import Annotator

import utils


def transform_df(df):
    method_index = len(df.columns) - 3
    df_hue = df.melt(id_vars=df.columns[:method_index],
                     var_name="Method",
                     value_name="Cell count")
    return df_hue


def seaborn_grouped_plot(df, base_path, test, graph_type, hue="Group", sort=None, ):
    order_hue = df[hue].unique()
    if len(order_hue) == 0:
        raise ValueError(' Statistics could not be applied because there is no group!')
    elif len(order_hue) == 1:
        raise ValueError('Statistics could not be applied because there is only one group!')
    elif len(order_hue) == 2:
        seaborn_2groups_plot(df, base_path, test, graph_type, hue, sort)
    elif len(order_hue) == 3:
        raise ValueError(f' Too many groups! : {len(order_hue)}')
        #seaborn_3groups_plot(df, base_path, 'kruskal-wallis', graph_type, hue, sort)


def seaborn_2groups_plot(df, base_path, test, graph_type, hue="Group", sort=None, ):
    # apply statistics
    write_descriptive_stats_to_file(df, base_path)
    df = transform_df(df)
    df.sort_values(by=sort, inplace=True)
    x = "Method"
    y = "Cell count"
    order_method = df[x].unique()
    order_hue = df[hue].unique()
    pairs = [
        [(order_method[0], order_hue[0]), (order_method[0], order_hue[1])],
        [(order_method[1], order_hue[0]), (order_method[1], order_hue[1])],
        [(order_method[2], order_hue[0]), (order_method[2], order_hue[1])]
    ]

    hue_plot_params = {
        'data': df,
        'x': x,
        'y': y,
        "order": order_method,
        "hue": hue,
        "hue_order": order_hue,
        "palette": "Set2",
        "showfliers": False,
        "showmeans": True,
        "meanprops": {"marker": "X", "markerfacecolor": "k", "markeredgecolor": "k"}
    }
    sns.set(style="white")

    # Calculate number of obs per group
    nobs = df.groupby([hue]).count() / len(order_method)
    nobs = ["n= " + str(int(x)) for x in nobs[x].tolist()]
    legend_text = []
    for t, n in zip(df[hue].unique(), nobs):
        legend_text.append(t + ' ' + n)

    ax = get_ax()
    if graph_type == 'box':
        ax = sns.boxplot(ax=ax, **hue_plot_params)
    elif graph_type == 'violin':
        ax = sns.violinplot(ax=ax, **hue_plot_params)

    # Add annotations
    annotator = Annotator(ax, pairs, **hue_plot_params)
    annotator.configure(test=test).apply_and_annotate()
    write_test_result_to_file(base_path, annotator)
    ax = edit_graph(ax, legend_text)
    ax.set(title=f'{x} per {hue} ({test})')
    plt.savefig(f'{base_path}/plot_{graph_type}_test_{test}_grouped_by_{hue}.png')

    # plt.show()


def seaborn_3groups_plot(df, base_path, test, graph_type, hue="Group", sort=None, ):
    # TODO to generate fig11 in paper,
    #  1-filter df, select only Elimination results
    #  apply two level grouping, F-W and I-M-A
    #  apply Kruskal-Wallis-test and post hoc Dunn’s test
    return True


def get_ax():
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    fig.patch.set_alpha(1)
    return ax


def edit_graph(g1, legend_text):
    g1.set(xlabel=None)
    handles, _ = g1.get_legend_handles_labels()
    g1.legend(handles, legend_text)
    return g1


def write_descriptive_stats_to_file(data, base_path):
    method_index = len(data.columns) - 3
    methods = data.columns[method_index:]
    grouped = data.groupby(data.columns[0])
    stats_grp = grouped[methods].agg([np.size, np.mean, np.std])
    # TODO append mode but for each loading one time
    fout_st = open(base_path + '/stats.txt', "a")
    fout_st.write(f'\n----------------------------------------------------------------------------------------'
                  f'\n{utils.get_formatted_datetime()}')
    fout_st.write("\n#### Descriptive statistics for all image sequences\n\n")
    fout_st.write(f'{stats_grp.to_string()}\n')
    fout_st.close()


def write_test_result_to_file(base_path, annotator):
    fout_st = open(base_path + '/stats.txt', "a")
    for anno in annotator.annotations:
        if anno.data.pvalue > anno.data.alpha:
            interpret = 'Same distribution (fail to reject H0)'
        else:
            interpret = 'Different distribution (reject H0)'
        fout_st.write(f'\n{"_".join(anno.data.group1)} vs. {"_".join(anno.data.group2)}\n')
        fout_st.write(f'{anno.formatted_output}, {interpret}\n')
    fout_st.close()
