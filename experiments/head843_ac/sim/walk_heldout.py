"""held-out check of a max-speed gait param file on the current twiglet_v3.xml: 20 randomized seeds 6000-6019 (not used by walk_refine/eval).
python walk_heldout.py v3 <params.npy> <tag>  -> appends to sim_summary.txt"""
import sys, os, numpy as np, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import walk_search as W
if __name__ == "__main__":
    x = np.load(sys.argv[2]); pool = mp.Pool(6); R = W.batch([x] * 20, range(6000, 6020), True, pool, T=10.0)
    s = float(np.mean([not r["fell"] for r in R])); v = float(np.mean([r["dx"] / 10.0 for r in R if not r["fell"]] or [0]))
    line = f"heldout {sys.argv[3]} params={os.path.basename(sys.argv[2])} seeds6000-6019 succ {s:.2f} ({int(round(s*20))}/20) speed {v:.3f}"
    print(line); open(os.path.join(W.OUT, "sim_summary.txt"), "a").write(line + "\n")
