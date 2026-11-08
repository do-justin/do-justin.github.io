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

Building on our JAMIA Open study, we are investigating whether high-frequency intraoperative waveforms improve postoperative risk prediction. We extract time-series features from ECG, plethysmography, capnography, and airway-pressure waveforms in VitalDB and test their added value in interpretable tabular models.

I developed the waveform-processing and feature-extraction pipeline and led the modeling and analysis. We presented the work as an ePoster at ANESTHESIOLOGY 2026, with the manuscript currently being drafted.

[Conference record](https://www.abstractsonline.com/pp8/#!/21448/presentation/6835)
</div>

## Evaluation of multimodal medical AI

<div class="research-project" markdown="1">
I’m interested in the emerging capabilities of large language models. When [Gemini 2.5](https://developers.googleblog.com/en/conversational-image-segmentation-gemini-2-5/) introduced image segmentation through text prompts, I wanted to see how well it worked on medical images. We evaluated Gemini 2.5 Flash and Flash-Lite on 13,086 image-mask pairs across seven imaging modalities, comparing their outputs with expert masks.

Performance was strong on several photographic targets and weak on some radiologic structures. In our dermoscopy audit, masks were generated less often and had lower overlap with expert masks for darker-tone images. I designed and implemented the benchmark, including the skin-tone audit, and led the analysis and writing.

[Preprint](https://doi.org/10.1101/2025.11.21.25340008) · [Related outputs]({{ '/publications/#segmentation-medrxiv-2025' | relative_url }})
</div>

## Home fall-risk assessment

<div class="research-project" markdown="1">
At Jefferson's Health Design Lab, I led development and evaluation of a multimodal workflow that identifies home hazards and visualizes suggested modifications. The JMIR Aging research letter reports a formative evaluation using 27 publicly licensed home images.

Reviewers preferred the enhanced, CDC-grounded recommendations over baseline prompting, while some generated visualizations introduced hazards. I led prototyping, evaluation coordination, analysis, and manuscript drafting. The study evaluates a proposed workflow; clinical deployment and effects on falls remain untested.

[Research letter](https://doi.org/10.2196/77591) · [Citation]({{ '/publications/#fall-risk-jmir-2026' | relative_url }})
</div>

## Future directions

I hope to externally validate these models using multi-center data. I also plan to compare models trained directly on waveform sequences, including pretrained foundation models, with engineered features.
