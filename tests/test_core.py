import pandas as pd
from src.core import analyze,bh

def test_bh():
    assert len(bh([0.01,0.04,0.2]))==3

def test_analysis():
    df=pd.DataFrame({'sample_id':['a','b','c','d'],'replicate':[1,1,1,1],'treatment':['A','A','B','B'],'response':[1,2,4,5]})
    r=analyze(df,'treatment',['response'],'replicate',['sample_id'])
    assert len(r['tests'])==1
