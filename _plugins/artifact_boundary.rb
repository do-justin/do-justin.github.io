# A reviewed public site should not inherit unused theme assets or demo files.
Jekyll::Hooks.register :site, :post_read do |site|
  site.static_files.select! do |file|
    path = file.relative_path
    allowed = %w[/assets/css/tailwind.css /assets/css/jekyll-pygments-themes-github.css
                 /assets/css/font-stack.css /assets/img/icon.svg /assets/img/justin-do.jpg
                 /assets/js/nav-toggle.js /assets/js/tooltips-setup.js /assets/js/no_defer.js
                 /assets/js/common.js /assets/js/copy_code.js /assets/js/jupyter_new_tab.js
                 /robots.txt]
    allowed.include?(path) || path.start_with?('/assets/bib/') || path == '/assets/pdf/Justin_Do_CV.pdf'
  end
end
