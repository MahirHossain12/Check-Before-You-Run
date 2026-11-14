import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0"
INPUTS = range(21)
TASKS = {
    "minimum": (
        ("Concert booking", "A booking must contain at least 3 tickets. Return 1 if it qualifies, otherwise 0.",
         "int(x >= 3)", "int(x > 3)", [0, 3, 5, 12]),
        ("Printing discount", "An order of at least 7 pages gets a discount. Return 1 if it qualifies, otherwise 0.",
         "int(x >= 7)", "int(x > 7)"),
    ),
    "maximum": (
        ("Bike rack", "A group of up to 5 bikes fits in the rack. Return 1 if it fits, otherwise 0.",
         "int(x <= 5)", "int(x < 5)", [2, 5, 8, 10]),
        ("Workshop seats", "A group of up to 9 people can book. Return 1 if it fits, otherwise 0.",
         "int(x <= 9)", "int(x < 9)"),
    ),
    "cap": (
        ("Loyalty points", "Award one point per purchase, capped at 4 points.",
         "min(x, 4)", "x", [0, 2, 4, 6]),
        ("Practice credits", "Award one credit per completed practice, capped at 6 credits.",
         "min(x, 6)", "x"),
    ),
    "floor": (
        ("Shuttle allocation", "Return the requested number of shuttle seats with a minimum allocation of 2.",
         "max(x, 2)", "x", [0, 2, 4, 8]),
        ("Workshop supplies", "Return the requested number of kits with a minimum allocation of 4.",
         "max(x, 4)", "x"),
    ),
}
CONDITIONS = {"A": "Run first", "B": "Predict first"}


def schedule(sequence):
    if type(sequence) is not int or sequence not in range(8):
        raise ValueError("Sequence must be an integer from 0 to 7.")
    ids = list(TASKS)
    shift = sequence % 4
    pattern = "ABBA" if sequence < 4 else "BAAB"
    return list(zip(ids[shift:] + ids[:shift], pattern))


def fixture(task, transfer=False):
    name, spec, correct, candidate, *choices = TASKS[task][int(transfer)]
    expected = {x: eval(correct, {"__builtins__": {}, "int": int, "min": min, "max": max}, {"x": x}) for x in INPUTS}
    actual = {x: eval(candidate, {"__builtins__": {}, "int": int, "min": min, "max": max}, {"x": x}) for x in INPUTS}
    return {
        "name": name, "spec": spec, "code": f"def candidate(x):\n    return {candidate}",
        "expected": expected, "actual": actual, "choices": choices[0] if choices else [],
    }


def public_task(task):
    practice = fixture(task)
    transfer = fixture(task, transfer=True)
    return {
        "practice": {k: v for k, v in practice.items() if k != "expected"},
        "transfer": {k: transfer[k] for k in ("name", "spec", "code")},
    }


def session_html(participant, sequence, mode="walkthrough"):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", participant):
        raise ValueError("Use an anonymous ID of 1–32 letters, digits, underscores, or hyphens.")
    if mode not in {"walkthrough", "participant"}:
        raise ValueError("Unknown session mode.")
    config = {
        "version": VERSION, "participant": participant, "sequence": sequence, "mode": mode,
        "rounds": [
            {"id": task, "condition": condition, **public_task(task)}
            for task, condition in schedule(sequence)
        ],
    }
    payload = json.dumps(config).replace("<", "\\u003c")
    return (ROOT / "prototype" / "session.html").read_text().replace("__SESSION_CONFIG__", payload)


def score(record):
    if record["version"] != VERSION or record["mode"] not in {"synthetic", "walkthrough", "participant"}:
        raise ValueError("Unsupported version or session mode.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", record["participant"]):
        raise ValueError("Invalid participant ID.")
    rounds = record["rounds"]
    if len(rounds) != 4:
        raise ValueError("A complete session requires four rounds.")
    rows = []
    for index, ((task, condition), response) in enumerate(zip(schedule(record["sequence"]), rounds), 1):
        if (response["id"], response["condition"]) != (task, condition):
            raise ValueError(f"Round {index} does not match the assigned sequence.")
        practice, transfer = fixture(task), fixture(task, transfer=True)
        practice_input = response["practice_input"]
        transfer_input = response["transfer_input"]
        expected = response["transfer_expected"]
        prediction = response["practice_prediction"]
        if type(practice_input) is not int or practice_input not in practice["choices"]:
            raise ValueError("Invalid practice input.")
        if type(transfer_input) is not int or transfer_input not in INPUTS:
            raise ValueError("Invalid transfer input.")
        if type(expected) is not int or expected not in INPUTS:
            raise ValueError("Invalid expected output.")
        if condition == "A" and prediction is not None:
            raise ValueError("Run-first rounds do not collect predictions.")
        if condition == "B" and (type(prediction) is not int or prediction not in INPUTS):
            raise ValueError("Predict-first rounds require an integer prediction.")
        if response["practice_verdict"] not in {"matches", "differs", "unsure"}:
            raise ValueError("Invalid practice verdict.")
        practice_differs = practice["expected"][practice_input] != practice["actual"][practice_input]
        discriminates = transfer["expected"][transfer_input] != transfer["actual"][transfer_input]
        expected_correct = expected == transfer["expected"][transfer_input]
        rows.append({
            "participant": record["participant"], "sequence": record["sequence"], "mode": record["mode"],
            "round": index, "task": task, "condition": condition,
            "valid_counterexample": int(discriminates and expected_correct),
            "discriminating_input": int(discriminates), "correct_expected_output": int(expected_correct),
            "practice_discriminating_input": int(practice_differs),
            "practice_verdict_correct": int(response["practice_verdict"] == ("differs" if practice_differs else "matches")),
            "practice_prediction_correct": None if prediction is None else int(prediction == practice["expected"][practice_input]),
        })
    return rows


def synthetic_sessions():
    records = []
    for sequence in range(8):
        rounds = []
        for index, (task, condition) in enumerate(schedule(sequence)):
            practice, transfer = fixture(task), fixture(task, transfer=True)
            practice_input = practice["choices"][(sequence + index) % 4]
            pool = [x for x in INPUTS if (transfer["expected"][x] != transfer["actual"][x]) == ((sequence + index * 2) % 3 != 0)]
            transfer_input = pool[sequence % len(pool)]
            expected = transfer["expected"][transfer_input]
            rounds.append({
                "id": task, "condition": condition, "practice_input": practice_input,
                "practice_prediction": practice["expected"][practice_input] if condition == "B" else None,
                "practice_verdict": "differs" if practice["expected"][practice_input] != practice["actual"][practice_input] else "matches",
                "transfer_input": transfer_input,
                "transfer_expected": (expected + 1) % 21 if (index + sequence) % 5 == 0 else expected,
            })
        records.append({
            "version": VERSION, "participant": f"synthetic-{sequence + 1:02d}",
            "sequence": sequence, "mode": "synthetic", "rounds": rounds,
        })
    return records


def score_sessions(records, mode):
    ids = set()
    rows = []
    for record in records:
        if record["mode"] != mode:
            raise ValueError("Keep synthetic, walkthrough, and participant files in separate runs.")
        participant = record["participant"]
        if participant in ids:
            raise ValueError(f"Duplicate session ID: {participant}")
        ids.add(participant)
        rows.extend(score(record))
    if not rows:
        raise ValueError("No complete sessions to score.")
    return rows
