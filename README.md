# Scripts for updating Mozilla prducts

## create-tar.sh
For updating Firefox.
Downloads tar-balls, checks locales, packages all.

### Usage
1. Have create-tar.sh in your `$PATH` (or call it directly, if you don't mind the typing)
2. Run create-tar.sh without argument to show help-output
3. Copy example tar_stamps from help-output
4. Go into an empty directory, create tar_stamps and adjust to your needs
5. Run `create-tar.sh tar_stamps`
6. Copy resulting tar-balls to your repo

## releasenotes.py
Queries official release notes and MFSA (Mozilla Foundation Security Advisory) and parses them into the changelog format.

### Usage
1. Clone or update https://github.com/mozilla/release-notes
1. Clone or update https://github.com/thundernest/thunderbird-notes
1. Clone or update https://github.com/mozilla/foundation-security-advisories
1. Search for the correct release notes file
1. Search which yaml-file(s) is relevant in the release notes
1. Search SUSE bugzilla-ID for updating Firefox with security vulns.
1. `releasenotes.py release-notes/releases/firefox-<VERSION> foundation-security-advisories/announce/<YEAR>/mfsa<whichever you need>.yml <bugzilla ID>`

Note: All files can be passed individually as well. Or you can parse multiple releases in one go. Files are parsed in the order they are given in the commandline.

## sync\_ff
Program to sync an OBS repo with the github-repo

This will delete all `*.patch`-files in the github-repo and copy over the new ones (in order to notice deleted patches).
It will also copy all relevant Firefox-files to github-repo/Firefox/ (excluding tarballs, scripts and the like)

### Usage
1. Put or better yet link sync\_ff in a directory in your $PATH
2. Go into your OBS-repo you want to sync
3. Specify github-repo path (your local checkout)
    1. Either by giving it directly: `sync_ff /your/path/here`
    2. By hardcoding it into `sync_ff` (`DEFAULT_FF_SYNC_TARGET`)
    3. By giving it via env-variable: `FF_SYNC_TARGET=/tmp sync_ff`
    4. By giving it via env-variable from your `.bashrc`

## spec\_patch\_series

Program to import all patchfiles into an hg-repo from a given rpm-spec file.

### Usage
1. Go to your hg repo
2. run script with the associated spec-file
3. Apply the patches in the patch-queue


## get\_mozconfig\_from\_spec

If one wants to build FF or TB without OBS, one needs a mozconfig. This file is generated in the spec-file.
This script, utilizing the rpm build-option `--with only_print_mozconfig` prints the mozconfig for a given
spec-file and suse-version.

### Usage
1. Find out which `%suse_version` you need (e.g. 1510)
2. Optional: Find out which arch you want (otherwise local arch is used, e.g. s390x)
3. Optional: Find out additional rpmbuild-commands you may need/want
3. Call `get_mozconfig_from_spec $SPECFILE $SUSE_VERSION [--target=$ARCH]`


## chr

Script to chroot into an OBS chroot, doing additional preparation like mounting system directories and such.

### Usage
See help-output
