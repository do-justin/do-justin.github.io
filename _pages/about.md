---
layout: academic-home
title: About
permalink: /
---
I am a fourth-year medical student at Thomas Jefferson University, currently applying into anesthesiology.
At Jefferson, I am a research fellow in the Department of Anesthesiology and Perioperative Medicine and a research intern at the Health Design Lab.

My research focuses on the value of multimodal data for clinical prediction. I study whether intraoperative time series and physiologic waveforms add information beyond tabular clinical variables, and how we can interpret the models that use them. I hope to combine these signals with text, images, and audio.

I also study the emerging multimodal capabilities of large language models in medicine, with projects evaluating conversational image segmentation and home fall-risk assessment.

{% include scholar-metrics.liquid %}

## Selected publications

<div class="publications">
{% for id in site.data.featured %}{% bibliography --query @*[key={{ id }}] %}{% endfor %}
</div>

[All publications]({{ '/publications/' | relative_url }}) · [Research]({{ '/research/' | relative_url }})
