#!/bin/env bash
ENVPATH="${HOME}/pyenv/EnergyMonitoring"
python3 -m venv ${ENVPATH}
source ${ENVPATH}/bin/activate

pip install --upgrade pip

pip install pandas
pip install jupyter
pip install ipykernel
pip install SQLAlchemy
pip install neurio
pip install solaredge
# needed only for investigation and development purposes
# pip install xlrd
# pip install sklearn
# pip install sns
