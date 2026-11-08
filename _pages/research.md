---
layout: page
title: Research
permalink: /research/
nav: true
nav_order: 1
---
## Perioperative prediction and physiologic signals

<div class="research-project" markdown="1">
### Incremental value of intraoperative data

In our JAMIA Open study of 46,204 adults undergoing 57,055 noncardiac operations, we tested whether intraoperative measurements improved prediction of stage 2 or 3 postoperative acute kidney injury beyond preoperative information. We also compared engineered summary features with an MLP/LSTM model that retained temporal sequence.

Adding low-frequency intraoperative data improved gradient-boosted-tree AUROC from 0.891 to 0.896. The temporal model did not outperform simpler tabular approaches. I led study design, cohort construction, model development, validation, and manuscript preparation with clinical and computational collaborators.

[Paper](https://doi.org/10.1093/jamiaopen/ooag092) · [Citation]({{ '/publications/#aki-jamia-2026' | relative_url }})

### High-frequency waveform analysis

That result led to a follow-on question: could measurements recorded every five minutes miss useful physiology between observations? I am studying ECG, plethysmography, capnography, and airway-pressure waveforms from VitalDB, comparing engineered time-series features with interpretable tabular models for postoperative AKI and ICU-risk discrimination.

I led waveform processing, feature construction, modeling, and analysis. The work was presented as an ePoster at ANESTHESIOLOGY 2026; the manuscript remains in development.

[Conference record](https://www.abstractsonline.com/pp8/#!/21448/presentation/6835)
</div>

## Evaluation of multimodal medical AI

<div class="research-project" markdown="1">
I led a zero-shot conversational segmentation benchmark of 13,086 image-mask pairs across seven medical-imaging modalities. We evaluated Gemini 2.5 Flash and Flash-Lite against expert masks and audited dermoscopy performance across skin-tone groups.

Performance was strong on several photographic targets and weak on some radiologic structures. The dermoscopy audit found lower mask-generation success and overlap in darker-tone images. I led dataset curation, benchmark design, prompt implementation, fairness analysis, statistics, figures, and writing, with collaborators reviewing the technical methods.

The manuscript is a **preprint, not peer reviewed**. Its separate IARS/SOCCA conference abstract was published in the 2026 Anesthesia & Analgesia supplement.

[Preprint](https://doi.org/10.1101/2025.11.21.25340008) · [Related outputs]({{ '/publications/#segmentation-medrxiv-2025' | relative_url }})
</div>

## Home fall-risk assessment

<div class="research-project" markdown="1">
At Jefferson's Health Design Lab, I led development and evaluation of a multimodal workflow that identifies home hazards and visualizes suggested modifications. The JMIR Aging research letter reports a formative evaluation using 27 publicly licensed home images.

Reviewers preferred the enhanced, CDC-grounded recommendations over baseline prompting, while some generated visualizations introduced hazards. I led prototyping, evaluation coordination, analysis, and manuscript drafting. The study evaluates a proposed workflow; clinical deployment and effects on falls remain untested.

[Research letter](https://doi.org/10.2196/77591) · [Citation]({{ '/publications/#fall-risk-jmir-2026' | relative_url }})
</div>

## Future directions

I want to compare models trained directly on waveform sequences, including pretrained foundation models, with engineered features, and test whether those representations add information beyond clinical data. External validation should examine how performance and calibration vary across hospitals and patient populations.

I also want to study how clinicians interpret explanations and uncertainty, whether predictions change decisions such as postoperative monitoring, and whether those changes benefit patients.
