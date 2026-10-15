# 3-Minute Live Hackathon Pitch Script
## Project: Ragas Contrastive Evaluation Studio & Grounding Observability
### Track: Track C — Contrastive Speech & Grounding Verification

---

### [0:00 - 0:30] Hook & Problem Statement
> **Presenter:**  
> "Judges, consider this: An AI assistant reads a quarterly 10-K report and confidently answers:  
> *'The company invested $4.9B in data centers and forecasted $7.5B for 2026.'*  
> It sounds authoritative. It sounds fluent. But the 2026 forecast is completely fabricated—a pure hallucination.  
> In healthcare, enterprise finance, or mission-critical cloud ops, this isn't just an inaccuracy; it's a multi-million-dollar liability.  
> The fundamental problem? Current evaluation tools give you a single composite number like '0.78' and leave you guessing *where* the model failed.  
> Today, we're introducing the **Ragas Contrastive Evaluation Studio**."

---

### [0:30 - 1:15] The Breakthrough Solution
> **Presenter:**  
> "Instead of evaluating candidate answers in a vacuum, we built a **Contrastive A/B Grounding Engine** that pits an **Ideal Grounded Response** against a **Flawed, Hallucinating Variant** in real time.  
> 
> *[Presenter clicks '🚀 1-Click Hackathon Demo' in the Studio navbar]*  
> 
> In less than 300 milliseconds, our engine has:  
> 1. Split both answers into atomic claims.  
> 2. Verified each claim's semantic grounding against retrieved source chunks.  
> 3. Highlighted the hallucinated claim in bright coral with an alert badge: *'Claim 2: CapEx expansion budget of $7.5B has zero supporting evidence in source filings.'*  
> 4. Computed the exact **Quality Advantage (+20.0%)** and **Faithfulness Disparity (+50.0%)**."

---

### [1:15 - 2:00] Deep Dive: Dual Radar & Codebase Transparency
> **Presenter:**  
> "Take a look at the interactive canvas radar chart in the center of the screen.  
> You aren't looking at a single polygon—you're looking at a **dual-polygon overlay**.  
> The green polygon represents Model A (Ideal); the coral polygon represents Model B (Flawed). You can visually see the exact dimensional deficit—faithfulness plunging while semantic relevance stays deceptively high.  
> 
> Next, judges asked: *'How can we trust this evaluation logic without jumping to GitHub or inspecting messy terminal logs?'*  
> 
> *[Presenter clicks the 'Repo Code Explorer' tab]*  
> 
> We integrated the **entire Ragas repository right into the dashboard**. With zero external network requests, judges and developers can click into `src/ragas/metrics/_faithfulness.py` or `evaluator.py`, inspect line-by-line formulas, and copy production snippet examples directly from the UI."

---

### [2:00 - 2:30] Architectural Rigor & Zero-Dependency Execution
> **Presenter:**  
> "Under the hood:  
> - **Dual-Mode Engine:** Runs 100% offline using deterministic token stemming, n-gram Jaccard matching, and Dice lexical overlap. If OpenAI credentials are provided, it seamlessly hot-swaps to full Ragas LLM evaluators.  
> - **Automated Test Coverage:** 26 out of 26 pytest integration tests passing with 100% reliability.  
> - **Zero-Config Deployment:** Ready for production with a multi-stage `Dockerfile` and `docker-compose.yml`."

---

### [2:30 - 3:00] Call to Action & Conclusion
> **Presenter:**  
> "The Ragas Contrastive Evaluation Studio turns AI evaluation from an ambiguous black box into a deterministic, reproducible, and actionable engineering discipline.  
> You can try it right now at `http://127.0.0.1:8000` or inspect our complete open-source codebase.  
> Thank you, and we'd love to take your questions!"

---

## Judge Q&A Preparation Cheat Sheet

| Potential Judge Question | Best Response |
|---|---|
| **"Why contrastive evaluation instead of absolute evaluation?"** | "Absolute evaluation tells you that an answer scored 0.75, but doesn't explain what a 1.0 looks like or what specific assertion caused the drop. Contrastive evaluation isolates the precise delta—showing the exact clause where hallucination was introduced while holding retrieval context constant." |
| **"Does this require an expensive OpenAI API key?"** | "No! We engineered a deterministic heuristic fallback that decomposes claims, stems tokens, and computes exact lexical grounding offline. When API keys are supplied, it upgrades automatically to LLM-as-a-judge." |
| **"How does this align with Track C?"** | "Track C requires constructing contrastive 'ideal' vs 'flawed' datasets, generating rubric-based scores, and providing actionable feedback. We built 3 curated enterprise scenarios (Finance, Medical, DevOps), multi-axis scoring, and visual side-by-side claim drilldowns." |
| **"Can I deploy this in our Kubernetes/Enterprise cloud?"** | "Yes, we provide a production `Dockerfile` and `docker-compose.yml` with health check probes (`/api/health`, `/api/ready`) ready for microservice orchestration." |
