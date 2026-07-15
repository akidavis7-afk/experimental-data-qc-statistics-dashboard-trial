import numpy as np, pandas as pd
from scipy import stats

def load_table(path): return pd.read_excel(path) if str(path).lower().endswith(('.xlsx','.xls')) else pd.read_csv(path)
def bh(pvals):
    p=np.asarray(pvals,float); order=np.argsort(p); ranked=p[order]; n=len(p); adj=np.minimum.accumulate((ranked*n/np.arange(1,n+1))[::-1])[::-1]; out=np.empty(n); out[order]=np.minimum(adj,1); return out

def analyze(df,group,value_cols,replicate=None,id_cols=None):
    id_cols=id_cols or []
    qc=[]
    for c in [group,*value_cols,*id_cols]:
        if c not in df.columns: qc.append({'severity':'error','issue':f'missing required column: {c}'})
    if qc: return {'qc':pd.DataFrame(qc),'summary':pd.DataFrame(),'tests':pd.DataFrame(),'annotated':df}
    dup=df.duplicated(subset=id_cols+[replicate] if replicate and id_cols else None,keep=False)
    if dup.any(): qc.append({'severity':'warning','issue':f'{dup.sum()} duplicate records'})
    for c in value_cols:
        qc.append({'severity':'info','issue':f'{c}: {df[c].isna().sum()} missing values'})
    ann=df.copy()
    for c in value_cols:
        q1,q3=ann[c].quantile([.25,.75]); iqr=q3-q1; ann[f'{c}_outlier']=((ann[c]<q1-1.5*iqr)|(ann[c]>q3+1.5*iqr))
    summary=ann.groupby(group)[value_cols].agg(['count','mean','std','median']).reset_index()
    tests=[]
    for c in value_cols:
        groups=[x[c].dropna().values for _,x in ann.groupby(group)]
        labels=[str(k) for k,_ in ann.groupby(group)]
        if len(groups)==2:
            stat,p=stats.ttest_ind(groups[0],groups[1],equal_var=False); test='Welch t-test'
        elif len(groups)>2:
            stat,p=stats.f_oneway(*groups); test='one-way ANOVA'
        else: stat=p=np.nan; test='not applicable'
        tests.append({'variable':c,'test':test,'groups':' | '.join(labels),'statistic':stat,'p_value':p})
    tdf=pd.DataFrame(tests)
    if len(tdf): tdf['p_adjusted_bh']=bh(tdf['p_value'].fillna(1))
    return {'qc':pd.DataFrame(qc),'summary':summary,'tests':tdf,'annotated':ann}
