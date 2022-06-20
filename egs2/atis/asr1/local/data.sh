#!/usr/bin/env bash
# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

log() {
    local fname=${BASH_SOURCE[1]##*/}
    echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
}
SECONDS=0


stage=1
stop_stage=100000
log "$0 $*"
. utils/parse_options.sh

. ./db.sh
. ./path.sh
. ./cmd.sh

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )/..
gdrive_id="1uhYY48hO3N_swX25mgU6bmYGRTO2bf5x"

if [ $# -ne 0 ]; then
    log "Error: No positional arguments are required."
    exit 2
fi

if [ -z "${ATIS}" ]; then
    log "Fill the value of 'ATIS' of db.sh"
    ATIS="${parent_path}/ATIS"
    mkdir -p "$ATIS"
    echo "Path 'ATIS' not set in db.sh. Defaulting to ${ATIS}"
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    if [ ! -e "${ATIS}/all.trans.txt" ]; then
	    echo "stage 1: Downloading data to ${ATIS}"
      gdown $gdrive_id -O "${ATIS}/atis.tar.gz"
      cd $ATIS
      ls -a
      tar xf atis.tar.gz --strip-components 1
      rm *.tar.gz
      cd ..
    else
        log "stage 1: ${ATIS}/all.trans.txt already exists. Skip data downloading"
    fi
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    log "stage 2: Data Preparation"
    mkdir -p data/{train,dev,test}
    python3 local/data_prep.py ${ATIS}
    for x in test dev train; do
        for f in text wav.scp utt2spk; do
            sort data/${x}/${f} -o data/${x}/${f}
            sed -i '/^$/d' data/${x}/${f}
        done
        utils/utt2spk_to_spk2utt.pl data/${x}/utt2spk > "data/${x}/spk2utt"
        utils/validate_data_dir.sh --no-feats data/${x} || exit 1
    done
fi

log "Successfully finished. [elapsed=${SECONDS}s]"
