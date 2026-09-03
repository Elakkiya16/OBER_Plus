"""Evaluation of the R2 CLO change classifier.

Builds a labelled set of CLO statement pairs from the real outcomes of
CS F351 Theory of Computation and CS F459 Computer Vision, covering the four
classes the classifier reports, and measures agreement with those labels.

Run:  python eval_clo_change.py
"""
import sys, os, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import classify_clo_change, clo_similarity, SIM_THRESHOLD

PAIRS = [
 # unchanged
 ("Explain the fundamental concepts of alphabets, strings, languages, infinite sets, closure properties, and proof techniques.",
  "Explain the fundamental concepts of alphabets, strings, languages, infinite sets, closure properties, and proof techniques.", "Unchanged"),
 ("Construct finite automata and regular expressions for languages.",
  "Construct finite automata and regular expressions for languages.", "Unchanged"),
 ("Apply feature detection and description techniques to images.",
  "Apply feature detection and description techniques to images.", "Unchanged"),
 # paraphrase
 ("Construct finite automata and regular expressions for languages.",
  "Construct finite automata and regular expressions for formal languages.", "Paraphrase"),
 ("Develop Turing Machine models for language recognition.",
  "Develop Turing machine models for the recognition of languages.", "Paraphrase"),
 ("Analyze computational problems in terms of decidability.",
  "Analyze computational problems with respect to decidability.", "Paraphrase"),
 ("Explain digital image formation, formats, colour models and fundamental image processing operations.",
  "Explain digital image formation, image formats, colour models and basic image processing operations.", "Paraphrase"),
 ("Apply feature detection and description techniques to images.",
  "Apply feature detection and feature description techniques to digital images.", "Paraphrase"),
 ("Analyze the performance of segmentation and recognition methods.",
  "Analyze the performance of image segmentation and recognition methods.", "Paraphrase"),
 ("Design deep learning pipelines for vision tasks.",
  "Design deep learning pipelines for computer vision tasks.", "Paraphrase"),
 ("Design context-free grammars and pushdown automata.",
  "Design context free grammars and pushdown automata.", "Paraphrase"),
 # change of cognitive level
 ("Analyze computational problems in terms of decidability.",
  "Explain computational problems in terms of decidability.", "Change of cognitive level"),
 ("Design deep learning pipelines for vision tasks.",
  "Apply deep learning pipelines for vision tasks.", "Change of cognitive level"),
 ("Construct finite automata and regular expressions for languages.",
  "Describe finite automata and regular expressions for languages.", "Change of cognitive level"),
 ("Apply context-free grammars and pushdown automata to language problems.",
  "Design context-free grammars and pushdown automata.", "Change of cognitive level"),
 ("Develop Turing Machine models for language recognition.",
  "Explain Turing Machine models for language recognition.", "Change of cognitive level"),
 ("Analyze the performance of segmentation and recognition methods.",
  "Evaluate the performance of segmentation and recognition methods.", "Change of cognitive level"),
 # replacement
 ("Construct finite automata and regular expressions for languages.",
  "Construct proofs of the pumping lemma for regular and context-free languages.", "Replacement"),
 ("Develop Turing Machine models for language recognition.",
  "Develop reductions between undecidable problems.", "Replacement"),
 ("Design context-free grammars and pushdown automata.",
  "Design lexical analysers and parsers for programming languages.", "Replacement"),
 ("Apply feature detection and description techniques to images.",
  "Apply camera calibration and stereo geometry to multiple views.", "Replacement"),
 ("Analyze the performance of segmentation and recognition methods.",
  "Analyze the ethical implications of automated visual surveillance.", "Replacement"),
 ("Design deep learning pipelines for vision tasks.",
  "Design annotation protocols and dataset governance for vision projects.", "Replacement"),
 ("Explain digital image formation, formats, colour models and fundamental image processing operations.",
  "Explain the mathematics of projective geometry and camera models.", "Replacement"),
]

def main():
    conf = collections.Counter()
    per_class = collections.defaultdict(list)
    correct = 0
    for before, after, label in PAIRS:
        kind, sim, lb, la = classify_clo_change(before, after)
        conf[(label, kind)] += 1
        correct += (kind == label)
        if sim is not None:
            per_class[label].append(sim)
    print(f"threshold {SIM_THRESHOLD}")
    print(f"agreement {correct}/{len(PAIRS)}")
    for cls in ["Unchanged", "Paraphrase", "Change of cognitive level", "Replacement"]:
        v = per_class[cls]
        n = sum(c for (g, _), c in conf.items() if g == cls)
        rng = f"{min(v):.3f} to {max(v):.3f}" if v else "n/a"
        print(f"  {cls:26s} n={n}  similarity {rng}")
    wrong = {k: v for k, v in conf.items() if k[0] != k[1]}
    print("disagreements:", wrong if wrong else "none")
    a = "Apply context-free grammars and pushdown automata to language problems."
    b = "Design context-free grammars and pushdown automata."
    kind, sim, lb, la = classify_clo_change(a, b)
    print(f"\nCS F351 CLO3 in the demonstration data: {kind}, similarity {sim}, {lb} to {la}")

if __name__ == "__main__":
    main()
