from radon.metrics import mi_visit, h_visit, cc_visit
import os

def compute_code_metrics(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    mi_score = mi_visit(code, True)
    cc_scores = cc_visit(code)
    return {
        'maintainability_index': mi_score,
        'cyclomatic_complexity': cc_scores
    }

if __name__ == '__main__':
    metrics = compute_code_metrics('your_module.py')
    print(metrics)

