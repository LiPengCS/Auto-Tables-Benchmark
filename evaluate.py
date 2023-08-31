import pandas as pd
import os
import json
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', default="ATBench")
parser.add_argument('--result_dir', default="our_results")
args = parser.parse_args()

def listdir(root_dir):
    return [d for d in os.listdir(root_dir) if d[0] != "."]

def is_hit(pred, gt):
    # check hit (both operator and params are correct) or not
    if gt is None:
        return False

    if len(pred) != len(gt):
        return False
    
    for pred_i, gt_i in zip(pred, gt):
        for k in gt_i:
            if k not in pred_i or pred_i[k] != gt_i[k]:
                return False
    return True
    
def compute_hit_at_k(pred, gt, alternative_gt):
    # compute hit at k for one case 
    hit_at_k = np.zeros(len(pred))
    
    for i in range(len(pred)):
        # get top k pred
        pred_i = pred[f"top-{i+1}"]
        
        # check if pred hits gt or alternative gt 
        if is_hit(pred_i, gt) or is_hit(pred_i, alternative_gt):
            hit_at_k[i:] = 1
            break
    return hit_at_k
        
eval_results = []
for op in listdir(args.data_dir):
    for table_id in listdir(os.path.join(args.data_dir, op)):
        # get ground truth label
        with open(os.path.join(args.data_dir, op, table_id, "info.json"), "r") as f:
            info = json.load(f)
        gt = info["label"]
        alternative_gt = info["alternative_label"]

        # get pred label
        with open(os.path.join(args.result_dir, f"{table_id}.json"), "r") as f:
            pred = json.load(f)

        # compute hit at k for one case
        hit_at_k = compute_hit_at_k(pred, gt, alternative_gt)
        
        # save result
        result = {
            "table_id": table_id
        }
        for i in range(len(hit_at_k)):
            result[f"Hit@{i+1}"] = hit_at_k[i]

        eval_results.append(result)
        
eval_results = pd.DataFrame(eval_results)

# compute average Hit@k
avg_hit_at_k = eval_results.mean(numeric_only=True).round(3)
print(avg_hit_at_k)
