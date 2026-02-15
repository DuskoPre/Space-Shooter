## **A Feasibility-Margin Theory of Hallucination Reduction in LLM-Orchestrated Code Generation**

**Author:** (Draft for your AutoCoder concept)  
**Keywords:** hallucination, confabulation, prompt design, constraint satisfaction, orchestration, software agents, feasibility margin, verification

### **Abstract**

Hallucinations in large language models (LLMs)—fluent outputs that are unfaithful to available evidence or constraints—remain a core barrier to reliable automation. Prior work attributes hallucinations partly to training and evaluation incentives that reward guessing rather than calibrated uncertainty. ([arXiv](https://arxiv.org/abs/2509.04664?utm_source=chatgpt.com)) This paper proposes a theory for reducing hallucinations in program synthesis settings by **maximizing feasibility margin**: keeping task constraints within a region of the model’s distribution where multiple correct completions are likely, while delegating rigid selection/validation to an external orchestrator. The theory predicts a **constraint–support phase transition** (“hallucination barrier”) in which overly tight, high-coupling objectives drive the model to fabricate details to satisfy incompatible demands. We formalize the hypothesis, connect it to established mitigation methods (verification prompting, self-consistency, retrieval augmentation), and derive prompt and orchestration design principles for multi-agent code generation systems. ([arXiv](https://arxiv.org/abs/2303.08896?utm_source=chatgpt.com))

---

### **1\. Introduction**

LLMs are increasingly used as autonomous coding agents. In such settings, hallucinations often manifest as: nonexistent APIs, incorrect imports, fabricated file structure, or invented prior context. While larger models can reduce some error modes, they can also increase *confident fabrication* if prompts create impossible or underspecified constraint bundles.

The core thesis here is aligned with your intuition: **hallucinations rise sharply when we push the model beyond a “no-return barrier,” where it cannot satisfy constraints using high-probability continuations**, so it begins “confabulating” plausible-looking content. ([Nature](https://www.nature.com/articles/s41586-024-07421-0?utm_source=chatgpt.com)) The proposed remedy is not merely “simplify prompts,” but **engineer objectives and agent interfaces so the LLM is rarely forced into low-support regions**—and when it is, it is explicitly allowed to say “uncertain” and defer to orchestration.

---

### **2\. Background and related work**

**Definitions.** Hallucinations are commonly framed as outputs unfaithful to source content or evidence; recent work distinguishes “confabulations”: fluent claims that are wrong and *arbitrary* (sensitive to irrelevant factors such as random seed). ([Nature](https://www.nature.com/articles/s41586-024-07421-0?utm_source=chatgpt.com)) Surveys emphasize that “hallucination” spans multiple mechanisms and tasks, from summarization unfaithfulness to open-domain factual fabrication. ([ACM Digital Library](https://dl.acm.org/doi/10.1145/3703155?utm_source=chatgpt.com))

**Why hallucinations happen.** A prominent line argues that training pipelines reward guessing and penalize abstention, producing a “student guessing on an exam” behavior under uncertainty. ([arXiv](https://arxiv.org/abs/2509.04664?utm_source=chatgpt.com))

**Mitigation patterns.**

* **Verification prompting:** Chain-of-Verification (CoVe) drafts an answer, generates verification questions, answers them independently, and revises; it reduces hallucinations across tasks. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))  
* **Self-consistency / self-checking:** SelfCheckGPT detects hallucination signals via disagreement across stochastic samples. ([arXiv](https://arxiv.org/abs/2303.08896?utm_source=chatgpt.com))  
* **Retrieval augmentation:** Retrieval-in-the-loop can reduce hallucination in conversation and grounded generation by anchoring claims to external evidence. ([arXiv](https://arxiv.org/abs/2104.07567?utm_source=chatgpt.com))

These methods share a theme: **don’t force a single brittle completion; instead create a space of candidates \+ external checks**.

---

### **3\. Theory: the Feasibility-Margin Hypothesis**

#### **3.1 Informal statement**

Given an objective (x), an LLM defines a conditional distribution over completions (p(y \\mid x)). When the prompt imposes constraints (C) (format requirements, file names, APIs, behavior, etc.), the model must produce some (y) in the constrained set (Y\_C).

**Hypothesis (Feasibility Margin):**  
Hallucination probability increases as the probability mass (P(Y\_C \\mid x)) decreases. When (P(Y\_C \\mid x)) falls below a threshold, the system crosses a **hallucination barrier**: the model continues producing fluent text, but increasingly fabricates details to appear compliant.

This matches observed “confabulation” behavior: when the model cannot reliably ground an answer, it still outputs something plausible, often sensitive to sampling noise. ([Nature](https://www.nature.com/articles/s41586-024-07421-0?utm_source=chatgpt.com))

#### **3.2 Constraint–support tradeoff (why “simplicity” helps)**

“Simplicity” (as you’re using it) reduces:

* **Constraint density:** number of independent requirements per token budget  
* **Cross-file coupling:** constraints that require consistent coordination across multiple outputs (imports, filenames, shared interfaces)  
* **Latent dependencies:** hidden requirements not stated but assumed by the user (runtime environment, libraries, OS)

All of these increase the chance that a completion violates something. The LLM can respond by (a) admitting uncertainty, or (b) fabricating coherence. Because many training setups reward coherence over abstention, (b) is common under pressure. ([arXiv](https://arxiv.org/abs/2509.04664?utm_source=chatgpt.com))

#### **3.3 The “orchestration slack” principle (your key idea)**

Your “leave room for different interpretations” maps to a useful engineering move:

* **In the LLM layer:** Allow a *manifold* of valid solutions (multiple acceptable implementations).  
* **In the orchestration layer:** Enforce correctness via tests, validators, checklists, and iterative repair.

So the LLM is not forced to nail a single brittle path; instead it proposes within a feasible region, and the orchestrator chooses/repairs. This is conceptually aligned with CoVe’s verify-and-revise loop and SelfCheckGPT’s reliance on variance signals. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))

---

### **4\. Implications for multi-agent code generation (your AutoCoder-style system)**

Your architecture (task initializer → refactor → details → context → assignment → execution) is effectively a **controller** around the LLM. This paper’s theory suggests three concrete design rules for that controller:

#### **Rule 1: Minimize coupling per task (maximize per-task feasibility mass)**

Each isolated task should:

* touch **one file** (or one atomic operation),  
* require **one obvious interface**,  
* include **explicit imports** and **explicit call signatures**,  
* avoid depending on unstated outcomes of other tasks.

This aligns with your insistence: “each agent sees only one task.”

#### **Rule 2: Separate “creative degrees of freedom” from “hard constraints”**

* Put **hard constraints** in a short “contract” section (filenames, function names, signatures).  
* Put “allowed variation” explicitly (e.g., “Any CLI parsing approach is acceptable; do not add extra files.”)

This reduces accidental overfitting to an implied-but-wrong interpretation.

#### **Rule 3: Use verification gates early and cheaply**

Before running full integration:

* syntax check / import check,  
* unit tests for each class/function,  
* smoke-run for CLI.

This is compatible with CoVe’s observation: verification subquestions are often easier than the original generation problem. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))

---

### **5\. Testable predictions and evaluation protocol**

The theory becomes useful if it predicts measurable behaviors.

#### **5.1 Feasible-mass proxy metrics**

You can approximate “feasibility margin” by:

* **Constraint count** per objective token (or per line)  
* **Coupling score**: number of shared symbols spanning multiple files/tasks (imports, names)  
* **Format rigidity**: strict JSON-only vs free-form  
* **Ambiguity allowance**: explicit “any of these patterns are acceptable”

#### **5.2 Predicted outcomes**

1. Increasing coupling (multi-file requirements, shared interfaces, strict formatting) increases hallucinations sharply beyond a threshold.  
2. Allowing explicit variation (“any valid approach”) reduces hallucinations *when paired with orchestration checks*.  
3. Disagreement across samples (SelfCheck-like variance) rises as feasible mass drops; it can be used as an early warning signal. ([arXiv](https://arxiv.org/abs/2303.08896?utm_source=chatgpt.com))  
4. Adding verification steps reduces hallucinations more efficiently than further constraining the initial prompt. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))

A practical benchmark for your system could measure:

* rate of missing/incorrect imports,  
* non-existent file references,  
* “extra file creep” (models creating README/setup when not requested),  
* pass rate on generated unit tests.

(Recent benchmarks exist for hallucination evaluation broadly, though coding-focused variants would be your contribution.) ([ACL Anthology](https://aclanthology.org/2025.acl-long.1176.pdf?utm_source=chatgpt.com))

---

### **6\. Practical prompt/agent design derived from the theory**

#### **6.1 Objective template: “Contract \+ Slack \+ Acceptance”**

Example for your temperature converter objective:

* **Contract (hard):** exact filenames, class name, method signatures, I/O behavior.  
* **Slack (allowed):** any implementation details, any input parsing style, any formatting of numbers (within reason).  
* **Acceptance tests:** show 2–4 input/output examples or unit tests.

This is “simplicity,” but with **explicit slack** rather than implicit ambiguity.

#### **6.2 Add a “feasibility margin” clause to system prompts**

You asked: *could this be part of the system message?*  
Yes—**but as a short set of operating principles**, not the full paper (system prompts are precious token-budget and long prompts can backfire).

Here is a compact “LLM-language” version you can embed (or paraphrase) in your system messages:

**Feasibility-Margin System Principles (short):**

1. Prefer solutions that satisfy all explicit constraints with the fewest assumptions.  
2. If a requirement is underspecified, state 1–2 minimal assumptions and proceed; do not invent extra requirements.  
3. Keep outputs within the requested scope; do not add files, features, or dependencies unless explicitly required.  
4. When multiple implementations are valid, choose the simplest conventional approach.  
5. If constraint conflicts are detected, surface the conflict explicitly and propose the smallest correction.

That directly operationalizes “don’t push past the barrier” by encouraging abstention/assumptions instead of fabrication.

#### **6.3 Where to inject it in your pipeline**

Given your functions, the highest leverage places are:

* **code\_tasks\_initializer\_agent:** make tasks low-coupling; include slack & acceptance criteria.  
* **code\_tasks\_details\_agent / context\_agent:** add the missing “contract and assumptions” explicitly so isolated agents don’t invent.  
* **code\_writer\_agent:** enforce “no extra files/no extra features,” and “declare assumptions.”

You can also add a lightweight *variance check* gate: for tasks that historically hallucinate (imports / file paths), sample 2–3 times and compare—SelfCheck-style—then route to verification/refactor if variance is high. ([arXiv](https://arxiv.org/abs/2303.08896?utm_source=chatgpt.com))

---

### **7\. Limitations**

1. **Not all hallucinations are constraint pressure.** Some are factual gaps, stale knowledge, or tool/API drift—retrieval or explicit environment introspection may be needed. ([arXiv](https://arxiv.org/abs/2104.07567?utm_source=chatgpt.com))  
2. **Slack without verification can reduce correctness.** The theory explicitly requires orchestration checks (tests, validators).  
3. **Calibration remains hard.** Even with “admit uncertainty” instructions, models may still guess due to training incentives. ([arXiv](https://arxiv.org/abs/2509.04664?utm_source=chatgpt.com))

---

### **8\. Conclusion**

This paper proposed the **Feasibility-Margin Theory**: hallucinations emerge as a phase transition when prompts overconstrain the model relative to its internal support, pushing it into confabulation. The practical remedy is to **maximize feasible mass** by simplifying and decoupling tasks, **explicitly allowing controlled variation**, and moving rigid selection and correctness enforcement into an **orchestration layer** with verification gates. This framing unifies and explains why verification prompting (CoVe), self-consistency checks (SelfCheckGPT), and retrieval augmentation reduce hallucinations: all increase effective feasibility or add external constraints after generation rather than before. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))

---

## **Direct answer to your last question (system message?)**

Yes—**the *paper* should not be embedded**, but the **core principles** (feasibility margin, minimal assumptions, explicit slack, no extra scope, surface conflicts) are perfect as a *short* system-message “constitution.”

If you want, I can also rewrite **your existing system messages** (initializer/refactor/details/context/writer) into tighter versions that:

* reduce cross-file coupling,  
* force a “Contract / Allowed Variation / Acceptance” structure per task,  
* add an explicit “Assumptions” field,  
* and add a variance-triggered “verify” route inspired by CoVe/SelfCheck. ([arXiv](https://arxiv.org/abs/2309.11495?utm_source=chatgpt.com))

#cloude opus comment

Looking at your AutoCoder system and the feasibility-margin theory document, yes, this is highly plausible and theoretically sound. Let me break down why:
Why This Is Plausible
1. The Theory Maps Well to Your Architecture
The feasibility-margin hypothesis explains a real phenomenon you're likely experiencing:
When you give agents overly coupled, underspecified tasks, they hallucinate (invent imports, create extra files, fabricate APIs)
Your multi-agent pipeline with task decomposition is already implementing the core idea: maximize feasibility by breaking constraints into independent chunks
2. Your System Already Uses Key Mitigation Patterns
Looking at your code, you're already doing several things the theory recommends:
Task isolation via code_tasks_context_agent - each agent sees only one task
Verification loops - your refactor and relevance agents act as checks
External orchestration - the task assigner and file management agents enforce constraints outside the LLM
Retrieval augmentation - ChromaDB provides grounding context
3. The "Liquid Neural Network" Framing Makes Sense
Your classifier + ChromaDB approach does introduce dynamic adaptability:
Classifiers route tasks based on current state
ChromaDB provides external memory that evolves
This creates feedback loops that static LLMs lack
It's not a true liquid neural network (which has continuous-time dynamics and adaptive weights), but it's a practical approximation - a "semi-liquid" system where routing and context are fluid even if the core LLM weights are frozen.
What You Should Do Next
Immediate Wins (Easy Improvements)
Based on the theory, here's what would help most:
Add Explicit "Contract + Slack" Structure to Tasks
Modify your code_tasks_details_agent to enforce:
# Each task should have:
{
    "hard_constraints": {
        "filename": "temperature_converter.py",
        "class_name": "TemperatureConverter", 
        "method_signatures": ["celsius_to_fahrenheit(self, celsius: float) -> float"]
    },
    "allowed_variation": "Any implementation approach is acceptable. No extra files.",
    "acceptance_test": "converter.celsius_to_fahrenheit(0) == 32.0"
}

Add a "Feasibility Check" Before Code Generation
Insert a lightweight agent that checks if a task has too many constraints:
def task_feasibility_agent(task: str, context: str):
    system_message = """Count the number of hard constraints in this task:
    - File paths that must match exactly
    - Import statements that must exist
    - Function signatures that must be precise
    - Cross-file dependencies
    
    If count > 5, flag as HIGH_COUPLING. Suggest splitting the task."""

Implement the "Assumptions" Field
Add to your code_writer_agent:
prompt_message = f"""...
If any requirement is underspecified, state 1-2 minimal assumptions and proceed.
Do NOT invent extra requirements (like README files, setup.py, etc.).

Return JSON:
{{
    "assumptions": ["Assuming standard library only", "No input validation needed"],
    "code": "<your code>"
}}
"""

Medium-Term Improvements
Add SelfCheck-style Variance Detection
For high-risk tasks (imports, file paths), generate 2-3 samples and check agreement:
if chosen_agent == "code_writer_agent":
    samples = [code_writer_agent(task_description, task_isolated_context, relevant_chunks) 
               for _ in range(3)]
    
    # If imports differ across samples, it's a hallucination warning
    if detect_import_disagreement(samples):
        print_colored_text("⚠️ HIGH UNCERTAINTY - Running verification", "red")
        # Trigger refactor or ask for clarification

Embed Core Principles in System Messages
Add this to your code_writer_agent system message:
system_message = """You are an AGI agent responsible for writing code to accomplish a given task.

Operating principles:
1. Satisfy all explicit constraints with minimal assumptions
2. If underspecified, state 1-2 assumptions and proceed - do NOT invent requirements
3. Stay within requested scope - no extra files/features unless required
4. If multiple approaches work, choose the simplest conventional one
5. If constraints conflict, surface the conflict explicitly

Your goal is to analyze the provided task and write necessary code in format: {"code": "<actual Python code>", "assumptions": ["assumption 1", "assumption 2"]}"""

Bottom Line
Your intuition is correct: the feasibility-margin theory explains why simpler, decoupled tasks reduce hallucinations. Your AutoCoder architecture is already moving in the right direction. The easy wins are:
Make "slack" and "assumptions" explicit in task structure
Add lightweight feasibility checks before generation
Use variance across samples as an early warning system
Update system messages with the core principles
This won't require restructuring your system - just adding explicit metadata and checks at strategic points in your pipeline.
