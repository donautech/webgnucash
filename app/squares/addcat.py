import pandas as pd


def addcat(dum: pd.DataFrame, addhour, y):
    if 'name' in dum:
        # dmi3coder: untested
        dum['name'] = pd.Categorical(dum['name'])
        dum['city'] = pd.Categorical(dum['city_start_geofence_id'])
    #         miami_id = dum['name'].isin('miami')
    # TODO: dum=dum(miami_id,:);

    if addhour:
        # TODO: unimplemented addhour case
        pass
    else:
        dum.sort_values(['r', 'yearweek', 'weekday'], inplace=True)
        dum.reset_index(drop=True, inplace=True)

    dum['rn'] = dum['r']
    dum['r'] = pd.Categorical(dum['r'])
    tmp = pd.Categorical(dum['r'])  # ???

    # unused
    finalstats = dum.groupby(['yearweek'])[y].agg('mean').to_frame()
    if dum['yearweek'].dtype.name != 'category':
        dum['yearweekn'] = dum['yearweek']

    dum['yearweek'] = pd.Categorical(dum['yearweek'])

    if dum['weekday'].dtype.name != 'category':
        dum['weekday'] = dum['weekday']
    dum['weekday'] = pd.Categorical(dum['weekday'])

    if addhour:
        # TODO: implement addhour
        # dum['weekhourn']= (dum['weekdayn']* 24 - 1 ) + dum['hoursn']
        pass

    tmp = pd.Categorical(dum['r'])
    # TODO figure out what addcats do

    if addhour:
        # TODO implement addhour
        pass
    else:
        dum['eitheridx'] = pd.Series(range(1, dum.shape[0] + 1))
        dum['bothidx'] = pd.Series(range(1, dum.shape[0] + 1))
        dum['deviceidx'] = pd.Series(range(1, dum.shape[0] + 1))
    return dum
