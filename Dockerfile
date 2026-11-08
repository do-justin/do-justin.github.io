FROM amirpourmand/al-folio@sha256:5c4851775ffdc210902082d45d7f3b5b65a8464bd86dec5f42b4f9d6c47524e0
WORKDIR /srv/jekyll
ENV BUNDLE_FROZEN=true
COPY Gemfile Gemfile.lock requirements.txt /srv/jekyll/
RUN bundle install --jobs 2 --retry 3 && pip3 install --break-system-packages --no-cache-dir -r requirements.txt
ENV JEKYLL_ENV=production PYTHONUNBUFFERED=1
ENTRYPOINT []
CMD ["bash", "bin/build.sh"]
