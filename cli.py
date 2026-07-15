import argparse,yaml
from pathlib import Path
from src.core import load_table,analyze
p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--config',default='configs/default.yaml'); p.add_argument('--output',default='outputs'); a=p.parse_args()
cfg=yaml.safe_load(open(a.config)); r=analyze(load_table(a.input),cfg['group_column'],cfg['value_columns'],cfg.get('replicate_column'),cfg.get('id_columns'))
out=Path(a.output); out.mkdir(exist_ok=True)
for k,v in r.items(): v.to_csv(out/f'{k}.csv',index=False)
print(out)
