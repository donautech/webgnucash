import cvxpy as cp
import numpy as np
import pandas as pd

from app.squares.addcat import addcat


def makemodel(dum, y='count_device', addhour=False, addcategory=True, s=None):
    if s is None:
        s = {}

    if addcategory:
        dum = addcat(dum, addhour, y)
        if addhour:
            # TODO s.area_q=quantile(dum.dist,0:0.2:1);
            pass

    # TODO: removecats????
    dummyr = pd.DataFrame(pd.get_dummies(dum['r']).to_dict())
    dummyyw = pd.DataFrame(pd.get_dummies(dum['yearweek']).to_dict())
    dummyw = pd.DataFrame(pd.get_dummies(dum['weekday']).to_dict())
    s['nr'] = dummyr.shape[1]
    s['nyw'] = dummyyw.shape[1]
    s['nw'] = dummyw.shape[1]
    s['n'] = dummyr.shape[0]
    # TODO {TypeError}categories must match existing categories when appending
    s['A'] = pd.concat([dummyr, dummyyw, dummyw], axis=1)
    # TODO: dum['ywd'] = pd.Categorical()
    # TODO: dumyywd = dummyvar(removecats(dum.ywd));
    # s.nywd=size(dummyywd,2);
    # if 'size' in dum:
    #     dummysize = pd.get_dummies(dum['size'])
    # else:
    #     dummysize = pd.DataFrame(dummy)

    hourstr = ''

    dum[y] = dum[y].fillna(0)

    if dum.shape[1] < 2000:
        pass

    if addhour:
        # TODO handle addhour
        pass
    else:
        dum['smallidx'] = 1
        dum_small = dum
        Asmall = s['A']

    m, n = Asmall.shape[0], Asmall.shape[1]
    order = 1
    magiccoef = 10

    if 'rent' in y:
        order = 2
        magiccoef = 20

    if 'device' in y:
        order = 2
        magiccoef = 40

    mywd = 1
    if m < 20:
        magiccoef = 30
        order = 1
        mywd = 0

    # TODO cvx: i, m, penalty_size, penalty_r
    n = s['n']
    A = s['A'].values
    b = dum['count_device']

    # Define and solve the CVXPY problem.
    x = cp.Variable(s['nr'] + s['nyw'] + s['nw'])
    penalty_r = x[0:s['nr'] - 1] - x[1:s['nr']]
    i = s['nr']
    penalty_yearweek = x[i + 1:i + s['nyw']] - x[i:i + s['nyw'] - 1]
    i = i + s['nyw']
    penalty_weekday = x[i + 1:i + s['nw']] - x[i:i + s['nw'] - 1]

    magic2 = np.log(n) / magiccoef;

    cost = cp.norm(A @ x - b, p=order) + \
           magic2 * cp.norm(penalty_r, p=order) + \
           magic2 * cp.norm(penalty_yearweek, p=order) + \
           magic2 * cp.norm(penalty_weekday, p=order) + \
           magic2 * cp.norm(x, p=order)
    prob = cp.Problem(cp.Minimize(cost))
    prob.solve()

    Asmall.columns = np.arange(len(Asmall.columns))
    # TODO UNTESTED
    dum['rcvx_' + y] = 0
    dum['rcvx_' + y] = dum_small[y] - Asmall @ x.value
    s['coef_' + y] = x.value
    s['coef_r_' + y] = x[1:s['nr']].value
    s['coef_yw_' + y] = x[s['nr'] + 1:s['nr'] + s['nyw']].value
    s['coef_w_' + y] = x[(s['nr'] + 1 + s['nyw']):].value
    if addhour:
        s['coef_d_' + y] = x[s['nr'] + s['nyw']:-24]
        s['coef_h_' + y] = x[-23:]

    #     dum['ax_' + y] = s['A']*x

    if dum.shape[0] < 1000:
        s['breaks'] = [-100, -0.001, 0.001, 100];
    else:
        s['breaks'] = dum['rcvx_' + y].quantile(np.arange(0, 1.1, 0.1))

    s['nq'] = len(s['breaks']) - 1

    dum['rcvx_' + y + '_q'] = pd.cut(dum['rcvx_' + y], s['breaks'])

    tmp = pd.Categorical(dum['rcvx_' + y + '_q'])
    print(tmp)

    # dum[[dum['rcvx_' + y]<0.0000001]]['rcvx_' + y] = 0

    return dum, s
