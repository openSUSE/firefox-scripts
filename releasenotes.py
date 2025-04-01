#!/usr/bin/env python3
import yaml
import json
import string
import sys
import re
import textwrap

# From https://gist.github.com/pypt/94d747fe5180851196eb
# because the yaml-module ignores duplicate keys and
# silently overwrites them, making us loose advisories
# if, e.g. no CVE-number has yet been issued.
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = set()
        for key_node, value_node in node.value:
            if ':merge' in key_node.tag:
                continue
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"Duplicate {key!r} key found in YAML.")
            mapping.add(key)
        return super().construct_mapping(node, deep)

wrapBMO = textwrap.TextWrapper(
    initial_indent = "  ",
    subsequent_indent = "    ",
    width = 65)

wrapCHLOG = textwrap.TextWrapper(
    initial_indent = "    ",
    subsequent_indent = "    ",
    width = 65)


def print_json_release_notes(json_data):
    data = json.loads(json_data)

    print("- {0}".format(data['title']))
    print_release_notes(data)


def print_yml_file(file_data, bsc):
    # yaml_data = yaml.safe_load(file_data)
    yaml_data = yaml.load(file_data, Loader=UniqueKeyLoader)
    if "release" in yaml_data:
        print_release_notes(yaml_data)
    else:
        print_security_advisory(file_data, yaml_data, bsc)


def print_release_notes(notes):
    for note in notes['notes']:
        if note["tag"] == "":
             # This is just the reference-link to upstream release notes
             continue

        if note ["tag"] == "Known":
            # We don't log known issues
            continue

        content = note["note"]
        if "bug" in note and (note["bug"] != "" and note["bug"] != None):
            content += " (bmo#{0})".format(note["bug"])

        # thunderbird
        if "bugs" in note and (note["bugs"] != "" and note["bugs"] != None):
            content += " ("
            content += ",".join([ "bmo#{0}".format(bug) for bug in note["bugs"] ])
            content += ")"

        # Replacing ([bug 1234123][0]) with [bmo#1234123]:
        content = re.sub("\\(\\[[b,B]ug (?P<ID>[0-9]+)\\]\\[[0-9]+\\]\\)", "(bmo#\\g<ID>)", content)

        # Replacing <a href="https://bugzilla.mozilla.org/1234123">1234123</a> with "bmo#1234123"
        content = re.sub("<a href=\"https://bugzilla.mozilla.org/(?P<ID>[0-9]+)\">.*</a>", "bmo#\\g<ID>", content)

        # Replacing [something with a link][1] with "something with a link"
        content = re.sub("\\[(?P<text>[^\\]]+)\\]\\[\\d+\\]", "\\g<text>", content)

        # Replacing [something with a link](http:...) with "something with a link"
        content = re.sub("\\[(?P<text>[^\\]]+)\\]\\((?P<link>[^\\)]+)\\)", "\\g<text>", content)

        # Remove embedded images such as <img src="$FOO" width="700" alt="$TEXT">
        content = re.sub("<img src=.*>", "", content)

        contentlines = content.splitlines()
        print(wrapBMO.fill("* {0}: {1}".format(note["tag"], contentlines[0])))

        for line in contentlines[1:]:
            linestrip = line.strip()

            # Skip empty lines
            if linestrip == "":
                continue

            # Skip URL-links
            if linestrip.startswith("[") and linestrip[1].isnumeric() and ("]: https:" in line or "]:https:" in line):
                continue

            print(wrapCHLOG.fill("{0}".format(line)))


def print_security_advisory(mfsa_data, mfsa_yaml, bsc):
    mfsa = mfsa_data[3:mfsa_data.find('.')].replace('mfsa', 'MFSA ')

    print("- Mozilla {0}".format(mfsa_yaml['fixed_in'][0]))
    print("  {0} (bsc#{1})".format(mfsa, bsc))
    for a in mfsa_yaml['advisories']:
        cve = a
        bmos = []
        for b in mfsa_yaml['advisories'][a]['bugs']:
            if 'url' not in b:
                continue
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
            print_json_release_notes(file_data)
        elif argument.endswith(".yml"):
            print_yml_file(file_data, bsc)
        else:
            print("Wrong kind of file! Only yml and json-files supported!")
            print_usage_and_exit()

if __name__ == "__main__":
    main()
