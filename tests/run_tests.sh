#!/bin/bash

# Set config file
if [ "$1" = "full" ]; then
	cp .configs/.config_full.py utils/config.py
else
	cp .configs/.config_dev.py utils/config.py
	options=--sw
fi

# Execute test campaign
cd ../
source env/bin/activate
cd src/
echo "Execute the following command:"
echo "> pytest ../tests/unit_tests/ ../tests/utils/ --cov=./matmat/core/ --cov=./matmat/utils --cov-config=../tests/.coveragerc --no-cov-on-fail --cov-report=html:../tests/unit_tests/coverage/ $options"
pytest ../tests/unit_tests/ ../tests/utils/ --cov=./matmat/core/ --cov=./matmat/utils --cov-config=../tests/.coveragerc --no-cov-on-fail --cov-report=html:../tests/unit_tests/coverage/ $options

# Reset default config file
cd ../tests/
cp .configs/.config_full.py utils/config.py
