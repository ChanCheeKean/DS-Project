# function for kpi page

# import function
import numpy as np
from scipy.stats import t as ttest

# moving average data for excursion
def get_moving_avg (df, ma_win, channel = 'V'):
    # data of specific channel
    df_volt = df[[col for col in df.columns if channel in col]]         
    
#    def rolling_mean(df, window = ma_win):
#        return df.rolling(window, min_periods=1).mean()
#    df_ma = df_volt.groupby([df_volt.index.hour, df_volt.index.minute]).transform(rolling_mean)
    df_ma = df_volt.rolling('{}D'.format(ma_win)).mean()
    return df_ma, df_volt

#####################################################################################
# Frequency - Without Padding
def get_excursions_freq_wo_padding(df, lb_win = 7, ma_win = 10, frac_th = 0.01, channel = 'Voltage'):
    df_ma, df_volt_a = get_moving_avg (df, ma_win, channel = channel)
    # set upper and lower hit boundaries
    th_up = df_ma*(1+frac_th)
    th_low = df_ma*(1-frac_th)
    # detect hits
    df_out = (df_volt_a>th_up)|(df_volt_a<th_low)
    df_out = 1*df_out
    # count number of hits
    df_hits = df_out.diff(1).iloc[1:,:]==1 # When the voltage hits the threshold
    df_hits = 1*df_hits
    # df_hits = df_out
    df_freq = df_hits.rolling('{}D'.format(lb_win)).sum()
    return df_freq

#####################################################################################
def get_excur_percent(df, ma_win = 10, channel = 'Voltage'):
    df_ma, df_volt = get_moving_avg (df, ma_win, channel=channel)
    df_percent = (df_volt.div(df_ma, axis = 0).subtract(1))*100
        
    return df_percent

#####################################################################################
# alpha increase, outlier count increase
def get_sh_esd (df, max_pct = 0.02, alpha = 0.05):
    
    # df must be series
    df_trans = df.copy()
    n = len(df_trans)
    out_count = int(max_pct * n)
    num_anoms = 0
    idx = []
    # Compute test statistic until max_out values have been removed from the sample. 
    for i in range(out_count): 
        r = (df_trans - df_trans.median()).abs() 
        mad = df_trans.mad()
        # find highly deviate points
        r = r/float(mad) 
        rmax = r.max()
        try:
            max_idx = r[r == rmax].index.tolist()[0] 
        except:
            max_idx = r[r == rmax].index.tolist()
        idx.append(max_idx)
        df_trans = df_trans[df_trans.index != max_idx] 
        p = 1-alpha/float(2*(n-i)) 
        t = ttest.ppf(p,(n-i-2))
        lam = t*(n-i)/float(np.sqrt((n-i-2+t**2)*(n-i))) 
        if rmax > lam: 
            num_anoms = i
    
    if num_anoms > 0: 
        idx = idx[:num_anoms] 
    else:
        idx = None
    return idx

#####################################################################################
