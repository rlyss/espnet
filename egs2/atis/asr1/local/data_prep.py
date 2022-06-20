#!/usr/bin/env bash

import json
import os
import re
import subprocess
import sys

idir = sys.argv[1]
speaker = "synthetic"

for subset in ["train", "dev", "test"]:
    odir = os.path.join("data", subset)
    os.makedirs(odir, exist_ok=True)

    with open(os.path.join(idir, "nlu_iob", "iob." + subset)) as meta, open(
            os.path.join(odir, "text"), "w", encoding="utf-8"
    ) as text, open(os.path.join(odir, "wav.scp"), "w") as wavscp, open(
        os.path.join(odir, "utt2spk"), "w"
    ) as utt2spk:

        ids_seen = set()
        counter = 0

        for line in meta:
            [id, rest] = [i.strip() for i in line.split("BOS ")]
            if id in ids_seen: continue
            ids_seen.add(id)

            [utt, tags] = [i.strip() for i in rest.split(" EOS")]
            utt_list = utt.split(" ")
            tag_list = tags.split(" ")[1:]

            wavpath = os.path.join(idir, subset, id + ".wav")
            if not os.path.exists(wavpath): continue


            def merge_tags(acc, word, tag):
                if tag[0] == 'O':
                    return acc
                elif tag[0] == 'I' and acc:
                    pword, ptag = acc[-1]
                    acc[-1] = (pword + " " + word, ptag)
                    return acc
                else:
                    acc.append((word, tag[2:]))
                    return acc


            parsed_tags = []
            [parsed_tags := merge_tags(parsed_tags, word, tag) for word, tag in zip(utt_list, tag_list)]
            intent = tag_list[-1]

            intent_string = ' <sep> '.join(map(lambda sv: intent + " " + sv[1] + " " + sv[0], parsed_tags))

            text.write(str(counter) + " " + intent_string + " <utt> " + utt + "\n")
            wavscp.write(str(counter) + " " + wavpath + "\n")
            utt2spk.write(str(counter) + " " + str(counter) + "\n")

            counter += 1
