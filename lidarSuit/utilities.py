import pandas as pd 

class util:
    
    """
    This class contains useful tools
    """

    def getTimeBins(selDay, freq='10min'):
    
        start = selDay.strftime('%Y%m%d')
        startTime = pd.to_datetime('{0} 00:00:00'.format(start))

        end = (selDay+pd.to_timedelta(1, 'D')).strftime('%Y%m%d')
        endTime = pd.to_datetime('{0} 00:00:00'.format(end))

        timeBins = pd.date_range(startTime, endTime, freq=freq)

        return timeBins