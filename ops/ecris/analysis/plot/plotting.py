import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from ops.ecris.analysis.model import CSD

def plot_csd(csd: CSD) -> Figure:
    if csd.m_over_q is None:
        raise RuntimeError('CSD m_over_q is not set, estimate or scale the value before plotting')
    fig = plt.figure(figsize=(9,6), tight_layout=True)
    ax = fig.gca()
    plt.plot(csd.m_over_q, csd.beam_current)
    ax.set_title(csd.timestamp)
    ax.set_xlabel('M/Q')
    ax.set_ylabel(r'current [$\mu$A]')
    return fig
