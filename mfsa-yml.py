#!/usr/bin/env python3
import yaml
import string
import sys
import re
import textwrap


if len(sys.argv) <= 1:
    print("Usage: {0} <mfsa.yml> [bsc#]".format(sys.argv[0]))
    exit(1)

if len(sys.argv) > 2:
    bsc = sys.argv[2]
else:
    bsc = ""

try:
    inpf = open(sys.argv[1], 'r')
    mfsa_data = inpf.read()
    inpf.close()
except Exception as e:
    print(e)
    exit(1)


mfsa_yaml = yaml.load(mfsa_data)

mfsa = string.replace(mfsa_data[3:string.find(mfsa_data, '.')], 'mfsa', 'MFSA ')

wrapBMO = textwrap.TextWrapper(
        initial_indent = "    ",
        subsequent_indent = "     ",
        width = 65)

wrapCHLOG = textwrap.TextWrapper(
        initial_indent = "    ",
        subsequent_indent = "    ",
        width = 65)

print("- update to {0} (bsc#{1})".format(mfsa_yaml['fixed_in'][0], bsc))
for a in mfsa_yaml['advisories']:
    cve = a
    bmos = []
    for b in mfsa_yaml['advisories'][a]['bugs']:
        bmos += str(b['url']).split(', ')
    bmos.sort()
    bmos = map(lambda b: "bmo#" + b, bmos)
    print("  * " + mfsa + "/" + cve)
    print(wrapBMO.fill("({0})".format(", ".join(bmos))))
    print(wrapCHLOG.fill(mfsa_yaml['advisories'][a]['title']))


