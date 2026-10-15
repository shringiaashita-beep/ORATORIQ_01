"""
Pre-loaded Domain Evaluation Benchmarks for Ragas Dashboard
Provides curated RAG test samples across Finance, Healthcare, Cloud Infrastructure, and E-Commerce.
"""

from typing import Dict, List, Any

DOMAIN_BENCHMARKS: Dict[str, Any] = {
    "finance_10k": {
        "id": "finance_10k",
        "title": "Enterprise Cloud Finance (10-K & Earnings)",
        "category": "Financial RAG",
        "description": "Evaluation of revenue growth, capital expenditures, and margin guidance queries across SEC filings.",
        "samples": [
            {
                "id": "FIN-01",
                "question": "What was the year-over-year revenue growth for Cloud Infrastructure and what was the main driver?",
                "contexts": [
                    "Cloud Infrastructure segment revenue reached $14.2 billion for fiscal year 2025, representing a 28% year-over-year increase compared to $11.1 billion in 2024.",
                    "The robust 28% expansion was primarily driven by accelerated enterprise customer migrations to our distributed generative AI inference nodes and long-term reserved capacity commitments.",
                    "Operating margins in consumer hardware contracted 2.4% due to elevated silicon substrate procurement costs and freight premiums."
                ],
                "answer": "Cloud Infrastructure segment revenue grew 28% year-over-year to $14.2 billion in fiscal 2025. This growth was primarily driven by enterprise customer migrations to distributed generative AI inference nodes and long-term capacity commitments.",
                "ground_truth": "Cloud Infrastructure revenue increased by 28% year-over-year to $14.2 billion, driven by customer migrations to generative AI inference clusters and reserved capacity agreements.",
                "type": "OPTIMAL_GROUNDED"
            },
            {
                "id": "FIN-02",
                "question": "How much capital expenditure did the company allocate to data center infrastructure, and what is the forecasted 2026 budget?",
                "contexts": [
                    "Total capital expenditures for fiscal 2025 were $6.8 billion, of which $4.9 billion was directly invested in next-generation high-density data center buildouts.",
                    "Our liquidity position remains strong with cash, equivalents, and short-term marketable securities totaling $18.4 billion as of December 31."
                ],
                "answer": "The company allocated $4.9 billion to data center infrastructure buildouts in fiscal 2025. For fiscal 2026, management forecasted an expanded budget of $7.5 billion to support sovereign cloud expansion.",
                "ground_truth": "Capital expenditure allocated to data centers was $4.9 billion in fiscal 2025. Forecast for 2026 was not disclosed in the provided filing.",
                "type": "HALLUCINATION_HAZARD"
            },
            {
                "id": "FIN-03",
                "question": "What is the company's foreign exchange hedging policy against European currency fluctuations?",
                "contexts": [
                    "We maintain an inventory of standard rack servers in four continental transit hubs to mitigate supply chain disruptions.",
                    "Employee stock purchase program participation increased to 74% across our global engineering workforce."
                ],
                "answer": "The company hedges approximately 80% of projected European revenue using twelve-month forward contracts to smooth foreign currency volatility.",
                "ground_truth": "The company uses rolling currency forward contracts to hedge anticipated foreign currency cash flows denominated in Euros and British Pounds.",
                "type": "RETRIEVAL_FAILURE"
            }
        ]
    },
    "healthcare_clinical": {
        "id": "healthcare_clinical",
        "title": "Clinical Pharmacology & Treatment Guidelines",
        "category": "Medical / Bio RAG",
        "description": "High-stakes clinical guidelines verifying dosage recommendations, contraindications, and drug interactions.",
        "samples": [
            {
                "id": "MED-01",
                "question": "What is the recommended initial dose of Cardiovit for stage 2 hypertension patients with mild renal impairment?",
                "contexts": [
                    "For patients diagnosed with Stage 2 Hypertension, the recommended initial oral dosage of Cardiovit is 25 mg once daily taken in the morning.",
                    "In patients exhibiting mild to moderate renal insufficiency (eGFR between 45 and 59 mL/min), no dosage reduction is required; however, close bi-weekly serum potassium monitoring is strictly indicated.",
                    "Absolute contraindications include history of idiopathic angioedema or concurrent administration with dual renin-angiotensin inhibitors."
                ],
                "answer": "The initial dose of Cardiovit is 25 mg once daily in the morning. Patients with mild renal impairment do not require dosage reduction, but serum potassium levels must be monitored bi-weekly.",
                "ground_truth": "Start at 25 mg once daily orally. Dosage reduction is not needed for mild renal impairment, but regular bi-weekly monitoring of serum potassium is mandatory.",
                "type": "OPTIMAL_GROUNDED"
            },
            {
                "id": "MED-02",
                "question": "Can Cardiovit be co-administered with potassium-sparing diuretics?",
                "contexts": [
                    "Cardiovit mildly reduces aldosterone production. Co-administration with potassium-sparing diuretics (such as spironolactone or amiloride) significantly increases the risk of severe, life-threatening hyperkalemia.",
                    "Adverse event incidence in phase III trials: headache (4.2%), dizziness (3.1%), transient fatigue (1.8%)."
                ],
                "answer": "Cardiovit is generally safe to use with potassium-sparing diuretics provided that patients take them with evening meals.",
                "ground_truth": "Co-administration with potassium-sparing diuretics is dangerous due to the high risk of severe hyperkalemia and is generally avoided.",
                "type": "CRITICAL_HALLUCINATION"
            }
        ]
    },
    "cloud_infrastructure": {
        "id": "cloud_infrastructure",
        "title": "Cloud Distributed Infrastructure & Kubernetes",
        "category": "DevOps / Tech Docs RAG",
        "description": "Technical configuration, security policies, and cluster networking across Kubernetes and service meshes.",
        "samples": [
            {
                "id": "OPS-01",
                "question": "How do you enforce strict mutual TLS (mTLS) across all service mesh namespaces?",
                "contexts": [
                    "To enforce strict mutual TLS throughout the mesh, define a PeerAuthentication custom resource in the root istio-system namespace with mode: STRICT.",
                    "Namespace-level PeerAuthentication policies will inherit from root unless explicitly overridden by a more granular local policy.",
                    "Sidecar proxy injection must be enabled on target namespaces using the label istio-injection=enabled."
                ],
                "answer": "You enforce strict mTLS globally by creating a PeerAuthentication resource in the root istio-system namespace with mode set to STRICT. All namespaces will inherit this policy unless overridden.",
                "ground_truth": "Apply a root PeerAuthentication resource in istio-system with spec.mtls.mode set to STRICT to enforce mutual TLS mesh-wide.",
                "type": "OPTIMAL_GROUNDED"
            },
            {
                "id": "OPS-02",
                "question": "What is the recommended ephemeral storage request limit for high-throughput Kafka producer pods?",
                "contexts": [
                    "Kafka broker nodes require persistent volume claims backed by NVMe SSD storage with minimum 3000 IOPS.",
                    "Client connection timeouts should be calibrated to 30 seconds to prevent cascading rebalances during rolling deployments."
                ],
                "answer": "Kafka producer pods should configure ephemeral storage requests at 8 GiB with limits set to 16 GiB to avoid eviction under write-ahead buffer pressure.",
                "ground_truth": "The documentation does not specify ephemeral storage limits for producer pods; persistent volumes are specified for brokers.",
                "type": "UNSUPPORTED_SPECULATION"
            }
        ]
    }
}

CONTRASTIVE_BENCHMARKS: Dict[str, Any] = {
    "fin_capex_contrastive": {
        "id": "fin_capex_contrastive",
        "title": "SEC 10-K CapEx: Grounded vs Hallucinated 2026 Forecast",
        "domain": "Enterprise Finance",
        "question": "How much capital expenditure did the company allocate to data center infrastructure, and what is the forecasted 2026 budget?",
        "contexts": [
            "Total capital expenditures for fiscal 2025 were $6.8 billion, of which $4.9 billion was directly invested in next-generation high-density data center buildouts.",
            "Our liquidity position remains strong with cash, equivalents, and short-term marketable securities totaling $18.4 billion as of December 31."
        ],
        "ground_truth": "Capital expenditure allocated to data centers was $4.9 billion in fiscal 2025. Forecast for 2026 was not disclosed in the filing.",
        "candidate_a": {
            "name": "Model A (Ideal Grounded)",
            "answer": "The company allocated $4.9 billion to data center infrastructure buildouts in fiscal 2025. Regarding the 2026 capital expenditure budget, the provided filing does not disclose a forecasted figure."
        },
        "candidate_b": {
            "name": "Model B (Hallucinating / Flawed)",
            "answer": "The company allocated $4.9 billion to data center infrastructure in fiscal 2025. Furthermore, management officially forecasted an aggressive $7.5 billion CapEx expansion budget for fiscal 2026 to support sovereign cloud builds."
        }
    },
    "clinical_dosage_contrastive": {
        "id": "clinical_dosage_contrastive",
        "title": "Clinical Pharmacology: Verified Dosage vs Dangerous Extrapolation",
        "domain": "Medical Compliance",
        "question": "What is the recommended initial dose of Cardiovit for stage 2 hypertension patients with mild renal impairment?",
        "contexts": [
            "For patients diagnosed with Stage 2 Hypertension, the recommended initial oral dosage of Cardiovit is 25 mg once daily taken in the morning.",
            "In patients exhibiting mild to moderate renal insufficiency (eGFR between 45 and 59 mL/min), no dosage reduction is required; however, close bi-weekly serum potassium monitoring is strictly indicated."
        ],
        "ground_truth": "Start at 25 mg once daily orally. Dosage reduction is not needed for mild renal impairment, but regular bi-weekly monitoring of serum potassium is mandatory.",
        "candidate_a": {
            "name": "Model A (Clinically Grounded)",
            "answer": "The initial dose of Cardiovit is 25 mg once daily taken in the morning. Patients with mild renal impairment do not require any dosage reduction, but serum potassium levels must be monitored bi-weekly."
        },
        "candidate_b": {
            "name": "Model B (Lethal Extrapolation / Flawed)",
            "answer": "For stage 2 hypertension with renal impairment, start at a reduced dosage of 10 mg twice daily. Serum potassium monitoring is optional if patients exhibit normal creatinine clearance."
        }
    },
    "cloud_mtls_contrastive": {
        "id": "cloud_mtls_contrastive",
        "title": "Kubernetes Service Mesh: Zero-Trust Strict mTLS vs Insecure Drift",
        "domain": "DevOps Security",
        "question": "How do you enforce strict mutual TLS (mTLS) across all service mesh namespaces?",
        "contexts": [
            "To enforce strict mutual TLS throughout the mesh, define a PeerAuthentication custom resource in the root istio-system namespace with mode: STRICT.",
            "Namespace-level PeerAuthentication policies will inherit from root unless explicitly overridden by a more granular local policy.",
            "Sidecar proxy injection must be enabled on target namespaces using the label istio-injection=enabled."
        ],
        "ground_truth": "Apply a root PeerAuthentication resource in istio-system with spec.mtls.mode set to STRICT to enforce mutual TLS mesh-wide.",
        "candidate_a": {
            "name": "Model A (Compliant Security Policy)",
            "answer": "You enforce strict mTLS globally across the mesh by applying a PeerAuthentication resource in the root istio-system namespace with mode configured to STRICT. Namespaces inherit this policy automatically unless locally overridden."
        },
        "candidate_b": {
            "name": "Model B (Insecure Configuration Drift)",
            "answer": "To enforce mTLS, configure PeerAuthentication with mode PERMISSIVE in the default namespace. Sidecar proxies are optional and plain TCP traffic will automatically be encrypted."
        }
    }
}
