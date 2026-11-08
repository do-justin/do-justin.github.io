# Keep the native shell and add a keyboard shortcut to its existing main region.
Jekyll::Hooks.register :pages, :post_render do |page|
  next unless page.output_ext == '.html'
  page.output.sub!(/<body\b([^>]*)>/, '<body\1><a class="skip-link" href="#main-content">Skip to content</a>')
  page.output.sub!('role="main"', 'role="main" id="main-content" tabindex="-1"')
end
