#!/bin/bash
# defaults
BASE_PATH="${PWD}"
PUBLIC_PATH="${BASE_PATH}/public"
ASSETS_PATH="${PUBLIC_PATH}/assets"
SERVER_PATH="${BASE_PATH}/server"
APP_PATH="${SERVER_PATH}/app"
CONF_PATH="${SERVER_PATH}/conf"
LOG_PATH="${SERVER_PATH}/logs"
TMP_PATH="${SERVER_PATH}/tmp"

# collect all passed arguments
POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case ${key} in
        -n|--name)
            NAME="$2"
            shift # past argument
            shift # past value
            ;;
        *)    # unknown option
            POSITIONAL+=("$1") # save it in an array for later
            shift # past argument
            ;;
    esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

echo "starting setup ${NAME}
press CTRL + C to cancel"

echo "creating public directory at ${PUBLIC_PATH}"
mkdir "${PUBLIC_PATH}"
echo "copying static assets (*.js, *.css, images, ...) into public directory"
# TODO: actually doing it
echo "setting permissions to read/write for everybody (rw-rw-rw)"
chmod --recursive rw-rw-rw "${PUBLIC_PATH}"
echo "setting user:group to www-data/www-data"
chown --recursive www-data:www-data "${PUBLIC_PATH}"
echo "creating server directory at ${SERVER_PATH}"
mkdir "${SERVER_PATH}"
echo "creating app directory at ${APP_PATH}"
mkdir "${APP_PATH}"
echo "creating logs directory at ${LOG_PATH}"
mkdir "${LOG_PATH}"
echo "creating conf directory at ${CONF_PATH}"
mkdir "${CONF_PATH}"
echo "creating tmp directory at ${TMP_PATH}"
mkdir "${TMP_PATH}"
echo "writing directories.info"
echo "
BASE_PATH = ${PWD}
PUBLIC_PATH = ${BASE_PATH}/public
ASSETS_PATH = ${PUBLIC_PATH}/assets
SERVER_PATH = ${BASE_PATH}/server
APP_PATH = ${SERVER_PATH}/app
CONF_PATH = ${SERVER_PATH}/conf
LOG_PATH = ${SERVER_PATH}/logs
TMP_PATH = ${SERVER_PATH}/tmp
" > "${SERVER_PATH}/directories.info"
echo "moving docker files"
cp docker-compose.yml "${SERVER_PATH}/docker-compose.yml"
cp docker-run.sh "${SERVER_PATH}/docker-run.sh"
cp Dockerfile-bonham "${SERVER_PATH}/Dockerfile-bonham"

echo "setting permissions to 750 recursively for ${SERVER_PATH}"
chmod --recursive 750 "${SERVER_PATH}"

openssl genrsa -aes256 -out ca-key.pem 4096

echo "setup finished"
