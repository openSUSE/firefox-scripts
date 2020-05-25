#!/bin/bash

# Used to get a rough overview for https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Linux_compatibility_matrix

# One has to adjust package-names to whatever upstream calls it (e.g. "kernel" instead of "kernel-default")

# NOTE: stdc++ versions are difficult. There is no way to know which version is the one installed by default.
#       "Ususally" its the highest available one, but I found no other way to do it than looking directly in all ISOs
#       to see which is installed by default.

# NOTE: This script needs the tool "split" (https://github.com/msirringhaus/split), because I'm too
#       lazy to look up how to do it with awk and tr

. ~/.bashrc

function crawl() {
    packages="pixman glib glib2 glibc gcc gtk2 gtk3 llvm python3 kernel-default"
    tool="$1"
    streams="$2"

    for stream in $streams; do
        title=`echo $stream | split -c 1 :Update | split -c 1,2,3 :`
        echo "\"$title\": {"
        echo "    \"release\": {
        \"date\": \"1111-11\",
        \"eol\": \"2222-22\"
    },"
        echo "    \"versions\": {"
        for package in $packages; do
            versions=`$tool cat "$stream" "$package" "$package.spec" 2> /dev/null | grep "^Version:" | split -c="-1"`
            versions="\"$versions\""
            if [ "$package" = "llvm" ] || [ "$package" = "gcc" ]; then
                for xx in `seq 5 9`; do
                    tmp=`$tool cat "$stream" "$package$xx" "$package$xx.spec" 2> /dev/null | grep "^Version:" | split -c="-1" | split + -c 1`
                    if [ ! -z "$tmp" ]; then
                        versions="$versions, \"$tmp\""
                    fi
                done
                versions="[ $versions ]"
            fi

            if [ "$versions" != "\"\"" ]; then
                echo "        \"$package\": $versions,"
                if [ "$package" = "gcc" ]; then
                    echo "        \"stdc++\": $versions,"
                fi
            fi
        done
        echo "    }"
        echo "},"
    done
}

crawl "osc" "openSUSE:Leap:15.0 openSUSE:Leap:15.1 openSUSE:Leap:15.2 openSUSE:Leap:42.1 openSUSE:Leap:42.2 openSUSE:Leap:42.3"
crawl "osc -A https://api.suse.de" "SUSE:SLE-11-SP4:Update SUSE:SLE-12-SP1:Update SUSE:SLE-12-SP2:Update SUSE:SLE-12-SP3:Update SUSE:SLE-12-SP4:Update SUSE:SLE-12-SP5:Update SUSE:SLE-15:Update SUSE:SLE-15-SP1:Update SUSE:SLE-15-SP2:Update"
#crawl "osc -A https://api.suse.de" "SUSE:SLE-11-SP4:GA SUSE:SLE-12-SP1:GA SUSE:SLE-12-SP2:GA SUSE:SLE-12-SP3:GA SUSE:SLE-12-SP4:GA SUSE:SLE-12-SP5:GA SUSE:SLE-15:GA SUSE:SLE-15-SP1:GA SUSE:SLE-15-SP2:GA"
