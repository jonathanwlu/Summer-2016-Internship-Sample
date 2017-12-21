import pandas
import matplotlib.pyplot as plt
import os
import math


def chunks(list, n):
    # l is a list
    # yield successive n-sized chunks from list l

    if len(list) % n != 0:
        raise ValueError('number of elements in list must be a multiple of n')

    for i in xrange(0, len(list), n):
        yield list[i:i + n]


def custom_round(q, dir=None):
    # ex. round up to nearest billion - custom_round(1234567890, 'up')
    base = pow(10, math.floor(math.log10(abs(q))))
    if dir == 'up':
        return int(base * math.ceil(float(q) / base))
    elif dir == 'down':
        return int(base * math.floor(float(q) / base))
    else:
        return int(base * round(float(q)/base))


def bar_coord(patch):
    # each element in a bar chart is a graphical element called a patch
    # this returns the actual value corresponding to the bar, its easier to get it from the bar object
    if patch.get_y() < 0:
        return patch.get_y()
    else:
        return patch.get_height()

		
def gen_image_line(data, detailed_labels, title, ylabel, filepath, filename, colors=None, squeeze=False):
    # squeeze = true sets the y-axis scale such that it is near the min and max y values
    # detailed labels is the legend labels
    # colors = ['g', 'r'] for green -> red -> green cycle, etc
    # can use either letter (rgbcmykw) or color names (http://matplotlib.org/examples/color/named_colors.html)
    plt.close('all')
    fig, ax = plt.subplots(1, 1, figsize=(7.25, 4.5))

    if colors:
        ax.set_color_cycle(colors)

    data.plot(ax=ax)

    ax.set_title(title, fontsize=8, family='sans-serif')
    ax.set_xlabel('', visible=False)
    ax.legend(detailed_labels, loc='best', fontsize=8, frameon=False)
    ax.set_ylabel(ylabel, fontsize=8, family='sans-serif')
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8, right=True) # right = true draws the y-axis tick marks on the right
    ax.grid(b=True, which='both', color='0.65', linestyle='-')  # b=True turns on the axis grids
    hline = ax.axhline(linewidth=2, color='black')  # makes the x-axis darker

    if squeeze:
        ax.set_ylim([custom_round(data.values.min(), 'down'), custom_round(data.values.max(), 'up')])

    annotations = []
    for line in ax.lines:
        if line is not hline:
            xdata, ydata = line.get_data()
            annotations.append((ydata[-1], line.get_c(), ydata[-1]))  # data, color, annotation y coord
    annotations.sort() # sorts on data

    ymin, ymax = ax.get_ylim()  # range of max and min for the axis
    offset = (ymax - ymin) / 32  # 32 works for this font size and chart height

    # figure out the y coordinates of the annotations
    for i in range(1, len(annotations)):  # start at the second one and move everything else up accordingly
        if annotations[i][2] - annotations[i - 1][2] < offset:  # check if the annotations are sufficiently far apart
            annotations[i] = (annotations[i][0], annotations[i][1], annotations[i - 1][2] + offset)  # move this annotation up a little

    # write the annotations
    for j in annotations:
        ax.annotate(s=round(j[0], 1), xy=(1, j[2]), xytext=(4, 0), xycoords=('axes fraction', 'data'), textcoords='offset points', fontsize=8, color=j[1])
        # xytext how far the annotation is offset from the position, in this case, 4 to the right

    attrib_figure_path = filepath + filename + ".png"
    fig.savefig(attrib_figure_path, dpi=300)
    return attrib_figure_path


def gen_image_bar(data, detailed_labels, title, ylabel, filepath, filename, colors=None):
    # see gen_image_line
    plt.close('all')
    fig, ax = plt.subplots(1, 1, figsize=(7.25, 4.5))

    if colors:
        ax.set_color_cycle(colors)

    data.plot(ax=ax, kind='bar')

    ax.set_title(title, fontsize=8, family='sans-serif')
    ax.set_xlabel('', visible=False)
    ax.set_ylabel(ylabel, fontsize=8, family='sans-serif')
    ax.legend(detailed_labels, fontsize=8, bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0, frameon=False)
    # loc is the anchor point on the legend - 2 is top left
    # bbox_to_anchor sets the top left corner of the legend

    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8, right=True)
    ax.grid(b=True, which='both', color='0.65', linestyle='-')

    ymin, ymax = ax.get_ylim()  # range of max and min for the axis
    offset = (ymax - ymin) / 25  # 25 works for this font size and chart height
    datapoints = [bar_coord(patch) for patch in ax.patches]
    ax.set_ylim(min(datapoints) - offset * 4, max(datapoints) + offset * 4)  # make sure this is enough buffer for the annotations
    sorted_patches = sorted(ax.patches, key=lambda k: k.get_x())

    for group in chunks(sorted_patches, 3):
        pos_annotations = []
        neg_annotations = []
        xloc = group[0].get_x()

        # positive and negative reference points to start the annotations
        pos_yloc = max([bar_coord(patch) for patch in group])
        neg_yloc = min([bar_coord(patch) for patch in group])
        for patch in group:
            ydata = bar_coord(patch)

            if ydata >= 0:
                pos_annotations.append((ydata, patch.get_fc(), xloc, pos_yloc))  # data, color, annotation x coord, annotation y coord
            else:
                neg_annotations.append((ydata, patch.get_fc(), xloc, neg_yloc))

        # set positions of hte annotations
        if len(neg_annotations) > 0:
            neg_annotations[0] = (neg_annotations[0][0], neg_annotations[0][1], neg_annotations[0][2], neg_annotations[0][3] - offset)

            for i in range(1, len(neg_annotations)):
                neg_annotations[i] = (neg_annotations[i][0], neg_annotations[i][1], neg_annotations[i][2], neg_annotations[i - 1][3] - offset)

        if len(pos_annotations) > 0:
            pos_annotations[0] = (pos_annotations[0][0], pos_annotations[0][1], pos_annotations[0][2], pos_annotations[0][3] + offset / 2)

            for i in range(1, len(pos_annotations)):
                pos_annotations[i] = (pos_annotations[i][0], pos_annotations[i][1], pos_annotations[i][2], pos_annotations[i - 1][3] + offset)

        # annotate
        for j in neg_annotations:
            # decimals are set in the round here
            ax.annotate(s=round(j[0], 1), xy=(j[2], j[3]), xytext=(0, -2), xycoords=('data', 'data'), textcoords='offset points', fontsize=8, color=j[1])

        for j in pos_annotations:
            ax.annotate(s=round(j[0], 1), xy=(j[2], j[3]), xytext=(0, 2), xycoords=('data', 'data'), textcoords='offset points', fontsize=8, color=j[1])

    plt.gcf().subplots_adjust(bottom=0.15, right=0.8)  # adjusts margins

    attrib_figure_path = filepath + filename + ".png"
    fig.savefig(attrib_figure_path, dpi=300)
    return attrib_figure_path
