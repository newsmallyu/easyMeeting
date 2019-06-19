import dateutil.parser
import pytz
import time
from datetime import datetime

import json
import urllib.request as request
import pymysql

def connectDatabase():
    connect = pymysql.Connect(
        host='172.16.41.85',
        port=8306,
        user='root',
        passwd='123456',
        db='newegg',
        charset='utf8'
    )
    return (connect, connect.cursor())

def handleEsJson():
    conn, cursor = connectDatabase()
    count_success = 0
    s = open('C:\\Users\\ay05\\Desktop\\success4.txt', 'w+')
    f = open('C:\\Users\\ay05\\Desktop\\failure4.txt', 'w+')
    with open('C:\\Users\\ay05\\Desktop\\new_4.json') as jsonfile:
        data = json.load(jsonfile)
        for item in data['buckets']:
            result = item.get('key')
            try:
                sendToSql(conn, cursor, result)
                s.write(str(result) + "\n")
                count_success = count_success +1
                if count_success>500:
                    s.flush()
                    count_success=0
            except Exception:
                print(Exception)
                f.write(str(result) + "\n")
                f.flush()
            continue
    s.close()
    f.close()
    conn.close()




def timeConvert(datestring):
    local_time = dateutil.parser.parse(datestring).astimezone(pytz.timezone('Asia/Shanghai'))  # 解析string 并转换为北京时区
    da = datetime.strftime(local_time, '%Y-%m-%d %H:%M:%S')  # 将datetime转换为string
    return da
def strOrNot(data):
    if data == None:
        return None
    else:
        return str(data).lower()

def utctimeConvert(datestring):
    if datestring == None:
        return
    else:
        local_time = dateutil.parser.parse(datestring)  # 直接输出utc时间
        da = datetime.strftime(local_time, '%Y-%m-%d %H:%M:%S')  # 将datetime转换为string
        return da

def sendToSql(conn, cursor, result):
    req = request.Request("http://apis.newegg.org/whois?domain=" + result)
    req.add_header('Content-Type', 'application/json')
    response = request.urlopen(req)
    jsonBody = json.loads(response.read())
    cursor.execute("""INSERT INTO whois (DomainName,
            NameServer,
            RegistrarUrl,
            Registrar,
            RegistrantOrganization,
            RegistrarAbuseContactEmail,
            RegistrarWhoisServer,
            RegistrarAbuseContactPhone,
            RegistrantCountry,
            CreationDate,
            UpdatedDate,
            RegistryExpiryDate,
            RegistrarIanaId,
            Dnssec,
            RegistrantState,
            LastUpdateOfWhoisDatabase,
            RegistryDomainId,
            LocationCyc,
            LocationCyn,
            LocationRegion,
            LocationPcode,
            LocationLat,
            LocationLon,
            LocationOrg,
            LocationCity,
            LookupA,
            LookupIP,
            LookupMX,
            LookupNS) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (
                       strOrNot(jsonBody["domainName"] if "domainName" in jsonBody else result),
                       strOrNot(jsonBody["nameServer"] if "nameServer" in jsonBody else None),
                       strOrNot(jsonBody["registrarUrl"] if "registrarUrl" in jsonBody else None),
                       strOrNot(jsonBody["registrar"] if "registrar" in jsonBody else None),
                       strOrNot(jsonBody["registrantOrganization"] if "registrantOrganization" in jsonBody else None),
                       strOrNot(jsonBody[
                                    "registrarAbuseContactEmail"] if "registrarAbuseContactEmail" in jsonBody else None),
                       strOrNot(jsonBody["registrarWhoisServer"] if "registrarWhoisServer" in jsonBody else None),
                       strOrNot(jsonBody[
                                    "registrarAbuseContactPhone"] if "registrarAbuseContactPhone" in jsonBody else None),
                       strOrNot(jsonBody["registrantCountry"] if "registrantCountry" in jsonBody else None),
                       utctimeConvert(jsonBody["creationDate"] if "creationDate" in jsonBody else None),
                       utctimeConvert(jsonBody["updatedDate"] if "updatedDate" in jsonBody else None),
                       utctimeConvert(jsonBody["registryExpiryDate"] if "registryExpiryDate" in jsonBody else None),
                       strOrNot(jsonBody["registrarIanaId"] if "registrarIanaId" in jsonBody else None),
                       strOrNot(jsonBody["dnssec"] if "dnssec" in jsonBody else None),
                       strOrNot(
                           jsonBody["registrantState/province"] if "registrantState/province" in jsonBody else None),
                       utctimeConvert(
                           jsonBody["lastUpdateOfWhoisDatabase"] if "lastUpdateOfWhoisDatabase" in jsonBody else None),
                       strOrNot(jsonBody["registryDomainId"] if "registryDomainId" in jsonBody else None),
                       strOrNot(jsonBody["location.cyc"] if "location.cyc" in jsonBody else None),
                       strOrNot(jsonBody["location.cyn"] if "location.cyn" in jsonBody else None),
                       strOrNot(jsonBody["location.region"] if "location.region" in jsonBody else None),
                       strOrNot(jsonBody["location.pcode"] if "location.pcode" in jsonBody else None),
                       strOrNot(jsonBody["location.lat"] if "location.lat" in jsonBody else None),
                       strOrNot(jsonBody["location.lon"] if "location.lon" in jsonBody else None),
                       strOrNot(jsonBody["location.org"] if "location.org" in jsonBody else None),
                       strOrNot(jsonBody["location.city"] if "location.city" in jsonBody else None),
                       strOrNot(jsonBody["Lookup.A"] if "Lookup.A" in jsonBody else None),
                       strOrNot(jsonBody["Lookup.IP"] if "Lookup.IP" in jsonBody else None),
                       strOrNot(jsonBody["Lookup.MX"] if "Lookup.MX" in jsonBody else None),
                       strOrNot(jsonBody["Lookup.NS"] if "Lookup.NS" in jsonBody else None)))
    conn.commit()

def timestamp_utc_now(datestring):
    timeArray = time.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
    timestamp = time.mktime(timeArray)
    print(int(timestamp*1000))



if __name__ == '__main__':
    handleEsJson()
