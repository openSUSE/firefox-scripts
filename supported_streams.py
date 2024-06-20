#!/usr/bin/env python3

import requests

def get_json_data(package):
    url = f"https://smelt.suse.de/api/v1/basic/maintainedpackage/"
    res = requests.get(url, params={"package": package}, verify="/etc/ssl/certs/SUSE_Trust_Root.pem").json()
    if res == {}:
        raise ValueError(f"Unmaintained package {package}")

    return res

def filter_enabled_streams(values):
    result = set()
    for channel in values["results"]:
        supported = False;
        for binary in channel["binaries"]:
            if "status" in binary and binary["status"] != "unsupported":
                supported = True;
                break;

        codestream = channel["codestream"]
        
        result.add(codestream)

    # dict needs a tuple for key-values (lists and sets are not working)
    return tuple(sorted(list(result)))


def print_simple_list(packages, codestreams):
    pack_str = " & ".join(sorted(packages))
    print("Send", pack_str, "to codestreams:", ", ".join(codestreams))

def find_source(codestream):
    if "SLE-11" in codestream:
        return "Devel:Desktop:Mozilla:SLE-11-SP3:current"
    if "SLE-12" in codestream:
        return "Devel:Desktop:Mozilla:SLE-12:current"
    if "SLE-15" in codestream:
        return "Devel:Desktop:Mozilla:SLE-15:current"
    if "ALP" in codestream:
        return "Devel:Desktop:Mozilla:SLE-15:current"
    return "????"

def print_sr_commands(packages, codestreams):
    for package in packages:
        print(package + ":")
        for codestream in codestreams:
            if package == "MozillaFirefox" and "SLE-11-SP3" in codestream:
                # Don't submit Firefox to SP3, because it is handled differently
                continue
            if "Carwos" in codestream:
                # Carwos inherits from SLE15. Another corner case.
                continue
            source = find_source(codestream)
            print("isc sr --no-cleanup " + source + "/" + package + " " + codestream)
        print("")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="supported_streams",
        description="Look up to which codestreams a package should be submitted to"
    )
    parser.add_argument("-s", "--sr", help="Craft `isc sr` commands (Mozilla-specific)", action='store_true')
    parser.add_argument(
        "packages",
        help="List of packages to be queried",
        type=str,
        nargs="+"
    )

    args = parser.parse_args()

    codestreams = dict()
    for package in args.packages:
        values = get_json_data(package)
        streams = filter_enabled_streams(values)

        # Collect all packages with the same supported codestreams
        if streams not in codestreams:
            codestreams[streams] = []
        codestreams[streams].append(package)

    for codestreams, packages in codestreams.items():
        if args.sr:
            print_sr_commands(packages, codestreams)
        else:
            print_simple_list(packages, codestreams)
