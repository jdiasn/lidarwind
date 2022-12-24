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

    def update_settings(self):

        font_size = 16

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
        min_time=None,
        max_time=None,
    ):

        if plot_id == "rad_wind_speed_panel":

            tmp_data = self.data
            self.plot_data_azm(
                data_non_90=tmp_data,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                plot_id=plot_id,
                fig_path=fig_path,
                save=save,
                show=show,
                min_time=min_time,
                max_time=max_time,
            )

        else:
            tmp_data = Filtering(self.data).get_vertical_obs_comp(var_name)

            if name_prefix:
                std_name = tmp_data.attrs["standard_name"]
                string_name = f"{name_prefix}_{std_name}"

            else:
                string_name = tmp_data.attrs["standard_name"]

            self.plot_data(
                tmp_data=tmp_data,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax,
                elv=elv,
                azm=azm,
                save=save,
                plot_id=plot_id,
                string_name=string_name,
                fig_path=fig_path,
                min_time=min_time,
                max_time=max_time,
            )

    def view_ret_var(
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
        min_time=None,
        max_time=None,
    ):

        tmp_data = self.data[var_name]

        string_name = tmp_data.attrs["standard_name"]

        self.plot_data(
            tmp_data=tmp_data,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            elv=elv,
            azm=azm,
            save=save,
            plot_id=plot_id,
            string_name=string_name,
            fig_path=fig_path,
            show=show,
            min_time=min_time,
            max_time=max_time,
        )

    def plot_data(
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
        string_name=None,
        show=False,
        min_time=None,
        max_time=None,
    ):

        sel_day = pd.to_datetime(tmp_data.time[0].values)

        if max_time is not None:
            max_time = pd.to_datetime(max_time)

        else:
            max_time = pd.to_datetime(sel_day.strftime("%Y%m%d 23:59:59"))

        if min_time is not None:
            min_time = pd.to_datetime(min_time)

        else:
            min_time = pd.to_datetime(sel_day.strftime("%Y%m%d 00:00:00"))

        tmp_data = tmp_data.sel(time=slice(min_time, max_time))

        if string_name:
            tmp_data.attrs["standard_name"] = string_name

        plt.figure(figsize=(18, 8))
        plot = tmp_data.plot(x="time", cmap=cmap, vmin=vmin, vmax=vmax)
        plot = PlotSettings.plot_setup(plot)

        plt.grid(b=True)
        plt.ylim(0, 12e3)
        plt.xlim(min_time, max_time)
        plt.title(f"elv: {elv}, azm: {azm}")

        if plot_id == "hor_wind_dir":
            plot.colorbar.set_ticks(np.linspace(0, 360, 9))

        if save:
            sel_day_str = sel_day.strftime("%Y%m%d")
            file_name = f"{sel_day_str}_{plot_id}.png"
            output_file_name = os.path.join(fig_path, file_name)
            print(output_file_name)
            plt.savefig(output_file_name, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()

    def plot_data_azm(
        self,
        data_non_90,
        cmap="Spectral",
        vmin=-1,
        vmax=1,
        fig_path=None,
        save=False,
        plot_id=None,
        show=False,
        min_time=None,
        max_time=None,
    ):

        elv = data_non_90.elv.values[0]
        fig, axes = plt.subplots(5, 1, sharex=True, figsize=(18, 25))

        sel_day = pd.to_datetime(data_non_90.time[0].values)

        if max_time is not None:
            max_time = pd.to_datetime(max_time)

        else:
            max_time = pd.to_datetime(sel_day.strftime("%Y%m%d 23:59:59"))

        if min_time is not None:
            min_time = pd.to_datetime(min_time)

        else:
            min_time = pd.to_datetime(sel_day.strftime("%Y%m%d 00:00:00"))

        for ax_number, i in enumerate(data_non_90.azm.values):

            tmp_data = data_non_90.sel(azm=i)

            tmp_data = tmp_data.sel(time=slice(min_time, max_time))

            plot = tmp_data.plot(
                x="time", cmap=cmap, vmin=vmin, vmax=vmax, ax=axes[ax_number]
            )

            plot = PlotSettings.plot_setup(plot)

            axes[ax_number].grid(b=True)
            axes[ax_number].set_ylim(0, 12e3)
            axes[ax_number].set_xlim(min_time, max_time)
            axes[ax_number].set_title(f"elv: {elv}, azm: {i}")

        if save:
            sel_day_str = sel_day.strftime("%Y%m%d")
            file_name = f"{sel_day_str}_{plot_id}.png"
            output_file_name = os.path.join(fig_path, file_name)
            print(output_file_name)
            plt.savefig(output_file_name, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()
