#url=http://54.245.105.70:8493
url=http://127.0.0.1:5000

curl --data \
"uuid=1&date=2015-12-12 12:00:00&line=9&dir=1&lat=45&lon=-122&mode=on" \
$url/insertScan

curl --data \
"uuid=1&date=2015-12-12 12:30:00&line=9&dir=1&lat=45&lon=-123&mode=off" \
$url/insertScan


curl --data \
"date=2014-12-12 12:00:00&line=200&dir=1&on_stop=8347&off_stop=13134" \
http://127.0.0.1:5000/insertPair



