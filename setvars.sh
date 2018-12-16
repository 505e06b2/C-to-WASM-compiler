#!/bin/bash

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
	PATH=${DIR}/bin/:$PATH
	unset DIR
	echo "Setup PATH for environment"
else
	echo "You need to source this file"
fi
