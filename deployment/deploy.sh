clear

if [[ $# -eq 0 ]]; then
	echo "No arguments supplied - valid values are 'DEV' or 'PROD'"
	exit
fi

echo 'Deploying Docker Images'


echo 'Copy files to Flask Docker deploy directory'
cp ../source/anaplanapi.py ./flask/
cp ../source/automationhelper.py ./flask/
cp ../source/getvar.py ./flask/
cp ../source/managed-integration-services.py ./flask/
cp ../source/sendmail.py ./flask/

cp ../runtime/anaplanconnect/AnaplanClient.sh ./flask/
cp ../runtime/anaplanconnect/anaplan-connect-1-3-3-3.jar ./flask/
cp -R ../runtime/anaplanconnect/lib ./flask/lib
cp ../runtime/jre/jre-8u112-linux-x64.tar.gz ./flask/

if [[ $1='DEV' ]]; then
	cp ../certificates/dev/*.cer ./flask
elif [[ $1='PROD' ]]; then
	cp ../certificates/prod/*.cer ./flask
fi

docker build -t flask-server-mis flask/.
docker run -d --rm --name=flask-server-mis-google -p 5001:5001 -e ENV=$1 flask-server-mis

rm ./flask/*.py
rm ./flask/jre-8u112-linux-x64.tar.gz
rm ./flask/anaplan-connect-1-3-3-3.jar
rm ./flask/AnaplanClient.sh
rm -rf ./flask/lib
rm ./flask/*.cer