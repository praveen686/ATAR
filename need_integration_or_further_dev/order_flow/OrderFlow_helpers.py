import numpy as np
import matplotlib.pyplot as plt

np.seterr(divide='ignore', invalid='ignore')
font = {'family': 'serif',
        'style': 'italic',
        # 'color': 'darkred',
        'weight': 1,
        'size': 16,
        }
def MakeHeatMap(t, y, fignum=False, nct=20, lower_threshold=0.1, upper_threshold=0.48):

    Nbins = 100

    miny = np.nanmin(y)
    maxy = np.nanmax(y)
    dy = (maxy - miny) / Nbins

    bins = np.linspace(miny, maxy, 100)


    myNdt = 200
    yr = np.full([myNdt, len(bins)], np.nan)

    mydt = (t[-1] - t[0]) / (myNdt - 1)

    tr = np.full([myNdt, ], np.nan)

    for i in range(myNdt):
        kk = np.where(t < t[0] + mydt * (i + 1))[-1][-1]
        count = np.histogram(y[:, kk], np.arange(miny, maxy + 0.00001, dy))
        yr[i, :] = count[0]
        tr[i] = t[kk].item()

    zr = yr.T / len(y[:, 0])

    if not fignum:
        fig = plt.figure()
    else:
        fig = plt.figure(fignum)
    plt.tick_params(direction='in', bottom=True, top=True, left=True, right=True)
    axes = fig.gca()
    axes.set_xlim(left=0)
    axes.set_ylim(bottom=0, top=np.max(maxy))
    x_cord_i, y_cord_i = np.meshgrid(tr, bins)

    zr[zr < np.max(zr)*lower_threshold] = 0
    zr[zr > np.max(zr)*upper_threshold] = np.max(zr)*upper_threshold
    cmap = plt.get_cmap('YlOrRd')
    #print(x_cord_i.shape)
    #print(y_cord_i.shape)
    #print(zr.shape)
    plt.contour(x_cord_i, y_cord_i, zr, nct, cmap=cmap, levels=np.linspace(zr.min(), zr.max(), 1000))

    lim = np.around(np.max(zr), int(np.around(-(np.log(0.10972799999999999)/np.log(10)))))
    plt.colorbar(ticks=np.arange(0, np.max(zr), lim/10))

    return [fig, tr, yr, zr]
def PlotPath(t, T, Y, idxfig, sigma, y_range, title, lw=1):
    fig_1 = plt.figure()
    plt.tick_params(direction='in', bottom=True, top=True, left=True, right=True)
    axes = fig_1.gca()
    axes.set_xlim([0, T])
    axes.set_ylim(y_range)

    for i in range(len(idxfig)):
        plt.plot(t, Y[idxfig[i]], linewidth=lw, label=i+1)

    plt.ylabel(title,  fontdict=font)
    plt.xlabel('Time (Day) ',  fontdict=font)
    plt.legend()
    plt.show()
def PlotHeatMap(t, Y, Y_AC, title, n=20, lower_threshold=0.1, upper_threshold=0.48):
    out = MakeHeatMap(t, Y, nct=n)
    [fig, tr, yr, zr] = out
    plt.plot(t, Y_AC, '--k')
    plt.ylabel(title,  fontdict=font)
    plt.xlabel('Time (Day) ',  fontdict=font)
    plt.show()