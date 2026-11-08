# The stock cache-bust gem only searches the site tree, while v1 assets live in
# the theme gem. Resolve both locations without copying theme assets into source.
require 'digest'
module ThemeAssetCache
  def bust_file_cache(input)
    site = @context.registers[:site]
    relative = input.to_s.sub(%r{^/}, '')
    roots = [site.source, site.theme&.root].compact
    path = roots.map { |root| File.join(root, relative) }.find { |file| File.file?(file) }
    path ? "#{input}?v=#{Digest::SHA256.file(path).hexdigest[0, 12]}" : input
  end

  def bust_css_cache(input)
    site = @context.registers[:site]
    sources = [File.join(site.source, 'Gemfile.lock')] +
              Dir[File.join(site.source, '{_sass,assets/css}', '**', '*.scss')].sort
    digest = Digest::SHA256.hexdigest(sources.select { |p| File.file?(p) }.map { |p| File.read(p) }.join)
    "#{input}?v=#{digest[0, 12]}"
  end
end
Liquid::Template.register_filter(ThemeAssetCache)
