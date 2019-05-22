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

# Internal variables
LOCALE_FILE="firefox-$VERSION/browser/locales/l10n-changesets.json"
SOURCE_TARBALL="firefox-$VERSION$VERSION_SUFFIX.source.tar.xz"
FTP_URL="https://ftp.mozilla.org/pub/firefox/releases/$VERSION$VERSION_SUFFIX/source"
# Exit script on CTRL+C
trap "exit" INT

function check_tarball_source () {
  TARBALL=$1
  # Print out what is going to be done:
  if [ -e $TARBALL ]; then
      echo "Reuse existing file"
  elif wget --spider $FTP_URL/$TARBALL 2> /dev/null; then
      echo "Download file"
  else
      echo "Mercurial checkout"
  fi
}

function ask_cont_abort_question() {
  while true; do
    read -p "$1 [(c)ontinue/(a)bort] " ca
    case $ca in
        [Cc]* ) return 0 ;;
        [Aa]* ) return 1 ;;
        * ) echo "Please answer c or a.";;
    esac
  done
}

function check_for_binary() {
  if ! test -x $1; then
    echo "$1 is missing: execute zypper in $2"
    exit 5
  fi
}

# check required tools
check_for_binary /usr/bin/hg "mercurial"
check_for_binary /usr/bin/jq "jq"

# use parallel compression, if available
compression='-J'
pixz -h > /dev/null 2>&1
if (($? != 127)); then
  compression='-Ipixz'
fi

# Check what is going to be done and ask for consent
for ff in $SOURCE_TARBALL $SOURCE_TARBALL.asc; do
  printf "%-40s: %s\n" $ff "$(check_tarball_source $ff)"
done
$(ask_cont_abort_question "Is this ok?") || exit 0

# Try to download tar-ball from officiall mozilla-mirror
if [ ! -e $SOURCE_TARBALL ]; then
  wget https://ftp.mozilla.org/pub/firefox/releases/$VERSION$VERSION_SUFFIX/source/$SOURCE_TARBALL
fi
# including signature
if [ ! -e $SOURCE_TARBALL.asc ]; then
  wget https://ftp.mozilla.org/pub/firefox/releases/$VERSION$VERSION_SUFFIX/source/$SOURCE_TARBALL.asc
fi

# we might have an upstream archive already and can skip the checkout
if [ -e $SOURCE_TARBALL ]; then
  echo "skip firefox checkout and use available archive"
  # still need to extract the locale information from the archive
  echo "extract locale changesets"
  tar -xf $SOURCE_TARBALL $LOCALE_FILE
else
  # We are working on a version that is not yet published on the mozilla mirror
  # so we have to actually check out the repo

  # mozilla
  if [ -d firefox-$VERSION ]; then
    pushd firefox-$VERSION || exit 1
    _repourl=$(hg paths)
    case "$_repourl" in
      *$BRANCH*)
        echo "updating previous tree"
        hg pull
        popd || exit 1
        ;;
      * )
        echo "removing obsolete tree"
        popd || exit 1
        rm -rf firefox-$VERSION
        ;;
    esac
  fi
  if [ ! -d firefox-$VERSION ]; then
    echo "cloning new $BRANCH..."
    hg clone http://hg.mozilla.org/$BRANCH firefox-$VERSION
  fi
  pushd firefox-$VERSION || exit 1
  hg update --check
  [ "$RELEASE_TAG" == "default" ] || hg update -r $RELEASE_TAG
  # get repo and source stamp
  echo -n "REV=" > ../source-stamp.txt
  hg -R . parent --template="{node|short}\n" >> ../source-stamp.txt
  echo -n "REPO=" >> ../source-stamp.txt
  hg showconfig paths.default 2>/dev/null | head -n1 | sed -e "s/^ssh:/http:/" >> ../source-stamp.txt
  popd || exit 1

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
        hg clone "http://hg.mozilla.org/l10n-central/$locale" "l10n/$locale"
        [ "$RELEASE_TAG" == "default" ] || hg -R "l10n/$locale" up -C -r "$changeset"
        ;;
    esac
  done
echo "creating l10n archive..."
tar $compression -cf l10n-$VERSION$VERSION_SUFFIX.tar.xz --exclude=.hgtags --exclude=.hgignore --exclude=.hg l10n

# compare-locales
echo "creating compare-locales"
hg clone http://hg.mozilla.org/build/compare-locales
tar $compression -cf compare-locales.tar.xz --exclude=.hgtags --exclude=.hgignore --exclude=.hg compare-locales

