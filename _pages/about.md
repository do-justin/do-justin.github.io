---
layout: academic-home
title: About
permalink: /
social: false
selected_papers: false
announcements:
  enabled: false
latest_posts:
  enabled: false
---
I am a fourth-year medical student at Thomas Jefferson University, currently applying into anesthesiology.

I’m interested in how machine learning can use different kinds of clinical data. My current work asks whether intraoperative time series and physiologic waveforms add useful information beyond tabular clinical variables. I want to understand when text, images, audio, and physiologic signals improve clinical prediction, which models can use them, and how to interpret what those models learn.

I also study the emerging multimodal capabilities of large language models in medicine. My work includes benchmarking conversational image segmentation and evaluating home fall-risk assessment: where these models are useful, where they fail, and what needs to improve.

{% include scholar-metrics.liquid %}

## Selected publications

<div class="publications">
{% for id in site.data.featured %}{% bibliography --query @*[key={{ id }}] %}{% endfor %}
</div>

[All publications]({{ '/publications/' | relative_url }}) · [Research]({{ '/research/' | relative_url }})
