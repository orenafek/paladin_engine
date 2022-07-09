D=$(realpath $(dirname $0))
export PYTHONPATH=${PYTHONPATH}:$D:$D/PaladinEngine

python3 $D/PaladinUI/paladin_cli/paladin_cli.py "$@"
