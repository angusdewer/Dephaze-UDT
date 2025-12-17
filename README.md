# Dephaze UDT

> **Canonical implementation (DOI):** https://doi.org/10.5281/zenodo.17964792

This repository mirrors the published **Dephaze UDT v1.0** implementation.  
The canonical, citable reference is the Zenodo record above.

---

## What this is

**Dephaze UDT is a **deterministic structural ontology engine**.

It is **not** an AI model in the conventional sense.

- ❌ No large language models (LLMs)
- ❌ No machine learning
- ❌ No training or fine-tuning
- ❌ No statistical fitting
- ❌ No server-side components

Instead, Dephaze UDT operates as a **phase-field–based structural interpreter**.

Symbolic input is deterministically projected into a continuous phase space (θ, φ, ρ), followed by explicit structural decision-making via Lambda (Λ) and Sigma (Σ) operators.

---

## Core concepts

- **Phase field (Imago)**  
  Deterministic mapping of input into a continuous phase space (not embeddings, not vectors, not learned representations).

- **Lambda (Λ)**  
  Ontological mode selection (entity, group, definition, etc.).

- **Sigma (Σ)**  
  Coherence tracking and branch isolation (no drift, no cross-contamination).

- **Atlas (star map)**  
  A compact, static reference topology anchoring phase dynamics. The Atlas does **not** learn, does **not** grow, and does **not** store data.

- **Gödel field**  
  Language-facing layer for extracting relations and mentions. It does not control decisions and does not feed back into learning.

- **GRM (Global Relation Model)**  
  World-state representation using immutable, lockable snapshots.

---

## Learning without learning

Dephaze UDT can become **faster and more coherent over time** without learning.

This emerges from:
- reduced phase uncertainty
- stabilized trajectories in phase space
- reuse of static structural references (Atlas)

No parameters are updated.  
No data is accumulated.  
No models are trained.

Coherence emerges from **structure**, not optimization.

---

## External data access (Wiki)

- Wikipedia access is **explicit, optional, and governed**
- No background crawling
- No data ingestion
- No storage of external content

Only a minimal, controlled Wikipedia provider is included.

---

## What this is NOT

- ❌ Not a language model
- ❌ Not a chatbot
- ❌ Not a neural network
- ❌ Not a probabilistic system
- ❌ Not an autonomous learner

This repository **does not** implement the full **DephazeAI** cognitive architecture or the **NORTH** system described elsewhere.

It provides a **deterministic structural substrate** inspired by the broader Dephaze framework.

---

## Running the system
 
### Core Demo (Recommended)
This executes the main logic loop directly:
```bash
python run_udt.py
### Requirements
- Python **3.10 – 3.13**
- No external dependencies

License
© 1992–2025 Angus Dewer / Dephaze Manufacture
All rights reserved.
Use, reproduction, modification, or redistribution requires explicit written permission from the author.
See LICENSE.txt for details.
Dewer, Angus. (2025).
Dephaze UDT – Deterministic Structural Ontology Engine (Implementation Layer) (v1.0).
Zenodo. https://doi.org/10.5281/zenodo.17964792
Status
 Canonical implementation archived on Zenodo
 Deterministic and reproducible
 No training, no learning, no LLMs
 Ready for inspection and further development
