#!/usr/bin/env python3
import sys
import os
from collections import OrderedDict

def print_usage_and_exit():
    print("Usage: {0} /path/to/some.spec".format(sys.argv[0]))
    print("       Extracts the patches in the applied order from a spec-file")
    exit(1)


def main():
    if len(sys.argv) != 2:
        print_usage_and_exit()

    spec_file = sys.argv[1];
    dirname = os.path.dirname(spec_file)

    patch_names = OrderedDict()
    applied_patches = []
    in_prep = False
    for line in open(spec_file):
        if not in_prep and line.startswith("Patch"):
            first, second = line.split();
            patch_num = int(first[5:-1])
            patch_name = second.strip()
            patch_names[patch_num] = patch_name

        if line.startswith("%prep"):
            in_prep = True

        # Newer spec-files have autopatch, so we can print all in order and stop
        if in_prep and line.startswith("%autopatch"):
            for patch in patch_names.values():
                print(os.path.join(dirname, patch));
            return;

        if in_prep and line.startswith("%patch"):
            num = int(line.split()[0][6:])
            applied_patches.append(patch_names[num])

        # Once we enter %build, all patches have been read and can be printed
        if in_prep and line.startswith("%build"):
            for patch in applied_patches:
                print(os.path.join(dirname, patch));
            return;

if __name__ == "__main__":
    main()