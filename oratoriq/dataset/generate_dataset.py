"""
Script to generate the curated 52-pair contrastive speech dataset for OratorIQ.
Covers 5 scenarios:
1. Public Speaking (11 pairs)
2. Interview Answers (11 pairs)
3. Persuasive Pitches (10 pairs)
4. Presentation Delivery (10 pairs)
5. Academic Explanations (10 pairs)
Total: 52 contrastive pairs = 104 genuine speech exemplars with dimension-specific ratings.
"""

import json
import os

PAIRS_DATA = [
    # -------------------------------------------------------------
    # SCENARIO 1: PUBLIC SPEAKING
    # -------------------------------------------------------------
    {
        "pair_id": "PAIR-PUB-01",
        "scenario": "public_speaking",
        "intended_audience": "Tech conference attendees (engineers and founders)",
        "communication_goal": "Inspire developers to build ethically responsible AI systems",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates the contrast between an immediate captivating hook with a moral imperative versus a hesitant, throat-clearing opening.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-01-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "In 2018, a single line of automated pricing code bankrupted three independent clinics in rural Ohio overnight. Not through malice, but through unexamined optimization. When we write algorithms that touch human lives, efficiency cannot be our sole metric. Today, I want to share three architectural guardrails that ensure our machine learning models protect the vulnerable before they optimize the bottom line.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "High-impact narrative hook, clear thesis, crisp transition to three guardrails. No filler words, laser-focused relevance."
        },
        "flawed": {
            "sample_id": "PUB-01-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "excessive_filler_words", "weak_transitions"],
            "severity": "moderate",
            "transcript": "Um, hello everyone. Can everyone hear me at the back? Uh, sorry, the slides took a second to load. So, yeah, I'm here to talk about, like, AI ethics. Um, it's pretty important nowadays because, you know, algorithms are everywhere and stuff. Back in 2018 some clinics had issues with pricing software. And so we should really think about guardrails, basically.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Weak technical opening with microphone checking and apology. High filler density (um, uh, like, you know, basically = 7.1%). Lacks emotional resonance or concrete architectural framing."
        }
    },
    {
        "pair_id": "PAIR-PUB-02",
        "scenario": "public_speaking",
        "intended_audience": "University commencement graduating class and families",
        "communication_goal": "Motivate graduates to embrace constructive failure as a catalyst for innovation",
        "primary_flaw": "weak_or_missing_conclusion",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts a triumphant, memorable call to action against an abrupt, trailing ending that dissipates momentum.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-02-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "As you walk through those historic gates today, remember: the world does not need you to be infallible. It needs you to be resilient. When your first venture stumbles, when your first manuscript is rejected, treat the scar as data. Step into the arena, dare to build what seems impossible, and make your resilience your signature. Class of 2026, go forth and build.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Rhetorically powerful conclusion, evocative metaphors ('treat the scar as data'), definitive and uplifting cadence."
        },
        "flawed": {
            "sample_id": "PUB-02-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_or_missing_conclusion", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "So, walking out of here today, you will face rejections and stuff, and failure happens to everybody. It happened to me, it happened to my friends. Failure is just, yeah, failure is a thing. So don't feel too bad when you fail because failing is part of life, and, um, yeah, I guess that's basically all I wanted to say. Thank you.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Anticlimactic finish ('I guess that's basically all I wanted to say'). Severe repetition of the word 'fail/failure' 6 times in 50 words without progression."
        }
    },
    {
        "pair_id": "PAIR-PUB-03",
        "scenario": "public_speaking",
        "intended_audience": "City council and local community residents",
        "communication_goal": "Advocate for municipal investment in protected bicycle infrastructure",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "severe",
        "contrastive_rationale": "Exemplifies how empirical local casualty statistics and economic trade-offs outperform emotional, unsubstantiated assertions.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-03-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Over the past twenty-four months, Main Street witnessed forty-seven preventable vehicular collisions involving pedestrians and cyclists. Department of Transportation records confirm that protected bike corridors reduce severe injuries by fifty-six percent while boosting retail foot traffic by twelve percent. Investing two hundred thousand dollars in bollards and green lanes is not merely a recreational amenity; it is a fiscally sound life-saving measure.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 4,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Dense with verified municipal evidence, direct causal argument connecting safety to merchant foot traffic."
        },
        "flawed": {
            "sample_id": "PUB-03-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "poor_logical_structure"],
            "severity": "severe",
            "transcript": "Cars are destroying our city and everybody knows that drivers don't care about anyone else. If you don't build bike lanes immediately, dozens of people are guaranteed to die every single month. Bike lanes make cities a million times better and local shops will literally double their sales overnight because cycling is the future. Everyone who drives should just be taxed out of downtown.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 3,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Wildly hyperbolic claims ('millions of times better', 'double sales overnight', 'guaranteed to die every month'). Polarizing tone alienates council members."
        }
    },
    {
        "pair_id": "PAIR-PUB-04",
        "scenario": "public_speaking",
        "intended_audience": "Environmental summit delegates",
        "communication_goal": "Propose scalable modular nuclear energy as a baseload green energy solution",
        "primary_flaw": "poorly_placed_pauses",
        "flaw_severity": "minor",
        "contrastive_rationale": "Highlights the difference between deliberate rhetorical pauses that highlight key statistics versus awkward mid-phrase stops.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-04-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Wind and solar are indispensable. But when the grid demands continuous baseload power in mid-winter, we face a mathematical reality. Small modular reactors occupy less than one percent of the land footprint of solar arrays, producing zero direct carbon emissions twenty-four hours a day. We cannot solve a generational crisis by eliminating our most power-dense tool.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Balanced perspective, strong antithesis ('indispensable... but mathematical reality'), concise and structured."
        },
        "flawed": {
            "sample_id": "PUB-04-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poorly_placed_pauses", "excessively_slow_pacing"],
            "severity": "minor",
            "transcript": "Wind and solar... are indispensable. But when... the grid demands... continuous baseload... power in mid-winter... we face... a mathematical reality. Small modular reactors occupy... less than one percent... of the land footprint... producing zero direct carbon emissions.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 4,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Content is strong, but delivery is fragmented by unnatural pauses splitting verbs and direct objects, dropping speaking rate to 88 WPM."
        }
    },
    {
        "pair_id": "PAIR-PUB-05",
        "scenario": "public_speaking",
        "intended_audience": "Healthcare gala donors and medical researchers",
        "communication_goal": "Inspire philanthropic funding for pediatric rare disease therapeutics",
        "primary_flaw": "monotonous_vocal_delivery",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Illustrates how emotional range and pitch contrast are essential to connect with donors compared to dry recital.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-05-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Behind every scientific diagnostic code is a family sitting in a pediatric waiting room, praying for a breakthrough that commercial pharmaceutical pipelines deemed too small to pursue. Tonight, your generosity changes that equation. With five million dollars in endowed research, we fund three clinical trials this year, turning clinical dead ends into active cures.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 4,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Deeply empathetic opening connected to tangible dollar-to-impact metrics. Eloquent and emotionally calibrated."
        },
        "flawed": {
            "sample_id": "PUB-05-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["monotonous_vocal_delivery", "unclear_articulation"],
            "severity": "moderate",
            "transcript": "There are numerous rare diseases that lack adequate market incentives in the pharmaceutical sector. Our institution seeks five million dollars to offset operational expenditures across three translational laboratory initiatives. Donating capital facilitates scientific throughput and addresses the aforementioned clinical deficits.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Clinical and bureaucratic vocabulary ('market incentives', 'translational laboratory initiatives', 'aforementioned deficits') delivered with zero tonal warmth."
        }
    },
    {
        "pair_id": "PAIR-PUB-06",
        "scenario": "public_speaking",
        "intended_audience": "Annual corporate all-hands meeting",
        "communication_goal": "Address an unexpected quarterly revenue miss with candor and strategic clarity",
        "primary_flaw": "poor_logical_structure",
        "flaw_severity": "severe",
        "contrastive_rationale": "Shows the difference between transparent root-cause accountability versus evasive corporate jargon and finger-pointing.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-06-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "I will not sugarcoat our third-quarter numbers: we fell eight percent short of our top-line target. Two key enterprise renewals slipped into Q4, and customer onboarding took three weeks longer than planned. That responsibility rests with executive leadership. We have already redesigned the deployment onboarding pipeline, and our forward pipeline for Q4 is thirty percent higher than last year. We own the miss, we fixed the friction, and now we execute.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Direct accountability, specific quantifiable diagnosis, and forward-looking action plan. Inspires organizational trust."
        },
        "flawed": {
            "sample_id": "PUB-06-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poor_logical_structure", "weak_transitions", "unsupported_claims"],
            "severity": "severe",
            "transcript": "Well, things happened this quarter that were totally outside our control. The macroeconomic climate is challenging, and sales teams didn't hit targets. But also engineering delayed some features. Actually, revenue is just an accounting artifact if you look at our underlying brand value. We're going to crush next quarter because our culture is unstoppable, regardless of what the balance sheet says.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Evasive scapegoating, dismisses financial metrics as an 'accounting artifact', lacks a coherent causal breakdown."
        }
    },
    {
        "pair_id": "PAIR-PUB-07",
        "scenario": "public_speaking",
        "intended_audience": "High school science fair awards assembly",
        "communication_goal": "Encourage young student researchers to pursue scientific curiosity over perfection",
        "primary_flaw": "excessive_filler_words",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts smooth, punchy encouragement against distracted, filler-laden speech that loses the students' attention.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-07-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Every medal awarded today is thrilling, but the experiments that blew a fuse, contaminated a petri dish, or disproved your beloved hypothesis are where real discoveries take root. Alexander Fleming did not set out to find penicillin; he paid attention to a mistake. Keep questioning the anomalies in your data. The world needs your curiosity.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Accessible historical anecdote, concise framing, strong motivating closing."
        },
        "flawed": {
            "sample_id": "PUB-07-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessive_filler_words", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "Um, you guys did, like, really good experiments today. But, um, you know, when your experiment, like, doesn't work out, that's, you know, actually pretty cool too. Like Fleming, he, um, had mold in his dish, and like, you know, he didn't throw it away. So, like, mistakes are good, you know? Keep doing mistakes, basically.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Extreme filler frequency (12 filler words in 68 words = 17.6%). Phrasing 'keep doing mistakes' is syntactically awkward."
        }
    },
    {
        "pair_id": "PAIR-PUB-08",
        "scenario": "public_speaking",
        "intended_audience": "Rotary club civic leaders lunch",
        "communication_goal": "Present the civic benefits of establishing a downtown literacy center",
        "primary_flaw": "excessively_fast_pacing",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates the risk of a rushed delivery where important statistics blur together without breathing room.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-08-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "One in four adults in our county struggles with functional literacy. That means they cannot read a prescription warning or comprehend a mortgage agreement. By converting the vacant library on 4th Street into an evening adult learning hub, we can teach six hundred parents to read this year. When a parent learns to read, their child's graduation rate jumps forty percent.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Clear statistical cadence, vivid relatable examples (prescription labels), high civic relevance."
        },
        "flawed": {
            "sample_id": "PUB-08-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessively_fast_pacing", "poorly_placed_pauses"],
            "severity": "moderate",
            "transcript": "Oneinfouradultsinourcountystruggleswithliteracywhichmeanstheycan'treadprescriptionsorcontractssoifweconvertthelibraryon4thstreetwecanhelp600peopleandgraduatefortypercentmorekidsbecauseparentallearningcorrelateswithchildhoodoutcomesrapidly.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Spoken at over 210 WPM without vocal cadence, making cognitive absorption almost impossible for the audience."
        }
    },
    {
        "pair_id": "PAIR-PUB-09",
        "scenario": "public_speaking",
        "intended_audience": "University debate society",
        "communication_goal": "Argue against algorithmic sentencing in criminal justice courts",
        "primary_flaw": "weak_transitions",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows how seamless logical signposts guide intellectual debate versus disjointed topic leaping.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-09-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Proponents of risk-assessment algorithms promise mathematical neutrality. Yet their models are trained on historic arrest data that reflects half a century of racially biased policing. First, an algorithm cannot distinguish between high criminality and high surveillance. Second, proprietary neural weights deny defendants their constitutional right to confront the logic of their accuser. We cannot outsource human liberty to a black box.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Formidable rhetorical rigor. Uses 'First... Second...' signposts to contrast surveillance bias against constitutional transparency."
        },
        "flawed": {
            "sample_id": "PUB-09-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_transitions", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Algorithms in court are bad. Also, policing in the past had problems with race. Software companies charge a lot of money for their software. Another thing is the Sixth Amendment which gives you rights in court. And artificial intelligence has hallucinations, like ChatGPT does. So judges shouldn't use computers to sentence people.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Haphazard collection of points connected by 'Also', 'Another thing is', 'And'. Conflates risk scoring algorithms with LLM hallucinations."
        }
    },
    {
        "pair_id": "PAIR-PUB-10",
        "scenario": "public_speaking",
        "intended_audience": "Regional chamber of commerce dinner",
        "communication_goal": "Present the regional economic multiplier of clean energy manufacturing",
        "primary_flaw": "unclear_articulation",
        "flaw_severity": "minor",
        "contrastive_rationale": "Contrasts sharp, crisp diction against slurred, indistinct syllable pronunciation.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-10-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "When a solar inverter manufacturing facility opens in our industrial park, every direct engineering job creates three secondary service roles in logistics, catering, and maintenance. That is a 3.4x economic multiplier. Our county has the skilled machinists and the grid connectivity to lead this transition.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 4,
                "fluency_and_pacing": 4,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Clear, precise diction. Explains economic multiplier formula intuitively."
        },
        "flawed": {
            "sample_id": "PUB-10-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unclear_articulation", "monotonous_vocal_delivery"],
            "severity": "minor",
            "transcript": "Whna sol'r invrtr f'cility opens in're park, ev'ry direct job kinna makes three oth'r jobs in logist'cs 'n stuff. 'S a 3.4 multipli'r thing. We got'cha skilled machin'sts round here.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Slurred consonants, dropped vowels, and imprecise articulation detract from professional credibility."
        }
    },
    {
        "pair_id": "PAIR-PUB-11",
        "scenario": "public_speaking",
        "intended_audience": "TEDx audience interested in psychology and behavioral economics",
        "communication_goal": "Explain how the 'paradox of choice' causes decision paralysis in digital consumer habits",
        "primary_flaw": "failure_to_answer_question",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts staying rigorously on topic versus drifting into unrelated personal complaints about smartphones.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PUB-11-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "When researchers offered grocery shoppers twenty-four varieties of artisanal jam, thirty percent stopped, but only three percent purchased. When they reduced the selection to six jars, purchase rates surged to thirty percent. Why? Because excessive choice shifts cognitive effort from appreciation to post-decision regret. In our digital world of infinite scrolling, curated constraint is the ultimate gift of focus.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Uses the classic Iyengar jam experiment seamlessly to deduce the psychological principle of choice overload."
        },
        "flawed": {
            "sample_id": "PUB-11-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["failure_to_answer_question", "poor_logical_structure"],
            "severity": "severe",
            "transcript": "So I was browsing Netflix yesterday and it took me two hours to pick a movie. And then my phone battery died, which is so annoying because Apple batteries degrade after two years. My friend bought an Android and says the camera is better, but honestly social media notifications are ruining our sleep anyway. So yeah, technology is pretty overwhelming.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 3,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Begins with choice paralysis (Netflix) but wanders off into battery life, Android cameras, and sleep deprivation without explaining the psychological mechanism."
        }
    },

    # -------------------------------------------------------------
    # SCENARIO 2: INTERVIEW ANSWERS
    # -------------------------------------------------------------
    {
        "pair_id": "PAIR-INT-01",
        "scenario": "interview_answers",
        "intended_audience": "Senior Engineering Hiring Manager",
        "communication_goal": "Answer: 'Tell me about a time you resolved a major production outage under pressure.'",
        "primary_flaw": "failure_to_answer_question",
        "flaw_severity": "severe",
        "contrastive_rationale": "Demonstrates the structured STAR framework (Situation, Task, Action, Result) versus rambling about irrelevant context without addressing the root cause or outcome.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-01-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "During Black Friday 2024, our primary checkout API experienced an 85% latency spike, risking $400,000 in hourly transactions. As incident commander, I first segregated traffic by enabling our fallback caching layer to keep critical browse paths alive. Then, analyzing distributed traces, I discovered an unindexed database query introduced in the morning deploy. I rolled back that specific migration, restoring sub-200ms p99 latency in eighteen minutes. Afterwards, I instituted mandatory query plan regression tests in CI, preventing any recurrence.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Textbook STAR method execution: quantifiable stakes ($400k/hr), specific diagnostic action (distributed traces, query rollback), and long-term systemic safeguard."
        },
        "flawed": {
            "sample_id": "INT-01-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["failure_to_answer_question", "poor_logical_structure", "excessive_filler_words"],
            "severity": "severe",
            "transcript": "Oh man, production outages are so stressful. Like, one time on Black Friday, everything was just completely blowing up and Slack was going crazy with hundreds of notifications. People were yelling in the Zoom bridge and our VP of Product was asking for updates every five seconds. I really hate when people panic during incidents, you know? But anyway, we all worked together as a team and eventually the servers came back up after a few hours.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Focuses entirely on emotional chaos and workplace drama. Never explains what broke, what actions they personally took, how it was diagnosed, or how long it took."
        }
    },
    {
        "pair_id": "PAIR-INT-02",
        "scenario": "interview_answers",
        "intended_audience": "VP of Product and Design Panel",
        "communication_goal": "Answer: 'How do you handle disagreement with a technical lead on product scope?'",
        "primary_flaw": "weak_transitions",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows collaborative empathy and data-driven prioritization versus passive-aggressive conflict avoidance.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-02-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "I view technical disagreement as an opportunity to discover hidden architectural constraints. When my lead engineer opposed shipping our real-time collaboration feature in Q2 due to WebSocket state complexity, I did not push back with hierarchy. Instead, we scheduled a whiteboard session to decouple the core milestone: we shipped asynchronous polling in Phase 1 to satisfy eighty percent of enterprise user needs on schedule, while provisioning dedicated engineering sprints to build the scalable WebSocket architecture for Phase 2.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Mature leadership response. Deconstructs the binary conflict into phased pragmatic milestones satisfying both business deadlines and engineering integrity."
        },
        "flawed": {
            "sample_id": "INT-02-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_transitions", "unsupported_claims"],
            "severity": "moderate",
            "transcript": "Whenever tech leads disagree with me, I usually just tell them that product owns the roadmap. But engineers are always trying to rewrite everything from scratch and gold-plate code. So I had this argument about WebSockets and I just told the VP that engineering was blocking the release, and then the VP told them they had to build it anyway. So we won that argument.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Adversarial mindset ('we won that argument'), relies on top-down escalation rather than cross-functional problem solving. Disastrous interview signal."
        }
    },
    {
        "pair_id": "PAIR-INT-03",
        "scenario": "interview_answers",
        "intended_audience": "Director of Finance and Corporate Strategy",
        "communication_goal": "Answer: 'Walk me through how you evaluate whether to acquire or build a new software capability.'",
        "primary_flaw": "unnecessary_repetition",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates an analytical build-vs-buy financial framework versus looping over the same generic sentence repeatedly.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-03-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "I evaluate build-versus-buy decisions across four disciplined vectors: core competitive differentiation, time-to-market advantage, total cost of ownership over three years, and integration maintenance risk. If the capability is our core IP—such as our proprietary risk pricing engine—we build to protect competitive moat. If it is commoditized infrastructure—like billing or authentication—we buy to compress time-to-market and avoid diverting engineering capital from our unique value proposition.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Crisp 4-pillar taxonomy with clear heuristic: build core IP differentiators, license commoditized plumbing."
        },
        "flawed": {
            "sample_id": "INT-03-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unnecessary_repetition", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Building versus buying is really about whether you want to build it or buy it. Because if you build it, you have to build it yourself, but if you buy it, someone else built it. So you have to look at whether building it takes longer than buying it, and whether buying it costs more than building it. It really depends on building versus buying tradeoffs.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Tautological looping: uses the words 'build' and 'buy' 12 times in 60 words without providing a single concrete decision framework or criterion."
        }
    },
    {
        "pair_id": "PAIR-INT-04",
        "scenario": "interview_answers",
        "intended_audience": "Behavioral Interview Panel (Chief People Officer)",
        "communication_goal": "Answer: 'What is your greatest professional weakness and how do you mitigate it?'",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts genuine self-awareness and active systems of behavioral mitigation against a clichéd humblebrag.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-04-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Early in my career, I had a tendency to default to doing tasks myself when junior team members struggled, confusing delegation with lack of support. This bottlenecked team velocity and slowed their technical growth. To correct this, I adopted a structured delegation framework: whenever assigning critical features, I now agree on clear definition-of-done criteria, schedule bi-weekly pairing check-ins, and step back during implementation. This has allowed two engineers I mentored to step up into tech lead roles this year.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 4,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Authentic weakness (over-involvement/bottlenecking), specific behavioral mitigation mechanism, and proven positive outcome (mentees promoted)."
        },
        "flawed": {
            "sample_id": "INT-04-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "failure_to_answer_question"],
            "severity": "moderate",
            "transcript": "My biggest weakness is honestly that I'm just too much of a perfectionist. I care way too much about high quality and I work so hard that I end up staying until midnight making everything flawless. Sometimes I just care too much about the company's success, which I guess can make other people feel intimidated by my dedication.",
            "rubric_labels": {
                "content_and_relevance": 1,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 3,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Classic transparent humblebrag ('too much of a perfectionist', 'care too much'). Shows zero genuine vulnerability or self-awareness."
        }
    },
    {
        "pair_id": "PAIR-INT-05",
        "scenario": "interview_answers",
        "intended_audience": "Executive Leadership Recruiter",
        "communication_goal": "Answer: 'Why do you want to leave your current high-performing position to join our organization?'",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates forward-looking pull factors aligned with company mission versus venting grievances about past management.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-05-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "I am deeply proud of the platform we scaled from zero to four million monthly users over the past three years. However, our market focus was primarily domestic consumer e-commerce. Your organization is pioneering decentralized cross-border enterprise settlement, solving complex latency and compliance problems at global scale. My background in distributed ledger consensus directly aligns with your upcoming expansion into European markets.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Respectful of prior employer, articulates specific pull factor (global enterprise settlement) and maps personal domain expertise directly to target company."
        },
        "flawed": {
            "sample_id": "INT-05-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Honestly, my current manager is impossible to work with and management keeps canceling all our projects. The culture has gotten super toxic and they didn't give me the raise I was promised six months ago. So I'm pretty much ready to leave as soon as possible, and I saw your company was hiring and pays pretty well.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Critical red flag: disparages current employer, complains about compensation, indicates they are running away from friction rather than toward a deliberate career milestone."
        }
    },
    {
        "pair_id": "PAIR-INT-06",
        "scenario": "interview_answers",
        "intended_audience": "Chief Information Security Officer (CISO)",
        "communication_goal": "Answer: 'How do you foster a security-first culture among product engineering teams?'",
        "primary_flaw": "excessive_filler_words",
        "flaw_severity": "minor",
        "contrastive_rationale": "Contrasts automated security guardrails and empathetic developer tooling versus punitive policing.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-06-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Security cannot be a punitive tollgate at the end of the release cycle; it must be an integrated developer experience. I implement this through three mechanisms: first, shift-left static analysis and container scanning embedded directly into GitHub pull request checks with clear remediation advice; second, a Security Champions program embedding designated security liaisons within sprint squads; and third, blame-free postmortems that celebrate finding vulnerabilities before production.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 4,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "High strategic clarity. Combines automated CI tooling with cultural ownership (Security Champions, blame-free postmortems)."
        },
        "flawed": {
            "sample_id": "INT-06-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessive_filler_words", "weak_transitions"],
            "severity": "minor",
            "transcript": "Um, well, like, security is obviously super important. So, uh, basically what I do is, like, tell developers they have to follow security rules. And, uh, if they don't, we, you know, block their pull requests until they fix it. And, um, like, having meetings with them to remind them about passwords and stuff helps, you know?",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "High filler frequency, punitive approach ('block their pull requests until they fix it'), superficial tips ('remind them about passwords')."
        }
    },
    {
        "pair_id": "PAIR-INT-07",
        "scenario": "interview_answers",
        "intended_audience": "Data Science Panel (Lead ML Scientist)",
        "communication_goal": "Answer: 'Explain how you detect and mitigate data drift in production machine learning models.'",
        "primary_flaw": "unclear_articulation",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts rigorous statistical drift testing (KS-test, PSI) and automated shadow retraining versus hand-waving.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-07-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "I decouple drift monitoring into covariate shift and concept drift. For covariate shift, our pipeline runs daily Kolmogorov-Smirnov tests on continuous feature distributions and Population Stability Index on categorical features, alerting our team if PSI exceeds 0.2. For concept drift, we track rolling F1 and calibration error against delayed ground truth labels. When drift breaches statistical thresholds, it triggers automated retraining on recent windows evaluated in shadow mode before promotion.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Precise mathematical grounding (KS test, PSI > 0.2, calibration error) connected to an automated MLOps CI/CD deployment pipeline."
        },
        "flawed": {
            "sample_id": "INT-07-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unclear_articulation", "unsupported_claims"],
            "severity": "moderate",
            "transcript": "When data drifts, you kinda just look at the model outputs and see if they look weird. If accuracy drops, you retrain on new data. We had a script that ran sometimes, and if things broke we would just retrain the weights overnight and redeploy it to production.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Vague informal terminology ('look if they look weird', 'script that ran sometimes'). Zero awareness of statistical distribution tests."
        }
    },
    {
        "pair_id": "PAIR-INT-08",
        "scenario": "interview_answers",
        "intended_audience": "Operations Vice President",
        "communication_goal": "Answer: 'Describe a project where you had to balance short-term cost cuts with long-term operational resilience.'",
        "primary_flaw": "poor_logical_structure",
        "flaw_severity": "severe",
        "contrastive_rationale": "Shows nuanced risk trade-off modeling versus reckless slash-and-burn cost cutting that crippled operations.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-08-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "When our cloud infrastructure spend rose thirty percent above budget, executive mandate requested a flat twenty percent cost reduction within sixty days. Rather than terminating high-availability multi-region redundancy, I audited our compute utilization. We discovered forty terabytes of unindexed cold storage and over-provisioned staging clusters. By migrating cold tiers to Glacier and implementing auto-scaling on development clusters, we achieved a twenty-two percent spend reduction while keeping ninety-nine point nine-nine percent production uptime intact.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Protects core mission resilience (multi-region HA) while surgically eliminating wasteful staging and cold storage expenditure."
        },
        "flawed": {
            "sample_id": "INT-08-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poor_logical_structure", "weak_transitions"],
            "severity": "severe",
            "transcript": "Management told us we spent too much money. So I just canceled our backup servers and turned off all logging to save money immediately. It cut costs by thirty percent and everyone was super happy. But then two months later we had a disaster recovery test that failed completely because there were no backups. But at least we hit our quarterly budget target.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Short-sighted cost reduction destroying resilience (turning off backups and logging). Discloses catastrophic failure as if it were acceptable."
        }
    },
    {
        "pair_id": "PAIR-INT-09",
        "scenario": "interview_answers",
        "intended_audience": "Chief Marketing Officer",
        "communication_goal": "Answer: 'How do you design a customer retention strategy when churn begins rising in a mature product line?'",
        "primary_flaw": "weak_or_missing_conclusion",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows cohort analysis and targeted lifecycle interventions versus throwing generic discounts at churned users.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-09-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "When net churn increased from two percent to four point five percent in Q1, we avoided the trap of sending blanket promotional discount codes. Instead, we performed cohort survival analysis and isolated ninety percent of the churn to users who failed to complete their second workspace integration within fourteen days of signup. We redesigned the in-app onboarding wizard with step-by-step API connect guides. Within ninety days, secondary activation rose sixty-five percent, stabilizing monthly net churn back down to one point eight percent.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Data-informed cohort segmentation identifying the exact activation bottleneck, leading to a permanent structural fix."
        },
        "flawed": {
            "sample_id": "INT-09-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_or_missing_conclusion", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "When customers leave, you have to retain them because retention is what keeps the business going. We saw churn going up, so we just emailed everybody twenty percent off coupons. A lot of people opened the email, but then churn was still kinda high anyway. So retention is really hard, and yeah.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Circular reasoning ('you have to retain them because retention keeps business going'). Lacks root-cause diagnosis; ends abruptly."
        }
    },
    {
        "pair_id": "PAIR-INT-10",
        "scenario": "interview_answers",
        "intended_audience": "Executive Cross-functional Hiring Committee",
        "communication_goal": "Answer: 'Give an example of how you communicated complex technical risk to non-technical board members.'",
        "primary_flaw": "monotonous_vocal_delivery",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates translating arcane technical debt into financial risk and business velocity metrics.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-10-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Our board did not need to understand monolithic kernel memory fragmentation; they needed to understand why checkout feature delivery had slowed by fifty percent. I presented a financial analogy: I explained that our technical debt was like carrying a high-interest credit card balance. While minimum payments allowed us to ship small patches, forty cents of every engineering dollar was going toward paying down interest. The board unanimously authorized a two-sprint refactoring initiative that increased our subsequent quarterly feature velocity by thirty-five percent.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Brilliant executive translation: uses the credit-card interest analogy to reframe technical debt into measurable capital efficiency."
        },
        "flawed": {
            "sample_id": "INT-10-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["monotonous_vocal_delivery", "unclear_articulation"],
            "severity": "moderate",
            "transcript": "I told the board that our kubernetes ingress controllers were having race conditions with postgres transaction isolation levels under read-committed concurrency, and that we needed to refactor our ORM layer to support asynchronous connection pooling otherwise our p99 latency would breach SLA thresholds.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Completely fails to adapt communication to the target audience. Drowns non-technical board members in deep engineering jargon."
        }
    },
    {
        "pair_id": "PAIR-INT-11",
        "scenario": "interview_answers",
        "intended_audience": "Principal Architect Hiring Committee",
        "communication_goal": "Answer: 'How do you design for eventual consistency in high-volume distributed systems?'",
        "primary_flaw": "excessively_slow_pacing",
        "flaw_severity": "minor",
        "contrastive_rationale": "Contrasts confident architectural trade-off analysis against halting, hesitant delivery.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "INT-11-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Eventual consistency requires embracing the CAP theorem trade-off: trading instantaneous linearizability for high availability and low write latency. In our financial ledger, we separate immutable transaction event logs from materialized read projections using the transactional outbox pattern with Kafka. Writes acknowledge immediately once committed to the write-ahead log, while downstream read projections reconcile via idempotent consumer workers within fifty milliseconds.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Architecturally authoritative: specifies transactional outbox pattern, write-ahead logs, and idempotent consumers with clear latency expectations."
        },
        "flawed": {
            "sample_id": "INT-11-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessively_slow_pacing", "poorly_placed_pauses"],
            "severity": "minor",
            "transcript": "Eventual consistency... is when... data... becomes consistent... eventually. You use... databases like Cassandra... or Kafka... and then... you write events... and the consumer... reads them... whenever it has time... so the user... sees the update... later on.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Extremely slow (74 WPM), heavy awkward pauses between basic words, oversimplifies high-volume architecture to tautologies."
        }
    },

    # -------------------------------------------------------------
    # SCENARIO 3: PERSUASIVE PITCHES
    # -------------------------------------------------------------
    {
        "pair_id": "PAIR-PIT-01",
        "scenario": "persuasive_pitches",
        "intended_audience": "Venture Capital Seed Investors",
        "communication_goal": "Pitch an AI-driven cold-chain logistics monitoring platform",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows immediate market pain quantification versus timid biographical background before reaching the pitch.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-01-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Thirty-five billion dollars of temperature-sensitive pharmaceuticals spoil in transit every single year because current cargo loggers only alert companies after the medicine is ruined. Our platform, CryoPulse, deploys predictive IoT sensor pods that forecast thermal breach forty-five minutes before it occurs. In our twelve-week pilot with Novartis, we prevented eight cargo losses, saving 1.2 million dollars. We are raising two million dollars to scale deployment across five transcontinental freight corridors.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Exemplary venture pitch structure: $35B TAM pain point, proprietary predictive solution, pilot validation with enterprise logo (Novartis), clear $2M ask."
        },
        "flawed": {
            "sample_id": "PIT-01-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "excessive_filler_words", "weak_or_missing_conclusion"],
            "severity": "moderate",
            "transcript": "Hi everyone. Um, my name is Alex and I've always been really interested in logistics ever since I was in college. So, uh, vaccines need to stay cold, right? And sometimes trucks get hot and, like, things spoil. So we built this little sensor device that, you know, tracks temperature. It's really cool technology using machine learning and AI. So we'd love if you guys could invest some money with us today.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Meandering personal opening, zero market sizing, vague technology description ('little sensor device'), and an unquantified investment ask ('some money')."
        }
    },
    {
        "pair_id": "PAIR-PIT-02",
        "scenario": "persuasive_pitches",
        "intended_audience": "Enterprise Chief Information Officers (B2B SaaS Sales)",
        "communication_goal": "Sell an automated cloud compliance and SOC2 auditing platform",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts verified engineering hours saved and audit auditability against unsubstantiated promises of 'instant 100% compliance'.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-02-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Your engineering leads spend four hundred hours every quarter manually taking screenshots of AWS IAM policies for SOC2 auditors instead of shipping customer features. Our platform automates continuous evidence collection across ninety-two cloud services in real time. For mid-market SaaS companies, we compress audit preparation from twelve weeks to four days, reducing third-party auditor fees by forty percent. Let us run an automated diagnostic on your staging cluster this Thursday.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Speaks directly to the buyer's pain (400 engineering hours lost to screenshot gathering), provides proven metrics, and ends with a concrete, frictionless call to action."
        },
        "flawed": {
            "sample_id": "PIT-02-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "unnecessary_repetition"],
            "severity": "severe",
            "transcript": "Our software is the most revolutionary compliance tool in the history of cybersecurity. With our platform, you will literally get 100% SOC2 compliance in five minutes with zero human effort. Our AI does everything automatically so you never have to think about security ever again. Every other tool on the market is garbage compared to ours.",
            "rubric_labels": {
                "content_and_relevance": 1,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 3,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Outrageous, unsupportable claims ('100% compliance in five minutes with zero effort', 'never think about security again'). Destroys credibility with enterprise buyers."
        }
    },
    {
        "pair_id": "PAIR-PIT-03",
        "scenario": "persuasive_pitches",
        "intended_audience": "University sustainability grant review board",
        "communication_goal": "Secure $50,000 grant for campus food waste anaerobic digestion",
        "primary_flaw": "poor_logical_structure",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows tight linkage between grant budget, mass balance engineering calculations, and campus ROI.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-03-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Our dining halls generate four tons of organic food waste every week, costing the university twenty-eight thousand dollars annually in landfill tipping fees. With a fifty-thousand-dollar micro-grant, our engineering team will install a closed-loop anaerobic digester behind South Hall. This system converts seventy percent of that waste into organic fertilizer for campus grounds and biogas powering dining hall water heaters, recouping the entire investment within twenty-two months.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Flawless grant pitch: baseline waste volume, existing cost penalty, technical conversion mechanism, and 22-month payback period."
        },
        "flawed": {
            "sample_id": "PIT-03-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poor_logical_structure", "weak_transitions"],
            "severity": "moderate",
            "transcript": "Food waste is a major problem globally and climate change is really bad. We want fifty thousand dollars to build a digester. Also, the campus grounds could use fertilizer. Students care a lot about green initiatives, and landfill emissions are harmful to the ozone layer. So please fund our grant project because composting is sustainable.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Superficial platitudes ('climate change is bad', 'composting is sustainable'). Fails to provide any operational specs, tonnage numbers, or financial payback timeline."
        }
    },
    {
        "pair_id": "PAIR-PIT-04",
        "scenario": "persuasive_pitches",
        "intended_audience": "Angel Investor Group",
        "communication_goal": "Pitch a digital physical therapy and computer vision rehabilitation app",
        "primary_flaw": "excessively_fast_pacing",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Illustrates how rushing through unit economics and clinical trials prevents investors from absorbing key traction signals.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-04-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Seventy percent of post-surgical physical therapy patients abandon their home exercise routines, leading to a twenty-two percent hospital readmission rate. Our app turns any smartphone camera into a real-time clinical motion-tracker, guiding joint angles with millimeter precision. In our IRB-approved trial with Baptist Health, patient adherence doubled to eighty-four percent. We have secured two commercial payer pilots, generating sixty thousand dollars in annual recurring revenue.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "High-conviction presentation with clinical validation (Baptist Health trial), adherence metrics, and early enterprise SaaS traction."
        },
        "flawed": {
            "sample_id": "PIT-04-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessively_fast_pacing", "poorly_placed_pauses"],
            "severity": "moderate",
            "transcript": "Seventypercentofpatientsstopphysicaltherapyandgetreadmittedsoourcomputer-visionapptracksmovementswithsmartphoneswehavetrialresultsshowingeighty-fourpercentadherenceandtwocommercialcontractsfor60kARRandwe'reraisingseedfundingtoday.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Rushed at over 220 WPM without vocal cadence. Critical clinical data points blur together, undermining investor confidence."
        }
    },
    {
        "pair_id": "PAIR-PIT-05",
        "scenario": "persuasive_pitches",
        "intended_audience": "Corporate Innovation Committee",
        "communication_goal": "Pitch internal adoption of a 4-day work week pilot program",
        "primary_flaw": "failure_to_answer_question",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts rigorous empirical productivity metrics and client SLA guarantees against entitlement arguments.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-05-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "We propose a six-month pilot of a 32-hour work week for our customer support department. Similar pilots across ninety-one companies demonstrated a thirty-five percent drop in employee turnover while customer satisfaction scores rose six points. To protect client SLAs, we will stagger team shifts across Monday-through-Thursday and Tuesday-through-Friday cohorts, ensuring continuous five-day coverage without overtime expense. If support resolution times increase by more than five percent, the pilot terminates automatically.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Proactively addresses corporate risk: staggered coverage protects client SLAs, accompanied by an explicit quantitative circuit-breaker condition."
        },
        "flawed": {
            "sample_id": "PIT-05-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["failure_to_answer_question", "unsupported_claims"],
            "severity": "severe",
            "transcript": "Working five days a week is an outdated capitalist invention that makes everyone burnt out. We deserve to only work four days because work-life balance is a human right. If management cared about our mental health, they would give us Fridays off immediately with full pay, and our productivity will obviously double because we'll be happier.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Entitled, aggressive framing that ignores business realities, customer SLAs, and coverage logistics."
        }
    },
    {
        "pair_id": "PAIR-PIT-06",
        "scenario": "persuasive_pitches",
        "intended_audience": "Commercial Real Estate Developers",
        "communication_goal": "Pitch retrofitting commercial office buildings with smart IoT HVAC optimization",
        "primary_flaw": "monotonous_vocal_delivery",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts dynamic value-proposition delivery against dry technical component recitals.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-06-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Commercial real estate owners are heating and cooling empty conference rooms, bleeding thirty cents of every utility dollar. Our wireless mesh thermostat network learns floor occupancy patterns dynamically, reducing aggregate kilowatt-hour consumption by twenty-four percent. In a typical two-hundred-thousand square foot office tower, that translates to ninety thousand dollars in annual net operating income expansion—boosting your asset valuation by 1.8 million dollars at a five-percent cap rate.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Understands real estate financial levers: connects kilowatt savings directly to Net Operating Income (NOI) and cap-rate asset valuation expansion."
        },
        "flawed": {
            "sample_id": "PIT-06-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["monotonous_vocal_delivery", "unclear_articulation"],
            "severity": "moderate",
            "transcript": "Our system includes Zigbee sensors, microcontrollers, and a cloud telemetry gateway. It communicates via MQTT protocols to regulate damper actuators in variable air volume terminals. Installing this hardware optimizes thermodynamic transfer functions across the HVAC distribution envelope.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Flat robotic list of hardware protocols (Zigbee, MQTT, VAV terminals) with zero financial justification for building owners."
        }
    },
    {
        "pair_id": "PAIR-PIT-07",
        "scenario": "persuasive_pitches",
        "intended_audience": "Non-profit Board of Trustees",
        "communication_goal": "Pitch expansion of mobile medical vans into underserved agricultural communities",
        "primary_flaw": "weak_or_missing_conclusion",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows inspiring donor closing with concrete milestone commitments versus an unfocused trailing finish.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-07-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Over twelve thousand migrant agricultural workers in our valley live more than forty miles from the nearest federally qualified health clinic. Preventable chronic conditions like diabetic retinopathy and hypertension go unmonitored until they require emergency triage. With two customized mobile health vans, our bilingual nurse practitioners can deliver primary care directly to worker dormitories on weekends. Tonight, your authorization of this pilot brings preventive medicine to three thousand families who harvest the food on our tables.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Compassionate and grounded: highlights health disparities, outlines operational delivery model, and connects donors to immediate community impact."
        },
        "flawed": {
            "sample_id": "PIT-07-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_or_missing_conclusion", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "Farm workers have health problems and healthcare is far away. Vans are good because vans can drive around. If you drive vans to farms, people can get medicine from the vans. We need money for the vans because without the vans people won't have healthcare vans. So, yeah, that's what we want.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Severe repetitive loops of the word 'van' 8 times in 48 words. Childlike vocabulary devoid of operational strategy."
        }
    },
    {
        "pair_id": "PAIR-PIT-08",
        "scenario": "persuasive_pitches",
        "intended_audience": "Chief Technology Officer & Architecture Board",
        "communication_goal": "Pitch migrating from monolithic Ruby backend to Go microservices",
        "primary_flaw": "poor_logical_structure",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts measured CPU profiling, GC pause bottlenecks, and phased migration versus developer resume-driven hype.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-08-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Our Ruby on Rails monolith has served us well, but at twelve thousand requests per second, garbage collection pauses consume thirty-five percent of our server CPU time, costing fifty thousand dollars monthly in excess AWS EC2 instances. We profiled our core authentication service: porting it to Go reduced memory consumption by seventy percent while slashing p99 latency from three hundred milliseconds to twelve milliseconds. We propose a low-risk strangler fig migration strategy, extracting one bounded context per quarter without halting new feature work.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Architecturally sound: respects the legacy system, provides empirical profiling data (p99 from 300ms to 12ms), and specifies a gradual strangler fig migration pattern."
        },
        "flawed": {
            "sample_id": "PIT-08-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poor_logical_structure", "unsupported_claims"],
            "severity": "severe",
            "transcript": "Ruby is totally dead and nobody uses it anymore. Go is what Google uses and it's ten thousand times faster. We should immediately stop all product development for six months and rewrite our entire codebase into Go microservices with gRPC. Everyone on Twitter says microservices are the best architecture.",
            "rubric_labels": {
                "content_and_relevance": 1,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Recipe for architectural disaster: unscientific generalizations ('Ruby is dead'), irresponsible proposal to freeze product work for six months, and cites 'Twitter' as engineering justification."
        }
    },
    {
        "pair_id": "PAIR-PIT-09",
        "scenario": "persuasive_pitches",
        "intended_audience": "University Athletic Director",
        "communication_goal": "Pitch biometric wearable recovery monitoring for collegiate student athletes",
        "primary_flaw": "excessive_filler_words",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts injury prevention statistics and biometric heart rate variability (HRV) metrics versus vague lifestyle buzzwords.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-09-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Soft tissue injuries sidelined fourteen percent of our varsity roster last season, costing our athletic department over four hundred thousand dollars in rehabilitation expenses and forfeited tournament opportunities. By monitoring resting heart-rate variability and sleep recovery via wristbands, our strength coaches can identify neuromuscular fatigue forty-eight hours before strain occurs. Similar programs at Stanford and Michigan reduced hamstring tears by thirty-eight percent. Investing sixty thousand dollars in wearable recovery protects both our athletes' health and our championship trajectory.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Ties biometric HRV tracking directly to athlete well-being, $400k injury cost prevention, and benchmark comparisons with peer institutions."
        },
        "flawed": {
            "sample_id": "PIT-09-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessive_filler_words", "weak_transitions"],
            "severity": "moderate",
            "transcript": "Um, athletes get tired, you know? And like, if they get injured, it's pretty bad for the team. So, uh, these smart bands track, like, sleep and stuff. It's really cool because players can, you know, see how many hours they slept. And, um, basically it helps them not be as tired, I think.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "High filler word density, lacks specific physiological metrics (HRV, neuromuscular load), and concludes with an unconvincing 'I think'."
        }
    },
    {
        "pair_id": "PAIR-PIT-10",
        "scenario": "persuasive_pitches",
        "intended_audience": "Municipal Transit Authority",
        "communication_goal": "Pitch intelligent traffic signal priority for public transit buses",
        "primary_flaw": "weak_transitions",
        "flaw_severity": "minor",
        "contrastive_rationale": "Shows how seamless progression from bus schedule unreliability to commuter ridership gains makes a compelling civic case.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PIT-10-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "When cross-town buses spend thirty-two percent of their route time idling at red lights, riders abandon public transit for single-occupancy vehicles. By installing connected vehicle signal priority along the Grand Avenue corridor, transit buses approaching green lights can request a four-second green extension. In Portland, this single software adjustment increased on-time bus reliability to ninety-four percent while boosting daily commuter ridership by twelve percent, without increasing cross-traffic congestion.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Solid civic case: quantifies red-light idle time, details signal extension technology, and cites Portland's 94% reliability success."
        },
        "flawed": {
            "sample_id": "PIT-10-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_transitions", "unclear_articulation"],
            "severity": "minor",
            "transcript": "Buses get stuck at red lights. Traffic is bad on Grand Avenue. Portland did something with traffic lights. If the light stays green, the bus goes faster. People should ride buses more often instead of driving cars.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Choppy, disconnected sentences. Lacks connective transition words and omits the engineering specifications of signal priority."
        }
    },

    # -------------------------------------------------------------
    # SCENARIO 4: PRESENTATION DELIVERY
    # -------------------------------------------------------------
    {
        "pair_id": "PAIR-PRE-01",
        "scenario": "presentation_delivery",
        "intended_audience": "Executive Leadership (Quarterly Business Review)",
        "communication_goal": "Present Q3 Enterprise SaaS customer acquisition and revenue telemetry",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows executive summary framing with actionable headlines versus reciting dense slide tables line-by-line.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-01-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Good morning. In Q3, our enterprise annual recurring revenue surpassed forty-two million dollars, representing thirty-four percent year-over-year expansion. The single largest driver of this growth was our new multi-cloud compliance module, which achieved forty-five percent attach rates across Fortune 500 renewals. On this slide, you see our customer acquisition cost dropped eighteen percent to fourteen thousand dollars, while net revenue retention held firm at one hundred and twenty-two percent.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Polished executive presentation: leads with top-line ARR milestone, highlights the key product catalyst, and validates capital efficiency."
        },
        "flawed": {
            "sample_id": "PRE-01-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "excessive_filler_words", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Um, so on this slide there's a lot of numbers. Uh, row one shows revenue, which was forty-two million, I think. And then if you look over in column D, that's customer acquisition cost. It's lower than before, which is good. And, um, there's another chart on the next slide about retention. So, yeah, overall things went pretty well last quarter.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Passive reading of slide coordinates ('row one shows', 'column D'). Lacks synthesis, strategic context, and narrative direction."
        }
    },
    {
        "pair_id": "PAIR-PRE-02",
        "scenario": "presentation_delivery",
        "intended_audience": "Cross-functional Product Sprint Retrospective",
        "communication_goal": "Review sprint velocity bottlenecks and propose automated CI improvements",
        "primary_flaw": "unnecessary_repetition",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts actionable blameless sprint retro action items versus cyclical complaining about flaky integration tests.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-02-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "In Sprint 24, our team completed seventy-two story points against an eighty-point commitment. Our main bottleneck was integration test flakiness in our end-to-end Cypress test suite, which caused thirty-four build failures on branches that had zero regressions. This cost the team eighteen developer hours in manual re-runs. For Sprint 25, we are quarantining the four most volatile test specs into an asynchronous nightly pipeline, freeing pull request gates to complete in under ten minutes.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Constructive engineering retro: measures sprint velocity variance, isolates specific friction root cause (Cypress flakiness), and implements a quarantine protocol."
        },
        "flawed": {
            "sample_id": "PRE-02-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unnecessary_repetition", "weak_transitions"],
            "severity": "moderate",
            "transcript": "The tests were just so flaky. Like, the tests failed, and then we ran the tests again, and the tests failed again. Flaky tests are the worst because when tests are flaky, you can't trust the tests. So we spent the whole sprint dealing with flaky tests because the tests wouldn't pass.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Repeats 'tests' and 'flaky' 11 times in 50 words without proposing a single architectural remediation or process improvement."
        }
    },
    {
        "pair_id": "PAIR-PRE-03",
        "scenario": "presentation_delivery",
        "intended_audience": "Enterprise Customer Success Webinar",
        "communication_goal": "Demonstrate best practices for RBAC (Role-Based Access Control) in the new UI",
        "primary_flaw": "unclear_articulation",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows clear, concise step-by-step instructional pacing versus muddled jargon and cursor-hunting.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-03-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "To implement the principle of least privilege, navigate to Settings, select Workspace Roles, and click Custom Policy. Here, instead of granting global Admin rights to your billing managers, you can check the discrete 'View Invoices' and 'Update Payment Methods' permissions. This ensures your finance team has full autonomy without granting write access to production database credentials.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Crystal clear tutorial delivery: sequential UI navigation combined with the security rationale (least privilege, avoiding db credential exposure)."
        },
        "flawed": {
            "sample_id": "PRE-03-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unclear_articulation", "poorly_placed_pauses"],
            "severity": "moderate",
            "transcript": "So you go over here to... wait, no, not that tab, click this button... and then you kinda check these boxes for the roles thing. If you don't do this, people can see stuff they shouldn't see, which isn't good. So just click save and it should work.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Disorganized demo execution ('wait, no, not that tab'). Uses vague spatial descriptions ('this button', 'these boxes') that confuse webinar attendees."
        }
    },
    {
        "pair_id": "PAIR-PRE-04",
        "scenario": "presentation_delivery",
        "intended_audience": "Corporate Marketing All-Hands",
        "communication_goal": "Present the rebrand guidelines and unified visual design system",
        "primary_flaw": "monotonous_vocal_delivery",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates creative enthusiasm and brand philosophy versus dry, lifeless reading of color hex codes.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-04-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Our visual identity is shifting from utilitarian software provider to trusted enterprise partner. Notice the shift in our palette: we have retired our aggressive electric blues in favor of a warm, deep navy paired with accessible teal accents. Our new typography pairing elevates readability across mobile and desktop, while our component library guarantees WCAG triple-A color contrast across all customer touchpoints.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Inspiring design narrative connecting aesthetic decisions directly to accessibility standards (WCAG AAA) and brand positioning."
        },
        "flawed": {
            "sample_id": "PRE-04-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["monotonous_vocal_delivery", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "The new logo color is hex code 0F172A. The secondary color is 06B6D4. The font is Inter. Don't use the old font. Use the new font. If you use the old colors, that violates brand guidelines. So use the new hex codes for all slides.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Monotonous recital of raw hex codes. Stiff, punitive instructions with zero articulation of design philosophy."
        }
    },
    {
        "pair_id": "PAIR-PRE-05",
        "scenario": "presentation_delivery",
        "intended_audience": "Annual Sales Kickoff Conference",
        "communication_goal": "Unveil the new sales commission tier structure to motivate field reps",
        "primary_flaw": "weak_or_missing_conclusion",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows inspiring, high-energy sales compensation rollout versus a confusing mathematical maze that deflates morale.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-05-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "This year, we eliminated commission caps entirely. Once you achieve one hundred percent of your annual quota, your commission accelerator jumps from twelve percent to twenty-two percent on every dollar booked. For multi-year prepaid contracts, we added an immediate three percent cash kicker paid in the quarter of signature. We built this plan to reward our highest-conviction dealmakers. Let's make 2026 our most historic year.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Punchy and motivating: uncapped commissions, explicit accelerator numbers (12% to 22%), and inspiring sales leadership cadence."
        },
        "flawed": {
            "sample_id": "PRE-05-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_or_missing_conclusion", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "So the compensation plan has changed again. There's this formula with marginal multipliers and tier coefficients based on whether you sell product A or product B. If you hit quota, you get something, but if you don't hit the sub-quota for services, your accelerator gets reduced by some fraction. You can check the PDF on the intranet later to figure out what you'll make.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Confusing and bureaucratic. Tells reps to 'check a PDF to figure out what you make', deflating energy at an annual sales kickoff."
        }
    },
    {
        "pair_id": "PAIR-PRE-06",
        "scenario": "presentation_delivery",
        "intended_audience": "Technical Security Audit Review",
        "communication_goal": "Present the findings of a third-party penetration testing engagement",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts verified CVSS scoring and reproducible remediation patches against defensive downplaying of security vulnerabilities.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-06-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "The external penetration test identified two critical vulnerabilities: first, an unauthenticated server-side request forgery in our webhook dispatcher with a CVSS score of 9.1; second, a cross-site scripting flaw in our customer onboarding form. Within forty-eight hours of receipt, our security team patched the webhook endpoint with strict IP whitelisting and deployed input sanitization across all forms. Re-testing confirmed both exploit vectors are fully resolved with zero data exposure.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Objective security reporting: cites CVSS 9.1, explains exact architectural remediation (IP whitelisting), and verifies patch closure."
        },
        "flawed": {
            "sample_id": "PRE-06-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "poor_logical_structure"],
            "severity": "severe",
            "transcript": "The auditors found some theoretical vulnerabilities, but honestly nobody could ever actually exploit them in the real world. They claimed there was an SSRF bug, but our firewall would probably block it anyway. Security researchers always exaggerate severity to justify their consulting invoices. Everything is totally secure.",
            "rubric_labels": {
                "content_and_relevance": 1,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Dangerous rationalization of critical security findings ('nobody could ever exploit them', 'auditors exaggerate'). Catastrophic governance failure."
        }
    },
    {
        "pair_id": "PAIR-PRE-07",
        "scenario": "presentation_delivery",
        "intended_audience": "Hospital Board of Directors",
        "communication_goal": "Present quarterly surgical department infection control statistics",
        "primary_flaw": "excessively_slow_pacing",
        "flaw_severity": "minor",
        "contrastive_rationale": "Contrasts confident epidemiological data delivery against halting recital that creates unease.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-07-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "In Q3, our surgical site infection rate dropped to 0.42 percent, placing our hospital in the top fifth percentile nationally. This improvement followed our mandate requiring chlorhexidine skin prep protocols and thirty-minute prophylactic antibiotic timing windows. By preventing an estimated fourteen postoperative infections, we saved three hundred and ten patient hospitalization days and over five hundred thousand dollars in uncompensated readmission costs.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Authoritative clinical metrics: 0.42% infection rate, benchmarked to top national percentile, with associated patient day and cost savings."
        },
        "flawed": {
            "sample_id": "PRE-07-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessively_slow_pacing", "poorly_placed_pauses"],
            "severity": "minor",
            "transcript": "In Q3... our surgical... infection rate... was zero point four two percent. We used... chlorhexidine... skin prep... and antibiotics... and it helped... prevent... fourteen infections... which is... good for patients.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Painfully slow (68 WPM) with awkward mid-clause pauses. Creates an impression of hesitancy despite positive underlying clinical metrics."
        }
    },
    {
        "pair_id": "PAIR-PRE-08",
        "scenario": "presentation_delivery",
        "intended_audience": "Product and Engineering Town Hall",
        "communication_goal": "Announce the deprecation of a legacy mobile API version",
        "primary_flaw": "failure_to_answer_question",
        "flaw_severity": "severe",
        "contrastive_rationale": "Shows thoughtful customer migration timelines and developer transition documentation versus abrupt uncoordinated shutdowns.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-08-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Today, we are officially beginning the sunset process for v1 of our Mobile REST API. Version 1 currently handles less than three percent of traffic but accounts for forty percent of our security maintenance burden. We have scheduled an eighteen-month deprecation window: client automated warnings begin in June, hard error deprecation takes effect in December, and we have published a complete migration SDK on our developer portal with automated endpoint conversion scripts.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Exemplary API lifecycle management: justifies sunset with data (3% traffic vs 40% maintenance burden), establishes an 18-month staged schedule."
        },
        "flawed": {
            "sample_id": "PRE-08-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["failure_to_answer_question", "weak_transitions"],
            "severity": "severe",
            "transcript": "We are turning off the old API next week. We hate maintaining old code and the v1 endpoints are ugly. If mobile users experience crashes, they should just update their app. Developers should have migrated a long time ago anyway.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Reckless engineering attitude. Gives one week notice, insults customers ('ugly code', 'should have migrated long ago'), with zero mitigation."
        }
    },
    {
        "pair_id": "PAIR-PRE-09",
        "scenario": "presentation_delivery",
        "intended_audience": "University Faculty Senate",
        "communication_goal": "Present proposed revisions to academic tenure evaluation criteria",
        "primary_flaw": "excessive_filler_words",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Demonstrates academic dignity and multi-dimensional faculty evaluation criteria versus nervous informal filler words.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-09-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "For decades, tenure evaluation has weighted single-author journal citations almost exclusively, disincentivizing interdisciplinary research and community-engaged scholarship. Our revised framework introduces a balanced triad: rigorous peer-reviewed scholarship, demonstrable excellence in undergraduate mentorship, and translational societal impact. By adopting these holistic standards, our university attracts visionary researchers who bridge foundational inquiry with real-world public policy.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Sophisticated academic rhetoric: deconstructs the citation monoculture and proposes an intellectually sound triad."
        },
        "flawed": {
            "sample_id": "PRE-09-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessive_filler_words", "weak_transitions"],
            "severity": "moderate",
            "transcript": "Um, so tenure is, like, pretty old-fashioned. And professors, you know, just write papers that nobody reads, basically. So, uh, we want to change it so, like, teaching counts more and, you know, being nice to students is good too. So that's what the committee came up with, basically.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "High filler frequency, dismissive tone toward faculty scholarship ('write papers that nobody reads'), lacks institutional gravitas."
        }
    },
    {
        "pair_id": "PAIR-PRE-10",
        "scenario": "presentation_delivery",
        "intended_audience": "Supply Chain Operations Review",
        "communication_goal": "Present root-cause analysis of warehouse fulfillment bottlenecks during peak season",
        "primary_flaw": "weak_transitions",
        "flaw_severity": "minor",
        "contrastive_rationale": "Shows systemic warehouse workflow diagnosis (slotting algorithms, pick paths) versus disjointed observations.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "PRE-10-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "During November peak, average pick-to-ship cycle times increased from forty-five minutes to two point four hours. Our root-cause analysis isolated two specific structural constraints: first, thirty percent of top-velocity promotional SKUs were slotted in distant mezzanine bays, tripling associate travel distance; second, conveyor merge points suffered barcode scan misreads due to degraded sensor lenses. Re-slotting high-velocity items and replacing the five optical sensors restored our pick-to-ship velocity to thirty-eight minutes within one week.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Logistics excellence: quantifies cycle time degradation (45 min to 2.4 hr), isolates physical root causes (slotting, optical sensors), and verifies the fix."
        },
        "flawed": {
            "sample_id": "PAIR-10-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_transitions", "unclear_articulation"],
            "severity": "minor",
            "transcript": "The warehouse was super busy. Things were in the wrong place on shelves. Conveyor belts were jammed. Workers were walking back and forth a lot. Then we moved some boxes and cleaned the scanners and it got faster.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 3
            },
            "annotation_rationale": "Oversimplified prose ('things were in the wrong place', 'moved some boxes') with zero operational metrics or statistical rigor."
        }
    },

    # -------------------------------------------------------------
    # SCENARIO 5: ACADEMIC EXPLANATIONS
    # -------------------------------------------------------------
    {
        "pair_id": "PAIR-ACA-01",
        "scenario": "academic_explanations",
        "intended_audience": "Undergraduate Computer Science Students",
        "communication_goal": "Explain how public-key cryptography (RSA) enables secure communication over untrusted channels",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows how an intuitive physical padlock metaphor illuminates asymmetric keypairs before diving into modular arithmetic.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-01-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Imagine you want to receive sensitive mail from someone you have never met. Instead of mailing them a key that a mail thief could copy, you send them an open padlock. Anyone in the world can snap that padlock shut around a box, but only you hold the private key that unlocks it. This is asymmetric cryptography. In mathematics, we replace the physical padlock with a one-way trapdoor function: multiplying two massive prime numbers is computationally trivial, but factoring their five-hundred-digit product would require billions of years of supercomputer time.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Brilliant pedagogical transition: bridges the open-padlock physical intuition seamlessly into the mathematical one-way trapdoor function."
        },
        "flawed": {
            "sample_id": "ACA-01-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "unclear_articulation", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "So RSA is based on Euler's totient theorem where phi of n equals p minus one times q minus one. You pick e coprime to phi of n and then compute the modular multiplicative inverse d such that ed is congruent to one mod phi of n. And then you do c equals m to the e mod n to encrypt. If you don't understand number theory, this won't make sense, but that's how it works.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Hostile pedagogical opening. Dumps modular equations without providing any conceptual intuition for why public/private keys exist."
        }
    },
    {
        "pair_id": "PAIR-ACA-02",
        "scenario": "academic_explanations",
        "intended_audience": "Introductory Biology Undergraduates",
        "communication_goal": "Explain how CRISPR-Cas9 performs targeted genomic editing",
        "primary_flaw": "unnecessary_repetition",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows the molecular machinery explained as a guided search-and-replace mechanism versus repetitive jargon.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-02-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Think of the human genome as a three-billion-letter encyclopedic textbook. If there is a single typo causing sickle cell disease, traditional medicine had no way to correct it without rewriting entire chapters. CRISPR-Cas9 functions like a molecular 'find-and-replace' tool. It consists of two components: a guide RNA molecule that acts like a GPS homing beacon, matching the exact twenty-letter genetic typo; and the Cas9 enzyme, which acts like microscopic molecular scissors, cleaving the flawed sequence so the cell's natural repair enzymes can insert the healthy code.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Pedagogical masterclass: uses 'find-and-replace' and 'molecular GPS + scissors' analogies to explain gRNA and Cas9 endonuclease action."
        },
        "flawed": {
            "sample_id": "ACA-02-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unnecessary_repetition", "weak_transitions"],
            "severity": "moderate",
            "transcript": "CRISPR edits genes. It edits genes because it's a gene editor. There is Cas9 and RNA and they cut the DNA. When the DNA is cut, the DNA gets edited. So gene editing happens when CRISPR edits the gene sequence. Editing genes is what CRISPR does in biology.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 1,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Extreme tautological repetition: uses the words 'gene' and 'edit' 10 times in 48 words without explaining the mechanism of guide RNA or PAM sites."
        }
    },
    {
        "pair_id": "PAIR-ACA-03",
        "scenario": "academic_explanations",
        "intended_audience": "Economics 101 College Students",
        "communication_goal": "Explain why printing excess currency causes price inflation using the Quantity Theory of Money",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts the mathematical relationship between money supply, velocity, and real output (MV=PQ) against partisan political blaming.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-03-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Imagine an island economy with ten coconuts and ten one-dollar bills. Each coconut naturally trades for one dollar. If the island governor doubles the currency supply to twenty dollars overnight, there are still only ten coconuts on the trees. Because twice as many paper dollars are now competing for the exact same physical output, sellers adjust their prices to two dollars per coconut. This demonstrates the Quantity Theory of Money: inflation occurs when the growth rate of money expands faster than the productive output of goods and services.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Classic island coconut micro-model that makes the macro equation (MV=PY) immediately intuitive to beginning students."
        },
        "flawed": {
            "sample_id": "ACA-03-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Inflation happens because greedy corporations just decide to raise prices to make record profits. And also the government prints money because politicians want to buy votes. Printing money has no effect on real goods unless businesses are being selfish and gouging consumers. If the government just capped prices, inflation would be zero percent forever.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Replaces economic theory with political talking points. Ignores monetary velocity, supply-demand mechanics, and shortages caused by price caps."
        }
    },
    {
        "pair_id": "PAIR-ACA-04",
        "scenario": "academic_explanations",
        "intended_audience": "Undergraduate Physics Students",
        "communication_goal": "Explain the Second Law of Thermodynamics and the physical meaning of entropy",
        "primary_flaw": "excessively_fast_pacing",
        "flaw_severity": "minor",
        "contrastive_rationale": "Contrasts statistical microstate probabilities against a rushed recitation of formulas.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-04-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "If you drop an egg onto the floor, it shatters into a chaotic mess. You will never observe those scattered fragments spontaneously reassemble themselves into a pristine shell. The Second Law of Thermodynamics is not a physical prohibition against reassembly; it is a statistical certainty. There is only one unique arrangement of molecules that corresponds to an intact egg, but there are trillions of trillions of arrangements that correspond to a shattered mess. Entropy is simply a measure of that probability: isolated systems evolve toward configurations with the greatest number of available microstates.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Brilliant clarification: entropy is not mysterious disorder, but Boltzmann's statistical probability of microstate multiplicity."
        },
        "flawed": {
            "sample_id": "ACA-04-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessively_fast_pacing", "poorly_placed_pauses"],
            "severity": "minor",
            "transcript": "EntropyisS=klnWwhereWisnumberofmicrostatesanddelatSgreaterthanzeromeansthingsgetmessyandeggsbreakbecauseisolatedsystemsdecayintomaximumprobabilityquickly.",
            "rubric_labels": {
                "content_and_relevance": 4,
                "structure_and_coherence": 3,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Rushed formula recitation without explanation of what 'k', 'W', or 'microstate' physically represent."
        }
    },
    {
        "pair_id": "PAIR-ACA-05",
        "scenario": "academic_explanations",
        "intended_audience": "Psychology 101 Students",
        "communication_goal": "Explain the difference between Classical Conditioning and Operant Conditioning",
        "primary_flaw": "monotonous_vocal_delivery",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows engaging behavioral experimental storytelling versus dry dictionary definition reading.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-05-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "The distinction between classical and operant conditioning hinges on who acts first: the environment or the organism. In Pavlovian classical conditioning, the organism is passive: an environmental bell is paired with food until a reflexive biological response—salivation—is involuntarily triggered. In Skinnerian operant conditioning, the organism is active: an animal voluntarily operates on its environment—such as a rat pressing a lever—and its future behavior is shaped by subsequent consequences: reinforcement or punishment.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Clean conceptual taxonomy: involuntary reflex (Pavlovian passive) versus voluntary consequence-shaped action (Skinnerian active)."
        },
        "flawed": {
            "sample_id": "ACA-05-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["monotonous_vocal_delivery", "unclear_articulation"],
            "severity": "moderate",
            "transcript": "Conditioning has two types. Classical is Pavlov with the dogs and the meat powder. Operant is Skinner with the pigeon boxes and the shock grids. One is stimulus-stimulus and the other is stimulus-response-reinforcer. Read chapter four for the exam details.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 1,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Lifeless bullet-point reading without explaining the underlying behavioral mechanism. Ends with lazy test-deferral."
        }
    },
    {
        "pair_id": "PAIR-ACA-06",
        "scenario": "academic_explanations",
        "intended_audience": "Philosophy of Mind Seminar",
        "communication_goal": "Explain John Searle's Chinese Room argument against strong artificial intelligence",
        "primary_flaw": "weak_or_missing_conclusion",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts the syntactic manipulation versus semantic intentionality thought experiment versus an abrupt unfinished ending.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-06-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "John Searle asks us to imagine an English-speaker locked in a room with a comprehensive rulebook that maps incoming Chinese characters to outgoing Chinese characters. To observers outside the room, the responses appear indistinguishable from a native speaker. Yet the person inside understands zero Chinese; they are merely manipulating formal symbols. Searle's argument demonstrates that syntax does not constitute semantics: computation alone, no matter how sophisticated, cannot generate genuine intentionality or conscious understanding.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Accurate and rigorous presentation of Searle's core philosophical deduction: syntax is insufficient for semantics."
        },
        "flawed": {
            "sample_id": "ACA-06-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_or_missing_conclusion", "unnecessary_repetition"],
            "severity": "moderate",
            "transcript": "There's this guy in a room with Chinese characters. People slide Chinese characters under the door and he looks up rules in a book. The book tells him what characters to slide back out. So he slides characters out and people think he knows Chinese, but he doesn't know Chinese. And, um, yeah, that's pretty much what Searle wrote.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 2,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Describes the scenario mechanics but completely fails to articulate the philosophical conclusion regarding syntax vs semantics."
        }
    },
    {
        "pair_id": "PAIR-ACA-07",
        "scenario": "academic_explanations",
        "intended_audience": "Undergraduate Chemistry Students",
        "communication_goal": "Explain Le Chatelier's Principle and chemical equilibrium shifts",
        "primary_flaw": "excessive_filler_words",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows dynamic chemical equilibrium and stress compensation explained clearly versus halting filler words.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-07-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Chemical equilibrium is not a static pause; it is a dynamic balance where forward and reverse reaction rates are precisely identical. Le Chatelier's Principle states that when a dynamic equilibrium experiences an external stress—such as a change in concentration, pressure, or temperature—the system shifts its reaction position to counteract that disturbance. For example, in the exothermic synthesis of ammonia, adding external heat drives the reaction in reverse toward the reactants to absorb that thermal energy.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Clear dynamic chemical definition paired with an intuitive exothermic ammonia synthesis stress example."
        },
        "flawed": {
            "sample_id": "ACA-07-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["excessive_filler_words", "weak_transitions"],
            "severity": "moderate",
            "transcript": "Um, so when reactions are at equilibrium, like, things are balanced. And then, you know, if you, like, mess with it by adding heat or stuff, it, um, tries to, you know, un-mess itself, basically. Like, it shifts the other way to, you know, undo what you did.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 1,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 1
            },
            "annotation_rationale": "Heavy filler density, non-scientific terminology ('mess with it', 'un-mess itself'). Lacks any chemical equation examples."
        }
    },
    {
        "pair_id": "PAIR-ACA-08",
        "scenario": "academic_explanations",
        "intended_audience": "Organic Chemistry Undergraduates",
        "communication_goal": "Explain the difference between SN1 and SN2 nucleophilic substitution reaction mechanisms",
        "primary_flaw": "poor_logical_structure",
        "flaw_severity": "severe",
        "contrastive_rationale": "Contrasts carbocation intermediate kinetics (unimolecular) versus backside attack inversion (bimolecular).",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-08-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "The fundamental difference between SN1 and SN2 reactions is whether substitution occurs in two distinct steps or one concerted step. In an SN1 mechanism, the leaving group departs first, forming a planar carbocation intermediate. Because the nucleophile can attack from either face of that flat carbocation, SN1 produces a racemic mixture with first-order kinetics. In contrast, SN2 is a concerted, one-step backside displacement: the incoming nucleophile attacks simultaneously as the leaving group departs, yielding complete stereochemical inversion with second-order kinetics.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Chemically rigorous: contrasts rate law kinetics (1st vs 2nd order), intermediates (carbocation vs concerted), and stereochemistry (racemic vs inversion)."
        },
        "flawed": {
            "sample_id": "ACA-08-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["poor_logical_structure", "unclear_articulation"],
            "severity": "severe",
            "transcript": "SN1 and SN2 both substitute things. In SN1, something leaves and then another thing attacks, or maybe it attacks at the same time in SN2. One of them makes a carbocation, which is tertiary, and the other one is primary because of steric hindrance. Memorize which solvent is polar aprotic for the quiz.",
            "rubric_labels": {
                "content_and_relevance": 2,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Muddled, hesitant phrasing ('or maybe it attacks at the same time'). Conflates mechanisms without clarifying the rate-determining step."
        }
    },
    {
        "pair_id": "PAIR-ACA-09",
        "scenario": "academic_explanations",
        "intended_audience": "Undergraduate Artificial Intelligence Seminar",
        "communication_goal": "Explain how the Self-Attention mechanism in Transformer architectures works",
        "primary_flaw": "weak_opening",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Shows how the Query-Key-Value database retrieval metaphor clarifies attention matrices versus mathematical opacity.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-09-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "Unlike recurrent networks that process text sequentially from left to right, self-attention allows a neural model to connect every word in a sequence directly to every other word simultaneously. It operates like a soft database lookup using Queries, Keys, and Values. For every token, the model computes a Query vector, taking dot products against the Key vectors of all other words to measure contextual relevance. These scores pass through a softmax function, creating weighted attention coefficients that blend the Value vectors into contextualized representations.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 4,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Superb conceptual framing: contrasts sequential recurrence with parallel QKV dot-product attention and softmax normalization."
        },
        "flawed": {
            "sample_id": "ACA-09-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["weak_opening", "unclear_articulation"],
            "severity": "moderate",
            "transcript": "Transformers are, like, the hottest thing in AI right now because of ChatGPT. So there's this paper 'Attention Is All You Need'. It does matrix multiplications on tensors. Q times K transpose divided by square root of d sub k times V. It's basically just linear algebra on GPUs.",
            "rubric_labels": {
                "content_and_relevance": 3,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Hype-driven opening ('hottest thing in AI'). Recites the raw equation without explaining what Query, Key, or Value vectors intuitively mean."
        }
    },
    {
        "pair_id": "PAIR-ACA-10",
        "scenario": "academic_explanations",
        "intended_audience": "Introduction to Linguistics Students",
        "communication_goal": "Explain the concept of linguistic relativity (the Sapir-Whorf hypothesis)",
        "primary_flaw": "unsupported_claims",
        "flaw_severity": "moderate",
        "contrastive_rationale": "Contrasts empirically supported weak linguistic relativity (color perception, spatial orientation) against discredited extreme linguistic determinism.",
        "dataset_version": "1.0.0",
        "ideal": {
            "sample_id": "ACA-10-IDEAL",
            "example_type": "ideal",
            "flaw_categories": [],
            "severity": "none",
            "transcript": "The Sapir-Whorf hypothesis investigates whether the structural categories of our language shape our habitual cognitive patterns. Modern cognitive linguistics rejects extreme linguistic determinism—the debunked claim that you cannot conceive of a concept without a specific word for it. Instead, empirical research supports weak linguistic relativity: languages that use absolute cardinal directions like 'north' rather than egocentric 'left' cultivate superior spatial awareness, and differing color terminologies influence cognitive sorting speed at visual boundaries.",
            "rubric_labels": {
                "content_and_relevance": 5,
                "structure_and_coherence": 5,
                "fluency_and_pacing": 5,
                "vocal_delivery": 5,
                "clarity_and_conciseness": 5
            },
            "annotation_rationale": "Accurate historical calibration: distinguishes debunked strong determinism from empirically supported weak relativity (Guugu Yimithirr spatial orientation)."
        },
        "flawed": {
            "sample_id": "ACA-10-FLAWED",
            "example_type": "flawed",
            "flaw_categories": ["unsupported_claims", "poor_logical_structure"],
            "severity": "moderate",
            "transcript": "Inuit people have fifty different words for snow, which literally proves that language imprisons your brain. If your language doesn't have a word for freedom, it is impossible for you to ever think about freedom or understand human rights. Your native language completely controls everything you are capable of thinking.",
            "rubric_labels": {
                "content_and_relevance": 1,
                "structure_and_coherence": 2,
                "fluency_and_pacing": 3,
                "vocal_delivery": 2,
                "clarity_and_conciseness": 2
            },
            "annotation_rationale": "Repeats the debunked popular myth of '50 words for snow' and makes unscientific assertions ('impossible to think without words')."
        }
    }
]

def generate_pilot_dataset_file(target_path: str):
    """Formats and writes the curated contrastive starter dataset."""
    formatted_pairs = []
    
    for item in PAIRS_DATA:
        pair_id = item["pair_id"]
        scenario = item["scenario"]
        audience = item["intended_audience"]
        goal = item["communication_goal"]
        flaw = item["primary_flaw"]
        severity = item["flaw_severity"]
        rationale = item["contrastive_rationale"]
        ver = item["dataset_version"]
        
        ideal_obj = item["ideal"]
        flawed_obj = item["flawed"]
        
        # Build SpeechSample objects
        ideal_sample = {
            "sample_id": ideal_obj["sample_id"],
            "pair_id": pair_id,
            "scenario": scenario,
            "language": "en",
            "intended_audience": audience,
            "communication_goal": goal,
            "transcript": ideal_obj["transcript"],
            "audio_reference": None,
            "example_type": "ideal",
            "flaw_categories": ideal_obj["flaw_categories"],
            "severity": ideal_obj["severity"],
            "rubric_labels": ideal_obj["rubric_labels"],
            "annotation_rationale": ideal_obj["annotation_rationale"],
            "provenance": "authored_expert_curated",
            "annotation_status": "reviewed",
            "dataset_version": ver
        }
        
        flawed_sample = {
            "sample_id": flawed_obj["sample_id"],
            "pair_id": pair_id,
            "scenario": scenario,
            "language": "en",
            "intended_audience": audience,
            "communication_goal": goal,
            "transcript": flawed_obj["transcript"],
            "audio_reference": None,
            "example_type": "flawed",
            "flaw_categories": flawed_obj["flaw_categories"],
            "severity": flawed_obj["severity"],
            "rubric_labels": flawed_obj["rubric_labels"],
            "annotation_rationale": flawed_obj["annotation_rationale"],
            "provenance": "authored_expert_curated",
            "annotation_status": "reviewed",
            "dataset_version": ver
        }
        
        formatted_pairs.append({
            "pair_id": pair_id,
            "scenario": scenario,
            "intended_audience": audience,
            "communication_goal": goal,
            "ideal_sample": ideal_sample,
            "flawed_sample": flawed_sample,
            "primary_flaw": flaw,
            "flaw_severity": severity,
            "contrastive_rationale": rationale,
            "dataset_version": ver
        })

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(formatted_pairs, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(formatted_pairs)} contrastive pairs in {target_path}")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "starter_pairs.json")
    generate_pilot_dataset_file(target)
