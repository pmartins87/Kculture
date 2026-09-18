from solver.programme_features import ITEMS
UNIT_OP={k:i for i,k in enumerate('PASS NORTH SOUTH EAST WEST PICKUP DROP PLACE PLANT WATER HARVEST FERTILIZE DIG BUILD_COOP BUILD_PASTURE FEED COLLECT_FERTILIZER CARE'.split())}
MARKET_OP={k:i+1 for i,k in enumerate('HIRE BUY_LAND BUY_SEED BUY_PRODUCT BUY_ANIMAL SELL'.split())}
U={v:k for k,v in UNIT_OP.items()};M={v:k for k,v in MARKET_OP.items()}
def decode(row):
    units=[]
    for j in range(int(row[0])):
        op,arg,n=map(int,row[1+3*j:4+3*j]);a=[U[op]]
        if arg>=0:a += [ITEMS[arg],n]
        units.append(a)
    orders=[]
    for j in range(int(row[121])):
        op,arg,n=map(int,row[122+3*j:125+3*j]);a=[M[op]]
        if arg>=0:a += [ITEMS[arg],n]
        orders.append(a)
    return dict(farmer=units[0],hands=units[1:],market=orders)
