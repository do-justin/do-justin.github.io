---
layout: page
title: Publications
permalink: /publications/
nav: true
nav_order: 2
---
{% include scholar-metrics.liquid %}

<nav class="publication-index" aria-label="Publication sections">{% for group in site.data.publications.groups %}<a href="#{{ group.kind }}">{{ group.title }}</a>{% endfor %}</nav>
{% for group in site.data.publications.groups %}
<section class="publication-group" aria-labelledby="{{ group.kind }}"><div class="bibliography-heading"><h2 id="{{ group.kind }}">{{ group.title }}</h2></div>
{% if group.kind == 'presentation' %}{% assign presentations = site.data.publications.works | where: 'kind', 'presentation' %}{% for work in presentations %}{% include publication.liquid work=work %}{% endfor %}{% else %}
{% assign works = site.data.publications.works | where: 'kind', group.kind %}
{% for work in works %}{% bibliography --query @*[key={{ work.id }}] %}{% endfor %}
{% endif %}</section>
{% endfor %}
