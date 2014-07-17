url=http://54.245.105.70:8493
#url=http://127.0.0.1:5000


#curl --data \
#"uuid=1&date=2015-12-12 12:00:00&line=9&dir=1&lat=45&lon=-122&mode=on" \
#$url/insertScan

#curl --data \
#"uuid=1&date=2015-12-12 12:30:00&line=9&dir=1&lat=45&lon=-123&mode=off" \
#$url/insertScan


#curl --data \
#"date=2014-12-12 12:00:00&rte=200&dir=1&on_stop=8347&off_stop=13134" \
#$url/insertPair


#user=APRj1YZdQ0A8kiESQlqW7jsETptnG8FPA4iXv-SZAQibWIQcC4kyMX-ttBdp5GALHs1tHLxL_6XR
#pass=APRj1Ya8L-O0RV--PV0abxDDMYFuSg8Dv0dUaAJ0J4CAM-yESW4wpeRM36qWLxBVjwCqWS65oNfb


data=APRj1YZ91cMXugQjSxyRD5mrwr8XkMWKOVQ_rdfIQ_Twb_gw3z_IDDBgGY4pGVDMBQgfsceJkb-G9gMRVS--WU356kGPg5ae3QlbqoAvEV32wWtClQdDlGQ

data=APRj1YZoo6A0248lCU0qW48BSna_7f9sPQrz3JEkTF9OkABqPbfmQiH5hCdOJOu0SSLv4u1eZ-TQMINpJhv-0YuFah2XUTumX6TorpX_Zv0c240MJkbn8XI

wget --post-data="credentials=$data" $url/verifyUser

#curl --data \
#"first=Test&last=User&username=testuser2&password=123456" \
#$url/createUser








