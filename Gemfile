source "https://rubygems.org"

# Jekyll 4.x includes security fixes and updated dependencies
# - Fixes CVE-2018-17567 (arbitrary file read via symlinks)
# - Pulls in kramdown >= 2.3 (fixes CVE-2020-14001 - critical RCE)
# - Pulls in addressable >= 2.8 (fixes CVE-2021-32740 - ReDoS)
gem "jekyll", "~> 4.4.0"

# Required for Ruby 3.0+ (WEBrick removed from stdlib)
gem "webrick", "~> 1.8"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-menus"
  gem "jekyll-tagging"
  gem "jekyll-archives"
end

# Windows does not include zoneinfo files, so bundle the tzinfo-data gem
gem 'tzinfo-data', platforms: [:mingw, :mswin, :x64_mingw, :jruby]
