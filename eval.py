"""Run test questions through the assistant, 
record latency, and save answers to CSV.
"""
import csv
import sys
import time

from src.qa import answer

QUESTIONS = [
        # ATmega328P
    "What is the operating voltage range of the ATmega328P?",
    "How much Flash program memory does the ATmega328P have?",
    "How many programmable I/O lines does the ATmega328P have?",
    "What is the resolution of the ATmega328P ADC and how many channels does it have?",

    # LM7805
    "What is the output voltage of the LM7805?",
    "What is the maximum output current of the LM7805?",
    "What is the input voltage range of the LM7805?",
    "What is the dropout voltage of the LM7805?",

    # LM358
    "What is the supply voltage range of the LM358?",
    "How many operational amplifiers are in one LM358 package?",
    "What is the typical input offset voltage of the LM358?",
    "What is the unity-gain bandwidth of the LM358?",

    # AT89C51
    "How much Flash memory does the AT89C51 have?",
    "How much internal RAM does the AT89C51 have?",
    "How many I/O lines does the AT89C51 have?",
    "What is the operating frequency range of the AT89C51?",

    # Comparisons
    "Compare the supply voltage range of the LM358 and the LM7805.",
    "Compare the Flash memory of the ATmega328P and the AT89C51.",

    # Not in the datasheets (the correct behavior is "not found")
    "What is the price of the LM358?",
    "What is the Wi-Fi range of the ATmega328P?",
]

OUT = "eval_results.csv"


def run():
    rows = []
    for i, q in enumerate(QUESTIONS, 1):
        start = time.time()
        text, docs = answer(q)
        latency = round(time.time() - start, 2)
        pages = "; ".join(sorted({f"{d.metadata['source']} p.{d.metadata['page']}" for d in docs}))
        rows.append([i, q, text.replace("\n", " "), pages, latency, ""])
        print(f"[{i}/{len(QUESTIONS)}] {latency}s")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "question", "answer", "sources", "latency_s", "correct"])
        w.writerows(rows)
    print(f"Saved {OUT}. Grade the 'correct' column (1 or 0), then run: python eval.py --score")


def score():
    with open(OUT, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    graded = [r for r in rows if r["correct"].strip() in ("0", "1")]
    if not graded:
        raise SystemExit("No graded rows yet. Fill the 'correct' column with 1 or 0.")
    correct = sum(int(r["correct"]) for r in graded)
    avg = sum(float(r["latency_s"]) for r in rows) / len(rows)
    print(f"Questions graded: {len(graded)}")
    print(f"Correct: {correct}/{len(graded)} = {100 * correct / len(graded):.0f}%")
    print(f"Average response time: {avg:.1f} s")


if __name__ == "__main__":
    score() if "--score" in sys.argv else run()
