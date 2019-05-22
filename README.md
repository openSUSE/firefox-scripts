# Scripts for updating Mozilla prducts

## create-tar.sh
For updating Firefox.
Downloads tar-balls, checks locales, packages all.

## mfsa-yml.py
Queries MFSA (Mozilla Foundation Security Advisory) and parses them into the changelog format.
### Usage
1. Adjust versions inside create-tar.sh
2. Run in an empty directory
3. Copy resulting tar-balls to your repo

### Usage
1. Clone or update mfsa-git: git clone https://github.com/mozilla/foundation-security-advisories.git
2. Search which yaml-file(s) is relevant in the release notes
3. Search SUSE bugzilla-ID for updating Firefox with security vulns.
4. mfsa-yml.py foundation-security-advisories/announce/2017/mfsa<whichever you need>.yml <bugzilla ID>
