#!/usr/bin/env python3
import yaml
import json
import string
import sys
import re
import textwrap

wrapBMO = textwrap.TextWrapper(
    initial_indent = "  ",
    subsequent_indent = "    ",
    width = 65)

wrapCHLOG = textwrap.TextWrapper(
    initial_indent = "    ",
    subsequent_indent = "    ",
    width = 65)


def print_release_note(json_data):
    data = json.loads(json_data)

    print("- {0}".format(data['title']))
    for note in data['notes']:
        if note["tag"] == "":
             # This is just the reference-link to upstream release notes
             continue

        if note ["tag"] == "Known":
            # We don't log known issues
            continue

        content = note["note"]
        if note["bug"] != "":
            content += " (bmo#{0})".format(note["bug"])

        # Replacing ([bug 1234123][0]) with [bmo#1234123]:
        content = re.sub("\(\[bug (?P<ID>[0-9]+)\]\[[0-9]+\]\)", "(bmo#\g<ID>)", content)

        # Replacing [something with a link][1] with "something with a link"
        content = re.sub("\[(?P<text>[^\]]+)\]\[\d+\]", "\g<text>", content)

        contentlines = content.splitlines()
        print(wrapBMO.fill("* {0}: {1}".format(note["tag"], contentlines[0])))

        for line in contentlines[1:]:
            linestrip = line.strip()

            # Skip empty lines
            if linestrip == "":
                continue

            # Skip URL-links
            if linestrip.startswith("[") and linestrip[1].isnumeric() and "]: https:" in line:
                continue

            print(wrapCHLOG.fill("{0}".format(line)))


def print_security_advisory(mfsa_data, bsc):
    mfsa_yaml = yaml.safe_load(mfsa_data)

    mfsa = mfsa_data[3:mfsa_data.find('.')].replace('mfsa', 'MFSA ')

    print("- Mozilla Firefox {0}".format(mfsa_yaml['fixed_in'][0]))
    print("  {0} (bsc#{1})".format(mfsa, bsc))
    for a in mfsa_yaml['advisories']:
        cve = a
        bmos = []
        for b in mfsa_yaml['advisories'][a]['bugs']:
            bmos += str(b['url']).split(', ')
        bmos.sort()
        bmos = map(lambda b: "bmo#" + b, bmos)
        print(wrapBMO.fill("* {0} ({1})".format(cve, ", ".join(bmos))))
        print(wrapCHLOG.fill(mfsa_yaml['advisories'][a]['title']))


def print_usage_and_exit():
    print("Usage: {0} [releasenote.json] [mfsa.yml] [bsc#]".format(sys.argv[0]))
    print("       json or yml-file(s) can be given in any order (and are printed in that order)")
    print("       Bug-ID, if any, has to be at the end")
    exit(1)


def main():
    if len(sys.argv) <= 1:
        print_usage_and_exit()

    json_files = []
    yml_files = []
    bsc = ""
    if sys.argv[-1].isnumeric():
        bsc = sys.argv.pop()

    for argument in sys.argv[1:]:
        try:
            inpf = open(argument, 'r')
            file_data = inpf.read()
            inpf.close()
        except Exception as e:
            print(e)
            exit(1)

        if argument.endswith(".json"):
            print_release_note(file_data)
        elif argument.endswith(".yml"):
            print_security_advisory(file_data, bsc)
        else:
            print("Wrong kind of file! Only yml and json-files supported!")
            print_usage_and_exit()

if __name__ == "__main__":
    main()
