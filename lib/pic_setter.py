# Function

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

def pic_setting(width = 4.5, height = 4.5, font_size = 9, **kwargs):
    def _decode_kwargs(kwargs):
        right = kwargs.get("right", True)
        top = kwargs.get("top", True)
        x_min = kwargs.get("x_min", -1)
        x_max = kwargs.get("x_max", 1)
        y_min = kwargs.get("y_min", -1)
        y_max = kwargs.get("y_max", 1)
        x_major_locator = kwargs.get("x_major_locator", 1)
        x_minor_locator = kwargs.get("x_minor_locator", 1)
        y_major_locator = kwargs.get("y_major_locator", 1)
        y_minor_locator = kwargs.get("y_minor_locator", 1)
        x_label = kwargs.get("x_label", "")
        y_label = kwargs.get("y_label", "")
        title = kwargs.get("title", "")
        return right, top, x_min, x_max, y_min, y_max, x_major_locator, x_minor_locator, y_major_locator, y_minor_locator, x_label, y_label, title
    
    def _set_ticks_and_spines(
            ax, right, top, x_min, x_max, y_min, y_max, 
            x_major_locator, x_minor_locator, y_major_locator, y_minor_locator, 
            x_label, y_label, title
            ):
        # font
        plt.rcParams["font.family"] = "Times New Roman"
        plt.rcParams["font.size"] = font_size
        
        # title
        ax.set_title(title)

        # ticks
        ax.minorticks_on()
        ax.grid(True, which="major", alpha=0.35, linewidth=0.6)
        ax.grid(True, which="minor", alpha=0.15, linewidth=0.35)
        ax.tick_params(direction="in", which="major", right=right, top=top, length=2.5, width=0.7)
        ax.tick_params(which="minor", left = False, bottom = False, right=False, top=False)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.xaxis.set_major_locator(MultipleLocator(x_major_locator))
        ax.xaxis.set_minor_locator(MultipleLocator(x_minor_locator))
        ax.yaxis.set_major_locator(MultipleLocator(y_major_locator))
        ax.yaxis.set_minor_locator(MultipleLocator(y_minor_locator))
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        #spines
        ax.spines["top"].set_visible(top)
        ax.spines["right"].set_visible(right)
        # ensure spines are rendered below plotted data so lines appear above axes
        for sp in ax.spines.values():
            try:
                sp.set_zorder(0)
            except Exception:
                pass

    fig, ax = plt.subplots(figsize=(width / 2.54, height / 2.54), dpi=700)
    _set_ticks_and_spines(ax, *_decode_kwargs(kwargs))
    ax.set_axisbelow(True)
    ax.margins(x=0, y=0)
    fig.tight_layout(pad=0.2)
    # ax.legend(loc="upper left", bbox_to_anchor=(0, 1), fontsize=font_size, borderpad = 0.1)

    return fig, ax