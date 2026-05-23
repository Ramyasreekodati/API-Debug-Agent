import sys, os
sys.path.append('g:/project/api-debug-agent')
from agents.lower.log_parser import parse_logs
from agents.middle.metrics import compute_metrics

def main():
    df = parse_logs('g:/project/api-debug-agent/sample_logs.txt')
    metrics = compute_metrics(df)
    print('Metrics:', metrics)

if __name__ == '__main__':
    main()
