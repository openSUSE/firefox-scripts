#!/bin/bash

# TODO
# http://ftp.mozilla.org/pub/firefox/candidates/48.0-candidates/build2/linux-x86_64/en-US/firefox-48.0.json
# "moz_source_stamp": "c1de04f39fa956cfce83f6065b0e709369215ed5"
# http://ftp.mozilla.org/pub/firefox/candidates/48.0-candidates/build2/l10n_changesets.txt
#
# Node ID: 64ee63facd4ff96b3e8590cff559d7e97ac6b061

CHANNEL="esr60"
BRANCH="releases/mozilla-$CHANNEL"
RELEASE_TAG="FIREFOX_60_7_0esr_RELEASE"
VERSION="60.7.0"
VERSION_SUFFIX="esr"
LOCALE_FILE="firefox-$VERSION/browser/locales/l10n-changesets.json"

# check required tools
test -x /usr/bin/hg || ( echo "hg missing: execute zypper in mercurial"; exit 5 )
test -x /usr/bin/jq || ( echo "jq missing: execute zypper in jq"; exit 5 )

# use parallel compression, if available
compression='-J'
pixz -h > /dev/null 2>&1
if (($? != 127)); then
  compression='-Ipixz'
fi

# we might have an upstream archive already and can skip the checkout
if [ -e firefox-$VERSION$VERSION_SUFFIX.source.tar.xz ]; then
  echo "skip firefox checkout and use available archive"
  # still need to extract the locale information from the archive
  echo "extract locale changesets"
  tar -xf firefox-$VERSION$VERSION_SUFFIX.source.tar.xz $LOCALE_FILE
else
  # mozilla
  if [ -d firefox-$VERSION ]; then
    pushd firefox-$VERSION
    _repourl=$(hg paths)
    case "$_repourl" in
      *$BRANCH*)
        echo "updating previous tree"
        hg pull
        popd
        ;;
      * )
        echo "removing obsolete tree"
        popd
        rm -rf firefox-$VERSION
        ;;
    esac
  fi
  if [ ! -d firefox-$VERSION ]; then
    echo "cloning new $BRANCH..."
    hg clone http://hg.mozilla.org/$BRANCH firefox-$VERSION
  fi
  pushd firefox-$VERSION
  hg update --check
  [ "$RELEASE_TAG" == "default" ] || hg update -r $RELEASE_TAG
  # get repo and source stamp
  echo -n "REV=" > ../source-stamp.txt
  hg -R . parent --template="{node|short}\n" >> ../source-stamp.txt
  echo -n "REPO=" >> ../source-stamp.txt
  hg showconfig paths.default 2>/dev/null | head -n1 | sed -e "s/^ssh:/http:/" >> ../source-stamp.txt
  popd

  echo "creating archive..."
  tar $compression -cf firefox-$VERSION$VERSION_SUFFIX.source.tar.xz --exclude=.hgtags --exclude=.hgignore --exclude=.hg --exclude=CVS firefox-$VERSION
fi

# l10n
echo "fetching locales..."
test ! -d l10n && mkdir l10n
jq -r 'to_entries[]| "\(.key) \(.value|.revision)"' $LOCALE_FILE | \
  while read locale changeset ; do
    case $locale in
      ja-JP-mac|en-US)
        ;;
      *)
        echo "reading changeset information for $locale"
        echo "fetching $locale changeset $changeset ..."
        hg clone http://hg.mozilla.org/l10n-central/$locale l10n/$locale
        [ "$RELEASE_TAG" == "default" ] || hg -R l10n/$locale up -C -r $changeset
        ;;
    esac
  done
echo "creating l10n archive..."
tar $compression -cf l10n-$VERSION$VERSION_SUFFIX.tar.xz --exclude=.hgtags --exclude=.hgignore --exclude=.hg l10n

# compare-locales
echo "creating compare-locales"
hg clone http://hg.mozilla.org/build/compare-locales
tar $compression -cf compare-locales.tar.xz --exclude=.hgtags --exclude=.hgignore --exclude=.hg compare-locales

