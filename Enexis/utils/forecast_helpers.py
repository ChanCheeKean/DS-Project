# function for forecasting
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import BaggingRegressor, RandomForestRegressor
import pvlib

############################################################################################
def prepare_fc_data(df_ori, time_res = '1h', phase = 1, y_var = 'P'):
    df = df_ori.copy()
    df = df.resample(time_res).mean()
    
    if phase != None:
    # define phase
        colname = [col for col in df.columns if str(phase) == col[-1]] 
        df = df[colname]
    else:
        df = df
        
    # moving average for active power column
    chosen_col = [col for col in df.columns if y_var in col]
    df_rm3 = df[chosen_col].rolling(3).mean()
    df_rm6 = df[chosen_col].rolling(6).mean()
    df_rm12 = df[chosen_col].rolling(12).mean()
    df_rm24 = df[chosen_col].rolling(24).mean()
    df_ma = pd.concat([df_rm3,df_rm6,df_rm12,df_rm24], axis=1)
    df_ma.columns =  ['ma3','ma6','ma12','ma24']
    
    # Create features for days, months, weekdays and weekend
    wks = [x.weekday() for x in df.index]
    date = [x.day for x in df.index]
    month = [x.month for x in df.index]
    df['weekend'] = [(x in [5,6]) for x in wks]
    df['weekday'] = [(x in [0,1,2,3,4]) for x in wks]
    df['holiday'] = [((x,y) in [(1,1),(21,4),(22,4),(27,4),(4,5),(30,5),(9,6),(10,6),(25,12),(26,12)])\
                          for (x,y) in zip(date,month)]
    
    dow = np.array([x.dayofweek for x in df.index])
    hr = np.array([x.hour for x in df.index])
    mo = np.array([x.month for x in df.index])

    for i in range(24):
        df['h'+str(i)] = [x==i for x in hr]
    for i in range(1,13):
        df['m'+str(i)] = [x==i for x in mo]
    
    # convert bool to float
    df = df.astype('float64')

    # read nasa data
    # df_venray = pd.read_csv('./processed_csv_files/Venray_weather_vars.csv', index_col=0)
    # df_venray.index = pd.to_datetime(df_venray.index)
    # df = pd.concat([df,df_venray,df_ma], join = 'inner', axis=1)
    df = pd.concat([df,df_ma], join = 'inner', axis=1)
    df.dropna(inplace=True)
    
    # df.to_csv('../processed_csv_files/mock_up_data.csv')
    return df

############################################################################################
# x-y splitting and feature scaling
def split_xy (df, y_var = 'apow', step = 1):
    # define X and Y
    y_col = [col for col in df.columns if col.split('.')[0] == y_var]
    X = df.iloc[:-1,:]
    Y = df[y_col].iloc[1:,0]
        
    if step>1:
        # for multi forecast
        mX = X[:-step+1]
        mY = pd.DataFrame(Y)
        for i in range(step-1):
            mY = pd.concat([Y.shift(i+1),mY], axis=1)
        mY = pd.DataFrame(mY.values[step-1:,:], index = mY.index[:-step+1])
        x_train, x_test, y_train, y_test = train_test_split(mX, mY, test_size=0.1, random_state=42)
    else:
        # single forecast
        x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    # Feature Scaling
    scaler = RobustScaler()
    scaler.fit(x_train)
    x_train = scaler.transform(x_train)
    x_test = scaler.transform(x_test)
    
#    with open('../forecast_models/scaler_new.sav', 'wb') as sc:
#        pickle.dump(scaler, sc)
    
    return x_train, x_test, y_train, y_test

############################################################################################
# Performance Evaluation
def evaluate_model (reg, x_test, y_test):
    pred_y = reg.predict(x_test)
    r2 = r2_score(y_test, pred_y)
    rmse = np.sqrt(mean_squared_error(y_test, pred_y))
    mae = mean_absolute_error(y_test, pred_y)
    metrics = [r2,rmse,mae]
    return pred_y, metrics

############################################################################################
# split and train new model
def train_fc_model (df, y_var, model='lr', step = 1):
    
    x_train, x_test, y_train, y_test = split_xy (df, y_var = y_var, step = step)
    
    if model == 'lr':
        reg = BaggingRegressor(LinearRegression(), bootstrap=True, random_state=42)
        reg.fit(x_train,y_train)

    elif model == 'rr':
        reg = RidgeCV(alphas=[10**(x/10) for x in range(-30,0)], cv=5)
        reg.fit(x_train,y_train)
            
    elif model == 'rf':
        reg = RandomForestRegressor(max_depth=None, max_features = 'sqrt', min_samples_leaf = 1, n_estimators = 50, random_state=101)
        reg.fit(x_train,y_train)

    # Fit after defining model
    pred_y, metrics = evaluate_model (reg, x_test, y_test)
        
    # actual vs predicted values in one dataframe
    if step == 1:
        df_pred = pd.DataFrame(pred_y, index = y_test.index, columns = ['Predicted'])
        df_act_pred = pd.concat([y_test, df_pred], axis = 1)
    else:
        df_pred = pd.DataFrame(pred_y, index = y_test.index)
        df_act_pred = pd.concat([y_test.iloc[:,0].rename('Actual'), df_pred], axis = 1)
            
    return df_act_pred, metrics, reg

############################################################################################
# function for PV production

def get_pv_load (df_trans, lat_lon_alt = [51.5, 6.0, 25]):
    # Estimate PV and load
    def rolling_max (df, window='60D'):
        return df.rolling(window, min_periods=10).max()
    
    # load demand, defined by the power peak
    df_load = df_trans.groupby([df_trans.index.hour, df_trans.index.minute]).transform(rolling_max)
    df_pv = df_load - df_trans
    
    loc = pvlib.location.Location(lat_lon_alt[0], lat_lon_alt[1], altitude=lat_lon_alt[2])
    clear_sky = loc.get_clearsky(df_trans.index)['ghi']
    # scale factor, zero at night, multiplicator for the lowest 15 % values
    scale_factor = 100. / 15 * clear_sky / clear_sky.max()
    scale_factor = pd.DataFrame(scale_factor)
    scale_factor['cap'] = 1
    scale_factor = scale_factor.min(axis=1)
    
    # adjust pv and load 
    df_pv = df_pv * scale_factor
    df_load = df_trans + df_pv    
    
    df_power = pd.concat([df_trans,df_load, df_pv], axis = 1)
    df_power.columns = ['Power Demand','Load','PV Production']
    
    return df_power
def get_pv_peak (df_pv):
    # Take pv and generate peak
    highest_pv_days = df_pv.groupby(df_pv.index.date).sum().sort_values(ascending=False)
#    ts = df_pv[0:1]
#    for i in range(5):
#        day = df_pv[highest_pv_days.index[i].strftime('%Y-%m-%d')]
#        ts = ts.append(day)
        
    # As all 5 days should have at least 2 times the peak pv production,
    # the 5th value lays good in the middle.
    # This slightly evens out the demand and other variabilies.
#    pv_peak = ts[1:].sort_values(ascending=False)[0]
    
    return highest_pv_days[0]
