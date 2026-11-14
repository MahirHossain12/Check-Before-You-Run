# Check Before You Run

**An HCI study prototype for verifying AI-suggested Python code**

Does predicting what a test should return before running it help novice programmers design better tests on an unfamiliar problem?

This project follows *Read, Check, Revise*. It moves from checking written AI explanations against documentation to checking candidate code against a specification. Two interfaces vary the order of the same verification activity.

| Condition | Practice flow |
| --- | --- |
| A · Run first | Select an input → see actual output → judge whether it meets the specification |
| B · Predict first | Select an input and commit to its expected output → see actual output → judge whether it meets the specification |

Both use the same tasks, input choices, code, and output engine. B also displays the learner's submitted prediction with the actual output. Each practice trial is immediately followed by a new test-design task with no runner or feedback.

## Try it

Open [demo/session.html](demo/session.html) locally for a four-round walkthrough. The prototype runs offline and exports JSON. Its fixed candidate snippets are authored study materials modeling common mistakes in AI-suggested code. The browser shows outputs verified by Python over the finite input domain. The project requires no model, API key, backend, or GPU.

## Run in Colab

Extract this archive for GitHub and upload the project folder contents. From Colab, open each notebook via **File → Open notebook → GitHub** or upload the notebook from your computer. In a fresh Colab runtime, its first cell asks for the original project ZIP and extracts its contents. Run cells from top to bottom. The final two notebooks include controls for scoring browser exports and analyzing participant data when available.

| Notebook | Deliverable |
| --- | --- |
| [01 · Study Design](01_Study_Design.ipynb) | Research question, counterbalancing, and session assignments |
| [02 · Stimuli and Validation](02_Stimuli_and_Validation.ipynb) | Practice and transfer tasks, verified over every permitted input |
| [03 · Browser Prototype](03_Browser_Prototype.ipynb) | Generate and download a session HTML |
| [04 · Data and Scoring](04_Data_and_Scoring.ipynb) | Validate sessions and score testing behavior and transfer |
| [05 · Analysis and Reporting](05_Analysis_and_Reporting.ipynb) | Descriptive results, paired differences, and an exportable figure |

For local Jupyter, start it from the repository root, use Python 3.10+, and install Matplotlib for Notebook 05. The other notebooks use the standard library and the IPython environment provided by Jupyter or Colab.

## Study and data

The primary outcome is a valid counterexample on the immediate independent task. A response must include a permitted input for which the candidate disagrees with the specification, plus the correct expected output. The analysis also distinguishes weak input selection from an incorrect expected output. See [the protocol](study/protocol.md) for assignment, recruitment, and limitations.

The downloadable demo and synthetic results demonstrate the pipeline. Participant sessions are pending. The example chart uses synthetic data.

## Research basis

- Kazemitabaar et al. (CHI 2024), [CodeAid](https://doi.org/10.1145/3613904.3642773), used AI feedback designed to support students without revealing complete code solutions.
- [When AI Is Wrong on Purpose](https://icer2026.acm.org/details/icer-2026-papers/29/When-AI-Is-Wrong-on-Purpose-How-Students-Respond-to-Buggy-GenAI-Code) (ICER 2026) examined how learners responded to realistic bugs deliberately seeded in generated code.
- [How students use generative AI for software testing](https://link.springer.com/article/10.1007/s10664-026-10898-0) (Empirical Software Engineering, 2026) observed novice testing workflows and reported subtle assertion mismatches, motivating the separate scoring of input and expected output.
- Bastani et al. (PNAS, 2025), [Generative AI without guardrails can harm learning](https://doi.org/10.1073/pnas.2422633122), assessed later unassisted performance in mathematics. This project uses an immediate unaided task in introductory programming.
