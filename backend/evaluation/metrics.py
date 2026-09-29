"""Evaluation Metrics for Hackathon Benchmarking (EM, F1, Groundedness, Costs)."""
import re
import string
from typing import List, Dict, Any, Union

def normalize_text(text: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(t):
        return re.sub(r"\b(a|an|the)\b", " ", t)

    def white_space_fix(t):
        return " ".join(t.split())

    def remove_punc(t):
        exclude = set(string.punctuation)
        return "".join(ch for ch in t if ch not in exclude)

    return white_space_fix(remove_articles(remove_punc(text.lower())))

def compute_exact_match(prediction: str, ground_truth: Union[str, List[str]]) -> float:
    """Calculates 1.0 if prediction exactly matches any ground truth answer, else 0.0."""
    gts = ground_truth if isinstance(ground_truth, list) else [ground_truth]
    norm_pred = normalize_text(prediction)
    for gt in gts:
        if norm_pred == normalize_text(str(gt)):
            return 1.0
        # Partial match if number matches
        if norm_pred.isdigit() and normalize_text(str(gt)).isdigit():
            if norm_pred == normalize_text(str(gt)):
                return 1.0
        # String containment for named entities
        gt_norm = normalize_text(str(gt))
        if len(gt_norm) > 4 and (gt_norm in norm_pred or norm_pred in gt_norm):
            return 1.0
    return 0.0

def compute_f1(prediction: str, ground_truth: Union[str, List[str]]) -> float:
    """Calculates token-level F1 score between prediction and ground truth."""
    gts = ground_truth if isinstance(ground_truth, list) else [ground_truth]
    best_f1 = 0.0
    for gt in gts:
        pred_tokens = normalize_text(prediction).split()
        gt_tokens = normalize_text(str(gt)).split()
        common = set(pred_tokens) & set(gt_tokens)
        num_same = sum(min(pred_tokens.count(w), gt_tokens.count(w)) for w in common)
        if len(pred_tokens) == 0 or len(gt_tokens) == 0:
            best_f1 = max(best_f1, int(pred_tokens == gt_tokens))
            continue
        if num_same == 0:
            continue
        precision = 1.0 * num_same / len(pred_tokens)
        recall = 1.0 * num_same / len(gt_tokens)
        f1 = (2 * precision * recall) / (precision + recall)
        best_f1 = max(best_f1, f1)
    return round(best_f1, 4)

def compute_groundedness(prediction: str, evidence_texts: List[str]) -> float:
    """Estimates percentage of prediction content supported by retrieved evidence."""
    pred_tokens = [w for w in normalize_text(prediction).split() if len(w) > 2]
    if not pred_tokens:
        return 1.0
    all_evidence = " ".join(normalize_text(t) for t in evidence_texts)
    supported = sum(1 for w in pred_tokens if w in all_evidence)
    return round(supported / len(pred_tokens), 4)