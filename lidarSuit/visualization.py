import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .filters import Filtering


class PlotSettings:
    def __init__(self, mpl, style="dark_background"):

        self.mpl = mpl
        self.style = style
        # self.update_settings()

    def update_settings(self):

        font_size = 16

        # mpl.style.use('seaborn')
        self.mpl.style.use(self.style)
        self.mpl.rcParams["figure.figsize"] = [6, 6]
        self.mpl.rcParams["figure.dpi"] = 80
        self.mpl.rcParams["savefig.dpi"] = 100

        self.mpl.rcParams["font.size"] = font_size
        self.mpl.rcParams["legend.fontsize"] = font_size
        self.mpl.rcParams["figure.titlesize"] = font_size

        self.mpl.rcParams["ytick.labelsize"] = font_size
        self.mpl.rcParams["xtick.labelsize"] = font_size
        self.mpl.rcParams["axes.titlesize"] = font_size
        self.mpl.rcParams["axes.labelsize"] = font_size

        self.mpl.rcParams["legend.fancybox"] = True
        self.mpl.rcParams["legend.framealpha"] = 0.7
        self.mpl.rcParams["legend.facecolor"] = "silver"
        self.mpl.rcParams["legend.frameon"] = True

        self.mpl.rcParams["lines.linewidth"] = 5

        return self

    def plot_setup(plot):

        plt.setp(plot.axes.xaxis.get_majorticklabels(), rotation=0)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        plot.axes.xaxis.set_major_formatter(formatter)

        plt.grid(b=True)

        return plot


class Visualizer:
    def __init__(self, data):

        self.data = data

    def view_orig_var(
        self,
        var_name,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plot_id=None,
        fig_path=None,
        name_prefix=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        if plot_id == "rad_wind_speed_panel":

            tmp_data = self.data
            self.plotDataAZM(
                dataNon90=tmp_data,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                plot_id=plot_id,
                fig_path=fig_path,
                save=save,
                show=show,
                minTime=minTime,
                maxTime=maxTime,
            )

        else:
            tmp_data = Filtering(self.data).get_vertical_obs_comp(var_name)

            if name_prefix:
                strName = "{}_{}".format(
                    name_prefix, tmp_data.attrs["standard_name"]
                )

            else:
                strName = tmp_data.attrs["standard_name"]

            self.plotData(
                tmp_data=tmp_data,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                elv=elv,
                azm=azm,
                save=save,
                plot_id=plot_id,
                strName=strName,
                fig_path=fig_path,
                show=show,
                minTime=minTime,
                maxTime=maxTime,
            )

    def viewRetVar(
        self,
        var_name,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plot_id=None,
        fig_path=None,
        name_prefix=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        tmp_data = self.data[var_name]

        strName = tmp_data.attrs["standard_name"]

        self.plotData(
            tmp_data=tmp_data,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            elv=elv,
            azm=azm,
            save=save,
            plot_id=plot_id,
            strName=strName,
            fig_path=fig_path,
            show=show,
            minTime=minTime,
            maxTime=maxTime,
        )

    def plotData(
        self,
        tmp_data,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        elv="90",
        azm="-",
        save=False,
        plot_id=None,
        fig_path=None,
        strName=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        sel_day = pd.to_datetime(tmp_data.time[0].values)

        if maxTime is not None:
            maxTime = pd.to_datetime(maxTime)

        else:
            maxTime = pd.to_datetime(sel_day.strftime("%Y%m%d 23:59:59"))

        if minTime is not None:
            minTime = pd.to_datetime(minTime)

        else:
            minTime = pd.to_datetime(sel_day.strftime("%Y%m%d 00:00:00"))

        tmp_data = tmp_data.sel(time=slice(minTime, maxTime))

        if strName:
            tmp_data.attrs["standard_name"] = strName

        plt.figure(figsize=(18, 8))
        plot = tmp_data.plot(x="time", cmap=cmap, vmin=vmin, vmax=vmax)
        plot = PlotSettings.plot_setup(plot)

        plt.grid(b=True)
        plt.ylim(0, 12e3)
        plt.xlim(minTime, maxTime)
        plt.title(f"elv: {elv}, azm: {azm}")

        if plot_id == "hor_wind_dir":
            plot.colorbar.set_ticks(np.linspace(0, 360, 9))

        if save:
            fileName = "{}_{}.png".format(sel_day.strftime("%Y%m%d"), plot_id)
            outputFileName = os.path.join(fig_path, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()

    def plotDataAZM(
        self,
        dataNon90,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        fig_path=None,
        save=False,
        plot_id=None,
        show=False,
        minTime=None,
        maxTime=None,
    ):

        elv = dataNon90.elv.values[0]
        fig, axes = plt.subplots(5, 1, sharex=True, figsize=(18, 25))

        sel_day = pd.to_datetime(dataNon90.time[0].values)

        if maxTime is not None:
            maxTime = pd.to_datetime(maxTime)

        else:
            maxTime = pd.to_datetime(sel_day.strftime("%Y%m%d 23:59:59"))

        if minTime is not None:
            minTime = pd.to_datetime(minTime)

        else:
            minTime = pd.to_datetime(sel_day.strftime("%Y%m%d 00:00:00"))

        for axN, i in enumerate(dataNon90.azm.values):

            tmp_data = dataNon90.sel(azm=i)

            tmp_data = tmp_data.sel(time=slice(minTime, maxTime))

            plot = tmp_data.plot(
                x="time", cmap=cmap, vmin=vmin, vmax=vmax, ax=axes[axN]
            )

            plot = PlotSettings.plot_setup(plot)

            axes[axN].grid(b=True)
            axes[axN].set_ylim(0, 12e3)
            axes[axN].set_xlim(minTime, maxTime)
            axes[axN].set_title(f"elv: {elv}, azm: {i}")

        if save:
            fileName = "{}_{}.png".format(sel_day.strftime("%Y%m%d"), plot_id)
            outputFileName = os.path.join(fig_path, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()
