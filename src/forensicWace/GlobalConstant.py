# Null variable messages
noDatabaseSelected = "No database selected"
noReportSelected = "No report selected"
noCertificateSelected = "No certificate selected"
selectWaDatabase = "Select Whatsapp database"
selectDatabaseFile = "Select Database file"
selectOutputPath = "Select output path"

backupDefaultPath = "%APPDATA%"

# Chat list extraction query
queryChatList = "SELECT ZWACHATSESSION.ZPARTNERNAME AS Contact, ZWAPROFILEPUSHNAME.ZPUSHNAME AS UserName, SUBSTRING(ZJID, 1, 12) AS PhoneNumber, (SELECT COUNT(*) FROM ZWAMESSAGE WHERE ZWACHATSESSION.ZSESSIONTYPE == 0 AND ZMESSAGETYPE IN ('0','1','2','3','4','5','7','8','11','14','15','38','39') AND (ZFROMJID = ZWAPROFILEPUSHNAME.ZJID OR ZTOJID = ZWAPROFILEPUSHNAME.ZJID) ) AS NumberOfMessages, datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch') AS MessageDate FROM ZWACHATSESSION LEFT JOIN ZWAMESSAGE ON ZWACHATSESSION.ZLASTMESSAGE = ZWAMESSAGE.Z_PK LEFT JOIN ZWAPROFILEPUSHNAME ON ZWACHATSESSION.ZCONTACTJID = ZWAPROFILEPUSHNAME.ZJID WHERE ZWACHATSESSION.ZSESSIONTYPE == 0 AND ZJID IS NOT NULL GROUP BY ZWACHATSESSION.ZPARTNERNAME HAVING MAX(datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch')) AND NumberOfMessages > 0 ORDER BY CASE WHEN ZWACHATSESSION.ZPARTNERNAME LIKE '+%' THEN 1 ELSE 0 END ASC, ZWACHATSESSION.ZPARTNERNAME"

# Gps data extraction query
queryGpsData = "SELECT CASE WHEN ZWAMESSAGE.ZGROUPMEMBER IS NOT NULL THEN SUBSTRING(ZWAGROUPMEMBER.ZMEMBERJID, 1, 12) WHEN ZWAMESSAGE.ZFROMJID IS NULL THEN 'Database owner'ELSE SUBSTRING(ZWAMESSAGE.ZFROMJID, 1, 12) END	AS Sender, CASE WHEN ZWAMESSAGE.ZTOJID IS NULL AND ZWAMESSAGE.ZGROUPMEMBER IS NULL THEN 'Database owner'WHEN ZWAMESSAGE.ZTOJID IS NULL AND ZWAMESSAGE.ZGROUPMEMBER IS NOT NULL THEN ZWACHATSESSION.ZPARTNERNAME ELSE SUBSTRING(ZWAMESSAGE.ZTOJID, 1, 12) END AS Receiver, datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch') AS MessageDate, ZLATITUDE AS Latitude, ZLONGITUDE AS Longitude FROM ZWAMESSAGE JOIN ZWACHATSESSION ON ZWACHATSESSION.Z_PK = ZWAMESSAGE.ZCHATSESSION LEFT JOIN ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM = ZWAMEDIAITEM.Z_PK LEFT JOIN ZWAGROUPMEMBER ON ZWAMESSAGE.ZGROUPMEMBER = ZWAGROUPMEMBER.Z_PK WHERE ZWAMESSAGE.ZMESSAGETYPE = 5 ORDER BY MessageDate"

# Blocked contacts list extraction query
queryBlockedContacts = "SELECT CASE WHEN ZPUSHNAME IS NULL THEN 'Name not available'ELSE ZPUSHNAME END	AS Name, SUBSTRING(ZWABLACKLISTITEM.ZJID, 1, 12) AS PhoneNumber FROM ZWABLACKLISTITEM LEFT JOIN ZWAPROFILEPUSHNAME ON ZWABLACKLISTITEM.ZJID = ZWAPROFILEPUSHNAME.ZJID"

# Private chat extraction queries
queryPrivateChatCountersPT1 = "SELECT count(case when True then 1 else null end) as TotalMessages, count(case when ZWAMESSAGE.ZMESSAGETYPE = 14 then 1 else null end) as DeletedMessages, count(case when ZWAMESSAGE.ZMESSAGETYPE IN ('1','38','2','39','3','4','5','7','8')  then 1 else null end) as Attachments, count(case when ZWAMESSAGE.ZMESSAGETYPE = 1 OR ZWAMESSAGE.ZMESSAGETYPE = 38 then 1 else null end) as Images, count(case when ZWAMESSAGE.ZMESSAGETYPE = 2 OR ZWAMESSAGE.ZMESSAGETYPE = 39 then 1 else null end) as Videos, count(case when ZWAMESSAGE.ZMESSAGETYPE = 3 then 1 else null end) as Audio, count(case when ZWAMESSAGE.ZMESSAGETYPE = 4 then 1 else null end) as Contacts, count(case when ZWAMESSAGE.ZMESSAGETYPE = 5 then 1 else null end) as Positions, count(case when ZWAMESSAGE.ZMESSAGETYPE = 15 then 1 else null end) as Stickers, count(case when ZWAMESSAGE.ZMESSAGETYPE = 7 then 1 else null end) as Url, count(case when ZWAMESSAGE.ZMESSAGETYPE = 8 then 1 else null end) as File FROM (ZWAMESSAGE JOIN ZWACHATSESSION ON ZWAMESSAGE.ZCHATSESSION = ZWACHATSESSION.Z_PK ) LEFT JOIN ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM=ZWAMEDIAITEM.Z_PK WHERE ZWACHATSESSION.ZCONTACTJID LIKE '%"
queryPrivateChatCountersPT2 = "%' AND ZSESSIONTYPE = 0 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatMessages = "SELECT SUBSTRING(ZFROMJID, 1, 12) as user, ZWAMESSAGE.ZTEXT as text, ZWACHATSESSION.ZPARTNERNAME as ZPARTNERNAME, ZWAMESSAGE.ZMESSAGETYPE as ZMESSAGETYPE, ZWAMESSAGEINFO.ZRECEIPTINFO as dateTimeInfos, datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch') as receiveDateTime, ZMOVIEDURATION as durata, ZLATITUDE as latitudine, ZLONGITUDE as longitudine, ZVCARDNAME as nomeContatto, ZVCARDSTRING as vcardString, SUBSTR(ZWAMEDIAITEM.ZVCARDSTRING, INSTR(ZWAMEDIAITEM.ZVCARDSTRING, '/') + 1) as fileExtension, ZWAMEDIAITEM.ZMEDIALOCALPATH as mediaPath FROM (ZWAMESSAGE JOIN ZWACHATSESSION ON ZWAMESSAGE.ZCHATSESSION = ZWACHATSESSION.Z_PK) LEFT JOIN ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM=ZWAMEDIAITEM.Z_PK LEFT JOIN ZWAMESSAGEINFO ON ZWAMESSAGEINFO.ZMESSAGE = ZWAMESSAGE.Z_PK WHERE ZWACHATSESSION.ZCONTACTJID LIKE '%"
queryPrivateChatMessagesPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZMESSAGETYPE IN ('0','1','2','3','4','5','7','8','11','14','15','38','39') ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatImagesPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND (ZWAMESSAGE.ZMESSAGETYPE = 1 OR ZWAMESSAGE.ZMESSAGETYPE = 38) ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatVideosPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND (ZWAMESSAGE.ZMESSAGETYPE = 2 OR ZWAMESSAGE.ZMESSAGETYPE = 39) ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatAudioPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 3 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatContactsPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 4 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatPositionsPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 5 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatStickersPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 15 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatUrlsPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 7 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryPrivateChatFilesPT2 = "%' AND ZWACHATSESSION.ZGROUPINFO is null AND ZWAMESSAGE.ZMESSAGETYPE = 8 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"


# Group list extraction query
queryGroupList = "SELECT ZPARTNERNAME AS Group_Name, datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch') AS Message_Date, (SELECT COUNT(*) FROM ZWAMESSAGE WHERE ZWAMESSAGE.ZMESSAGETYPE IN ('0','1','38','2','39','3','4','5','7','8','11','14','15','46') AND (ZWAMESSAGE.ZTOJID = ZWACHATSESSION.ZCONTACTJID OR ZWAMESSAGE.ZFROMJID = ZWACHATSESSION.ZCONTACTJID)) AS Number_of_Messages, ZWACHATPUSHCONFIG.ZMUTEDUNTIL AS Is_muted FROM ZWAMESSAGE LEFT JOIN ZWACHATSESSION ON ZWACHATSESSION.ZLASTMESSAGE = ZWAMESSAGE.Z_PK LEFT JOIN ZWAPROFILEPUSHNAME ON ZWACHATSESSION.ZCONTACTJID = ZWAPROFILEPUSHNAME.ZJID LEFT JOIN ZWACHATPUSHCONFIG ON ZWACHATPUSHCONFIG.ZJID = ZWACHATSESSION.ZCONTACTJID WHERE ZSESSIONTYPE = 1 ORDER BY ZWACHATSESSION.ZPARTNERNAME ASC"

queryGroupChatCountersPT1 = "SELECT count(case when ZWAMESSAGE.ZMESSAGETYPE IN ('0','1','38','2','39','3','4','5','7','8','11','14','15','46') then 1 else null end) as totalMessages, count(case when ZWAMESSAGE.ZMESSAGETYPE = 14 then 1 else null end) as deletedMessages, count(case when ZWAMESSAGE.ZMESSAGETYPE IN ('1','38','2','39','3','4','5','7','8')  then 1 else null end) as attachments, count(case when ZWAMESSAGE.ZMESSAGETYPE = 1 OR ZWAMESSAGE.ZMESSAGETYPE = 38 then 1 else null end) as images, count(case when ZWAMESSAGE.ZMESSAGETYPE = 2 OR ZWAMESSAGE.ZMESSAGETYPE = 39 then 1 else null end) as videos, count(case when ZWAMESSAGE.ZMESSAGETYPE = 3 then 1 else null end) as audio, count(case when ZWAMESSAGE.ZMESSAGETYPE = 4 then 1 else null end) as contacts, count(case when ZWAMESSAGE.ZMESSAGETYPE = 5 then 1 else null end) as positions, count(case when ZWAMESSAGE.ZMESSAGETYPE = 15 then 1 else null end) as stickers, count(case when ZWAMESSAGE.ZMESSAGETYPE = 7 then 1 else null end) as url, count(case when ZWAMESSAGE.ZMESSAGETYPE = 8 then 1 else null end) as file FROM ZWAMESSAGE join ZWACHATSESSION on ZWACHATSESSION.Z_PK=ZWAMESSAGE.ZCHATSESSION left JOIN ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM=ZWAMEDIAITEM.Z_PK left join ZWAGROUPMEMBER on ZWAMESSAGE.ZGROUPMEMBER=ZWAGROUPMEMBER.Z_PK WHERE ZWACHATSESSION.ZPARTNERNAME LIKE '%"
queryGroupChatCountersPT2 = "%'ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatIdPT1 = "SELECT ZCONTACTJID FROM ZWACHATSESSION WHERE ZPARTNERNAME LIKE '%"
queryGroupChatIdPT2 = "%';"

queryGroupChatMessages = "SELECT SUBSTRING(ZWAGROUPMEMBER.ZMEMBERJID, 1, 12) as user, CASE WHEN (SELECT CASE WHEN ZWACHATSESSION.ZPARTNERNAME IS NOT NULL THEN ZWACHATSESSION.ZPARTNERNAME ELSE ZWAPROFILEPUSHNAME.ZPUSHNAME END FROM ZWACHATSESSION LEFT JOIN ZWAPROFILEPUSHNAME ON ZWACHATSESSION.ZCONTACTJID = ZWAPROFILEPUSHNAME.ZJID WHERE ZJID LIKE ZWAGROUPMEMBER.ZMEMBERJID) IS NOT NULL THEN (SELECT CASE WHEN ZWACHATSESSION.ZPARTNERNAME IS NOT NULL THEN ZWACHATSESSION.ZPARTNERNAME ELSE ZWAPROFILEPUSHNAME.ZPUSHNAME END FROM ZWACHATSESSION LEFT JOIN ZWAPROFILEPUSHNAME ON ZWACHATSESSION.ZCONTACTJID = ZWAPROFILEPUSHNAME.ZJID WHERE ZJID LIKE ZWAGROUPMEMBER.ZMEMBERJID) WHEN ZWAGROUPMEMBER.ZMEMBERJID IS NULL THEN NULL ELSE 'Name not available' END AS contactName, ZWAMESSAGE.ZTEXT AS text, ZWAMESSAGE.ZMESSAGETYPE AS ZMESSAGETYPE, ZWAMESSAGEINFO.ZRECEIPTINFO as dateTimeInfos, datetime(ZWAMESSAGE.ZMESSAGEDATE + 978307200, 'unixepoch') AS receiveDateTime, ZMOVIEDURATION AS durata, ZLATITUDE AS latitudine, ZLONGITUDE AS longitudine, ZVCARDNAME AS nomeContatto, ZVCARDSTRING AS vcardString, SUBSTR(ZWAMEDIAITEM.ZVCARDSTRING, INSTR(ZWAMEDIAITEM.ZVCARDSTRING, '/') + 1) AS fileExtension, ZWAMEDIAITEM.ZMEDIALOCALPATH AS mediaPath FROM ZWAMESSAGE JOIN ZWACHATSESSION ON ZWACHATSESSION.Z_PK=ZWAMESSAGE.ZCHATSESSION LEFT JOIN ZWAMEDIAITEM ON ZWAMESSAGE.ZMEDIAITEM=ZWAMEDIAITEM.Z_PK LEFT join ZWAGROUPMEMBER ON ZWAMESSAGE.ZGROUPMEMBER=ZWAGROUPMEMBER.Z_PK LEFT JOIN ZWAMESSAGEINFO ON ZWAMESSAGEINFO.ZMESSAGE = ZWAMESSAGE.Z_PK WHERE ZWACHATSESSION.ZPARTNERNAME LIKE '%"
queryGroupChatMessagesPT2 = "%' AND ZMESSAGETYPE IN ('0','1','2','3','4','5','7','8','11','14','15','38','39') ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatImagesPT2 = "%' AND (ZWAMESSAGE.ZMESSAGETYPE = 1 OR ZWAMESSAGE.ZMESSAGETYPE = 38) ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatVideosPT2 = "%' AND (ZWAMESSAGE.ZMESSAGETYPE = 2 OR ZWAMESSAGE.ZMESSAGETYPE = 39) ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatAudioPT2 = "%' AND ZMESSAGETYPE = 3 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatContactsPT2 = "%' AND ZMESSAGETYPE = 4 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatPositionsPT2 = "%' AND ZMESSAGETYPE = 5 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatStickerPT2 = "%' AND ZMESSAGETYPE = 15 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatUrlsPT2 = "%' AND ZMESSAGETYPE = 7 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"

queryGroupChatFilesPT2 = "%' AND ZMESSAGETYPE = 8 ORDER BY ZWAMESSAGE.ZSENTDATE ASC;"


infoNotAvailable = "Information not available"