from ..wind_retrieval.fft_wind_retrieval import get_wind_properties


def get_horizontal_wind(ds):

    wind_ds = get_wind_properties(ds.MeanVel)
    wind_ds = wind_ds.merge(
        ds[
            [
                "start_scan",
                "end_scan",
                "zdr_max",
                "nan_percentual",
                "chirp_start",
                "chirp_end",
                "chirp_azimuth_bias",
                "azm_seq",
            ]
        ]
    )
    wind_ds = wind_ds.expand_dims(["mean_time"])

    return wind_ds
