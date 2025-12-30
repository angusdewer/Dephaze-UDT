 # Dephaze UDT v1.1 – Hybrid Structural & Generative Ontology Engine

**Canonical implementation (DOI):** [https://doi.org/10.5281/zenodo.17965773](https://doi.org/10.5281/zenodo.17965773)

This repository mirrors the published **Dephaze UDT v1.1** implementation. It represents a fundamental evolution from static structural analysis to a hybrid cognitive architecture capable of **controlled generation**.

---

### What this is
**Dephaze UDT is a "Zero-Fit" cognitive engine.**

It solves the fundamental reliability problems of modern AI (hallucination, opacity, catastrophic forgetting) by strictly separating **Structure (Memory)** from **Generation (Creativity)**.

It is **NOT** a standard AI model:
❌ **No Large Language Models (LLMs)**  
❌ **No Neural Networks (Backpropagation)**  
❌ **No Statistical Fitting / Training Runs**  
❌ **No Black-Box Weights**  

Instead, Dephaze UDT operates as a **Phase-Field System**. It uses geometric invariants ($\Phi^3$) to regulate information processing, distinguishing between deterministic facts and generative hypotheses.

---

### The v1.1 Hybrid Architecture

The system consists of three distinct, interacting components:

#### 1. The UDT Core (Structure)
A fully deterministic phase-space engine. It projects symbolic input into continuous phase coordinates ($\theta, \phi, \rho$).
*   **Function:** If a concept aligns with the existing **Atlas** (star map), the system returns a **FACT** with 100% stability.
*   **Behavior:** It never "hallucinates" known data. It acts as a rigid, trustworthy knowledge graph.

#### 2. The $\Phi^3$ Flux Motor (Generation)
A generative engine that replaces the stochastic randomness of LLMs with geometric perturbation.
*   **Trigger:** When the UDT Core detects low confidence (uncertainty), it ignites the Flux Motor.
*   **Function:** It generates a controlled phase-drift based on the $\Phi^3$ (cubic golden ratio) invariant. This allows the system to create novel **HYPOTHESES** and navigate the semantic gap between known concepts.

#### 3. The Gödel Filter (Validation)
A topological auditor (The "Józan Ész").
*   **Function:** It evaluates the output of the Flux Motor against the structural constraints of the Atlas.
*   **Logic:**
    *   If the generated idea is topologically distinct but resonant $\rightarrow$ **Accepted Hypothesis**.
    *   If the idea is topologically incoherent (too far from any structure) $\rightarrow$ **Rejected Noise**.

---

### Core Concepts

**Phase Field (Imago)**  
Deterministic mapping of input into a continuous phase space. Not embeddings, not vectors, but geometric coordinates.

**Atlas (Star Map)**  
A compact, static reference topology. The Atlas does not "learn" weights; it anchors coordinates. Knowledge is added by **Committing Stars**, an additive process that prevents catastrophic forgetting.

**Lambda (Λ) & Sigma (Σ)**  
Operators for ontological mode selection and coherence tracking. They ensure the system remains stable even during generative cycles.

**Safe Mode by Default**  
The system explicitly distinguishes between *retrieved structure* and *generated flux*, eliminating the deception inherent in probabilistic language models.

---

### Running the System

#### 1. Interactive Console (The Starship)
This executes the main logic loop, including the Flux Motor and Gödel Filter.
```bash
python run_udt.py
```
*   *Try entering a known term:* The system returns a **FACT** (UDT).
*   *Try entering an abstract concept:* The system ignites the **FLUX MOTOR** and generates a **HYPOTHESIS**.

#### 2. Headless CLI (Scripting)
Force the system to generate hypotheses by setting a high flux threshold:
```bash
python cli.py "the topology of a pancake universe" --flux-threshold 0.95
```

#### 3. Growing the Mind (Atlas Commit)
To make the system smarter, do not train it. **Map it.**
```bash
python atlas_commit.py "Quantum Physics"
```
This permanently anchors the concept in the phase space.

---

### External Data Access (Wiki)
Wikipedia access is explicit, optional, and governed.
*   No background crawling.
*   No data ingestion.
*   Used only as an external reference signal to validate internal hypotheses.

---

### Status & License

**Status:** Canonical implementation archived on Zenodo.  
**State:** STABLE / HYBRID (v1.1)  
**Determinism:** HARD (Seed-based entropy for Flux)  

© 1992–2025 Angus Dewer / Dephaze Manufacture  
All rights reserved. Use, reproduction, modification, or redistribution requires explicit written permission from the author. See LICENSE.txt for details.

**The code is complete. The map is yours to build.**
```
