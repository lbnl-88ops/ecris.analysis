from collections import deque
from itertools import compress

import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle

from ops.ecris.analysis.model import Element


def plot_element_markers(
    element: Element,
    marker: str = "v",
    fraction_y: float = 0.5,
    x_space_required: int = 35,
):
    ax = plt.gca()
    labels = []
    q_values = range(1, element.atomic_number + 1)
    m_over_q = [element.atomic_mass / q for q in q_values]
    mask = [mq < 10 for mq in m_over_q]
    q_values = list(compress(q_values, mask))
    m_over_q = list(compress(m_over_q, mask))
    y_min, y_max = ax.get_ylim()
    x_min, x_max = ax.get_xlim()
    height = y_max * fraction_y
    y_offset = 0.02 * abs(y_max - y_min)
    x_min = ax.transData.transform((x_min, 0))[0]
    x_max = ax.transData.transform((x_max, 0))[0]
    new_system_loc = ax.transData.transform((0, height))
    new_axes_loc = ax.transAxes.inverted().transform(new_system_loc)
    label_height = new_axes_loc[1]
    (ln,) = ax.plot(
        m_over_q,
        [height] * len(m_over_q),
        marker=marker,
        ms=10,
        ls="",
        markeredgecolor="black",
        animated=True,
    )

    last_visible = None
    for x, q in zip(m_over_q, q_values):
        artist_loc = ax.transData.transform((x, 0))[0]
        if x_min < artist_loc < x_max:
            if (
                last_visible is not None
                and abs(artist_loc - last_visible) < x_space_required
            ):
                continue
            last_visible = artist_loc

            txt = ax.text(
                x,
                height + y_offset,
                f"{q}",
                animated=True,
                c="black",
                ha="center",
                va="bottom",
                weight="bold",
                clip_on=True,
            )

    element_artist = ax.text(
        1.01,
        label_height,
        f"{element.symbol}-{element.atomic_mass}",
        transform=ax.transAxes,
        weight="bold",
        animated=True,
        color=ln.get_color(),
    )
