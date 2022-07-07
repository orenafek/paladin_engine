D=$(realpath $(dirname $0))
export PYTHONPATH=${PYTHONPATH}:$D:$D/PaladinEngine

python3 $D/PaladinCLI/paladin_cli.py "$@"
