import cvxpy as cp
import numpy as np
import pandas as pd
from keras.utils import to_categorical

from app.squares.makemodel import makemodel


def solve(df):
    # df = pd.read_csv('traccar_vsquaremodel_miami_for-backtesting.csv')

    area_q = np.quantile(df.dist, np.arange(0, 1.1, 0.2), interpolation='midpoint')
    df['size'] = pd.cut(df['dist'], area_q)
    df['hourgroup'] = pd.cut(df['hours'], [-1, 1.95, 6.95, 11.5, 25])
    df['daygroup'] = pd.cut(df['weekday'], [0, 3.5, 7])

    print(df[df['count_device'] != 0].shape)
    # print(df)
    # df = df[df['yearweek'] < 3]
    # df.reset_index(drop=True, inplace=True)
    smgrp = pd.pivot_table(df[df['count_device'] != 0],
                           index=['size', 'r', 'yearweek', 'weekday', 'hourgroup'],
                           aggfunc=[np.mean, np.sum],
                           values=['count_device', 'count_rent', 'count_return'])
    sm = smgrp.query('hourgroup == [11.5, 25]')
    sm['count_device'] = sm['mean', 'count_device']
    sm['count_rent'] = sm['sum', 'count_rent']
    df = sm.reset_index()
    df, s = makemodel(df, 'count_device', False, True)
    df, s = makemodel(df, 'count_rent', False, False, s)
    np.unique(df['r'], return_inverse=True)
    rgroup = np.unique(df['r'], return_inverse=True)[1] * s['nq'] + \
             np.unique(df['rcvx_count_device_q'].cat.codes, return_inverse=True)[1]
    rgroup = to_categorical(rgroup, s['nq'] * s['nr'] + 1)
    Aq = rgroup
    s['nrr'] = df['r'].unique().shape[0]
    mq, nq = Aq.shape
    # Aq = Aq.fillna(0)
    tmp = []
    for r in range(nq):
        tmp.append(df['rcvx_count_device'].values)

    Aq = Aq * np.array(tmp).T

    xreg4 = cp.Variable(nq - 1)
    # reshape not wroking because of grpstats
    penalty_r = cp.reshape(xreg4, (s['nq'], s['nr']))

    prob = cp.Problem(cp.Minimize(cp.norm(df['rcvx_count_rent'].values - Aq[:, :-1] * xreg4, 2) \
                                  + 0.05 * cp.norm(xreg4, 1) +
                                  0.1 * cp.norm(penalty_r[:, 1:] - penalty_r[:, :-1], 1)),
                      constraints=[
                          penalty_r[1:, :] <= penalty_r[:-1, :] - 0.01,
                          penalty_r >= 0
                      ]
                      )

    prob.solve()
