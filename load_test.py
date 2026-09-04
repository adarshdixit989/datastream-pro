"""Measure ingestion throughput against a running DataStream Pro API.
Example: python benchmarks/load_test.py --url http://localhost:8000/api/events/bulk/ --count 10000 --batch 500
"""
import argparse, random, time, requests
p=argparse.ArgumentParser(); p.add_argument('--url',default='http://localhost:8000/api/events/bulk/'); p.add_argument('--count',type=int,default=10000); p.add_argument('--batch',type=int,default=500); a=p.parse_args()
start=time.perf_counter(); sent=0
while sent<a.count:
    n=min(a.batch,a.count-sent)
    events=[{'event_type':random.choice(['purchase','login','signup','payment','search']),'source':random.choice(['web','mobile','api']),'value':round(random.expovariate(1/100),2),'payload':{'synthetic':True}} for _ in range(n)]
    r=requests.post(a.url,json={'events':events},timeout=30); r.raise_for_status(); sent+=n
elapsed=time.perf_counter()-start
print(f'events={sent} seconds={elapsed:.2f} throughput={sent/elapsed:.1f} events/sec')
