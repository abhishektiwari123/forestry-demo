# Dependency Audit Report

**Project:** Forestry Demo (Jekyll Static Site)
**Audit Date:** 2026-01-11
**Bundler Version:** 1.16.1

---

## Executive Summary

This audit identified **4 security vulnerabilities** (including 1 critical), **6 significantly outdated packages**, and **1 deprecated technology** in the project's Ruby dependencies.

**Risk Level:** HIGH - Immediate action recommended

---

## Security Vulnerabilities

### 1. CRITICAL: kramdown 1.16.2 - CVE-2020-14001

| Attribute | Value |
|-----------|-------|
| **Severity** | Critical (CVSS 9.8) |
| **Current Version** | 1.16.2 |
| **Fixed Version** | >= 2.3.0 |
| **Vulnerability** | Arbitrary file read / Remote code execution |

**Description:** A flaw in ruby-kramdown allows unintended file read access or embedded Ruby code execution when the `{::options /}` extension is used with the template option. An attacker could read sensitive files (e.g., `/etc/passwd`) or execute arbitrary Ruby code.

**References:**
- [GitHub Advisory GHSA-mqm2-cgpr-p4m6](https://github.com/advisories/GHSA-mqm2-cgpr-p4m6)
- [NVD CVE-2020-14001](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14001)

---

### 2. HIGH: Jekyll 3.6.2 - CVE-2018-17567

| Attribute | Value |
|-----------|-------|
| **Severity** | High |
| **Current Version** | 3.6.2 |
| **Fixed Version** | >= 3.6.3 |
| **Vulnerability** | Arbitrary file read via symlinks |

**Description:** Jekyll through 3.6.2 allows attackers to access arbitrary files by specifying a symlink in the `include` key in `_config.yml`.

**References:**
- [Jekyll Security Fixes Announcement](https://jekyllrb.com/news/2018/09/19/security-fixes-for-3-6-3-7-3-8/)
- [Snyk Jekyll Vulnerabilities](https://security.snyk.io/package/rubygems/jekyll)

---

### 3. MEDIUM: addressable 2.5.2 - CVE-2021-32740

| Attribute | Value |
|-----------|-------|
| **Severity** | Medium (CVSS 7.5) |
| **Current Version** | 2.5.2 |
| **Fixed Version** | >= 2.8.0 |
| **Vulnerability** | Regular Expression Denial of Service (ReDoS) |

**Description:** A maliciously crafted URI template can cause uncontrolled resource consumption, leading to denial of service.

**References:**
- [GitHub Advisory GHSA-jxhc-q857-3j6g](https://github.com/advisories/GHSA-jxhc-q857-3j6g)
- [NVD CVE-2021-32740](https://nvd.nist.gov/vuln/detail/CVE-2021-32740)

---

### 4. LOW-MEDIUM: ffi 1.9.18 - Multiple Issues

| Attribute | Value |
|-----------|-------|
| **Severity** | Low-Medium |
| **Current Version** | 1.9.18 |
| **Recommended Version** | >= 1.15.0 |
| **Issues** | Various security and compatibility fixes |

**Description:** The ffi gem version 1.9.18 has multiple security and stability issues that have been fixed in later versions.

---

## Outdated Packages

| Package | Current | Latest | Age | Priority |
|---------|---------|--------|-----|----------|
| **jekyll** | 3.6.2 | 4.4.1 | ~8 years | High |
| **kramdown** | 1.16.2 | 2.5.1 | ~8 years | Critical |
| **jekyll-feed** | 0.9.2 | 0.17.0 | ~7 years | Medium |
| **addressable** | 2.5.2 | 2.8.7 | ~7 years | High |
| **liquid** | 4.0.0 | 5.5.1 | ~7 years | Medium |
| **rouge** | 2.2.1 | 4.4.0 | ~7 years | Low |

---

## Deprecated Technology

### Ruby Sass (sass 3.5.5) - END OF LIFE

| Attribute | Value |
|-----------|-------|
| **Status** | Deprecated / End of Life |
| **EOL Date** | March 26, 2019 |
| **Current Version** | 3.5.5 |
| **Replacement** | Dart Sass via sassc or dartsass-sprockets |

**Description:** Ruby Sass reached its official end-of-life on March 26, 2019. The canonical Sass implementation is now Dart Sass. Projects should migrate to `sassc` or `dartsass-sprockets`.

**References:**
- [Official Deprecation Announcement](https://sass-lang.com/blog/ruby-sass-is-deprecated/)
- [Dart Sass GitHub](https://github.com/sass/dart-sass)

---

## Potential Bloat

### 1. nuggets (1.5.0)

**Issue:** The `jekyll-tagging` gem depends on `nuggets`, which is a general-purpose utility library adding ~1.5MB of unnecessary code.

**Recommendation:** Consider if `jekyll-tagging` is essential. If tags are needed, alternatives exist that don't pull in extra dependencies.

### 2. tzinfo-data

**Issue:** This gem is only needed for Windows and JRuby platforms but is included as a dependency.

**Status:** Already properly scoped with `platforms: [:mingw, :mswin, :x64_mingw, :jruby]` - no action needed.

---

## Recommendations

### Immediate Actions (Security)

1. **Upgrade Jekyll to 4.x series** (minimum 3.6.3 for security fix)
   - Latest stable: 4.4.1
   - Note: Jekyll 4.x requires Ruby >= 2.7.0

2. **Upgrade kramdown to >= 2.3.0**
   - Critical security fix for CVE-2020-14001
   - Jekyll 4.x will pull in kramdown 2.x automatically

3. **Update Gemfile.lock** to get patched versions of:
   - addressable >= 2.8.0
   - ffi >= 1.15.0

### Medium-Term Actions

4. **Migrate from Ruby Sass to sassc-embedded**
   - Ruby Sass is EOL and no longer receives security updates
   - Use `sassc-embedded` or configure asset pipeline differently

5. **Update Bundler** from 1.16.1 to latest (2.5.x)
   - Older Bundler versions may have security issues

6. **Review jekyll-tagging dependency**
   - Consider alternatives if the `nuggets` bloat is concerning

---

## Updated Gemfile (Recommended)

```ruby
source "https://rubygems.org"

# Core - Updated to latest stable 4.x
gem "jekyll", "~> 4.4.0"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-menus"
  gem "jekyll-tagging"
  gem "jekyll-archives"
end

# Windows timezone data (unchanged - properly scoped)
gem 'tzinfo-data', platforms: [:mingw, :mswin, :x64_mingw, :jruby]

# Note: Jekyll 4.x may require additional gems:
# gem "webrick", "~> 1.8"  # Required for Ruby 3.0+
```

---

## Migration Notes

### Breaking Changes in Jekyll 4.x

1. **Rouge 3+ syntax:** Some syntax highlighting themes may need updates
2. **Kramdown 2.x:** GFM (GitHub Flavored Markdown) parsing changes
3. **Liquid 4.x:** Already compatible
4. **Ruby requirement:** Minimum Ruby 2.7.0 (Ruby 3.x recommended)

### Recommended Migration Steps

1. Update Ruby to 3.1+ if not already
2. Update Bundler: `gem install bundler`
3. Apply the updated Gemfile
4. Run `bundle update`
5. Test site build: `bundle exec jekyll build`
6. Fix any deprecation warnings or errors
7. Test site locally: `bundle exec jekyll serve`

---

## Summary Table

| Category | Issues Found | Severity |
|----------|-------------|----------|
| Security Vulnerabilities | 4 | 1 Critical, 1 High, 2 Medium |
| Outdated Packages | 6 | Multiple years behind |
| Deprecated Technology | 1 | EOL since 2019 |
| Unnecessary Bloat | 1 | Low impact |

**Overall Risk Assessment:** HIGH - Recommend immediate updates to address security vulnerabilities.
