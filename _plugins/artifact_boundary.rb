# A reviewed public site should not inherit unused theme assets or demo files.
Jekyll::Hooks.register :site, :post_read do |site|
  bibliography = site.data.fetch('publications').fetch('works')
                     .reject { |work| work['kind'] == 'presentation' }
                     .map { |work| "/assets/bib/#{work.fetch('id')}.bib" }
  allowed = %w[/assets/css/tailwind.css /assets/img/icon.svg /assets/img/justin-do.jpg
               /assets/img/orcid-id.svg /assets/img/google-scholar.webp
               /assets/js/nav-toggle.js /robots.txt /assets/pdf/Justin_Do_CV.pdf] + bibliography
  site.static_files.select! { |file| allowed.include?(file.relative_path) }
end
