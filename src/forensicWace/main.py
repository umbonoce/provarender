import webbrowser
import ExtractInformation    # Uncomment this to develop on local. Add to create package to download and install pip
import os
import sys
import GenerateReport    # Uncomment this to develop on local. Add to create package to download and install pip
import Service    # Uncomment this to develop on local. Add to create package to download and install pip
import flask
import GlobalConstant    # Uncomment this to develop on local. Add to create package to download and install pip

from flask import Flask, flash, render_template, session, redirect, url_for, request
import werkzeug

app = Flask(__name__ , static_folder='assets')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

noDbError = 1
noOutPathError = 1
extractionDone = 1

extractedDataList = None

ReportPath = GlobalConstant.noReportSelected
CertificatePath = GlobalConstant.noCertificateSelected
reportStatus = 0

backupPath = GlobalConstant.backupDefaultPath

phoneNumber = ""
ALLOWED_EXTENSIONS = {'sqlite'}
UPLOAD_FOLDER = '//data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def Home():
    session['inputPath'] = GlobalConstant.noDatabaseSelected
    session['outputPath'] = GlobalConstant.noDatabaseSelected
    session['fileName'] = GlobalConstant.noDatabaseSelected
    session['fileSize'] = GlobalConstant.noDatabaseSelected
    session['dbSha256'] = GlobalConstant.noDatabaseSelected
    session['dbMd5']  = GlobalConstant.noDatabaseSelected
    ReportPath = GlobalConstant.noReportSelected
    CertificatePath = GlobalConstant.noCertificateSelected
    reportStatus = 0
    return render_template('index.html', inputPath=session['inputPath'], outputPath=session['outputPath'], fileName=session['fileName'], fileSize=session['fileSize'], dbSha256=session['dbSha256'], dbMd5=session['dbMd5'] , noDbError=noDbError, noOutPathError=noOutPathError)

@app.route('/inputPath', methods = ['GET', 'POST'])
def InputPath():
    global noDbError, noOutPathError

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = werkzeug.utils.secure_filename(f.filename)
            if filename == "":
                session['inputPath'] = GlobalConstant.noDatabaseSelected
            else:
                session['inputPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(session['inputPath'])
                session['outputPath'] = session['inputPath'].rsplit('/', 1)[0] + '/'
                session['fileName'] = session['inputPath'][session['inputPath'].rfind('/') + 1:]
                session['fileSize'] = str(round(Service.GetFileSize(session['inputPath']), 1)) + " MB"
                session['dbSha256'] = Service.CalculateSHA256(session['inputPath'])
                session['dbMd5']  = Service.CalculateMD5(session['inputPath'])
                noDbError = 0
                noOutPathError = 0

    return redirect(url_for('Home'))

@app.route('/outputPath')
def OutputPath():

    global InputPath, OutputPath, noOutPathError

    if session['outputPath'] == "":
        session['outputPath'] = InputPath.rsplit('/', 1)[0] + '/'
    else:
        session['outputPath'] = session['outputPath'] + '/'

    noOutPathError = 0

    return redirect(url_for('Home'))

@app.route('/blockedContact')
def BlockedContact():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetBlockedContacts(InputPath)
        return render_template('blockedContact.html', blockedContactsData=extractedDataList, formatPhoneNumber=Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/blockedContactReport')
def BlockedContactReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        GenerateReport.BlockedContactReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/groupList')
def GroupList():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGroupList(InputPath)
        return render_template('groupList.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/selectGroup')
def SelectGroup():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGroupList(InputPath)
        return render_template('selectGroup.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/groupListReport')
def GroupListReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        global InputPath
        GenerateReport.GroupListReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/chatList')
def ChatList():
    global noDbError, InputPath, extractedDataList

    if noDbError != 1:
        extractedDataList = ExtractInformation.GetChatList(InputPath)
        return render_template('chatList.html', chatListData = extractedDataList, formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocation')
def GpsLocation():
    global noDbError, InputPath, extractedDataList
    if noDbError != 1:
        extractedDataList = ExtractInformation.GetGpsData(InputPath)
        return render_template('gpsLocation.html', gpsData = extractedDataList, formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocationReport')
def GpsLocationReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        GenerateReport.GpsLocations(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route("/insertPhoneNumber", methods=["GET", "POST"])
def InsertPhoneNumber():
    global phoneNumber

    if noDbError != 1:

        if request.method == "POST":
            if request.form["button"] == "del":
                phoneNumber = phoneNumber[:-1]
            else:
                phoneNumber += request.form["button"]

        return render_template("inputPhoneNumber.html", phoneNumber=phoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/privateChat/<mediaType>/<phoneNumber>')
def PrivateChat(mediaType, phoneNumber):
    global noDbError, InputPath

    if noDbError != 1:
        counters, messages = ExtractInformation.GetPrivateChat(InputPath, mediaType, phoneNumber)
        return render_template('privateChat.html', phoneNumber=Service.FormatPhoneNumber(phoneNumber), nonFormattedNumber = phoneNumber, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, originalPhoneNumber = phoneNumber, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/groupChat/<mediaType>/<groupName>')
def GroupChat(mediaType, groupName):
    global noDbError, InputPath

    if noDbError != 1:
        counters, groupId, messages = ExtractInformation.GetGroupChat(InputPath, mediaType, groupName)

        return render_template('groupChat.html', groupName=groupName, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, FormatPhoneNumber=Service.FormatPhoneNumber, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/checkReport')
def CheckReport():
    global ReportPath, CertificatePath, reportStatus, noDbError

    if (ReportPath != GlobalConstant.noReportSelected and CertificatePath != GlobalConstant.noCertificateSelected):
        reportStatus = Service.ReportCheckAuth(ReportPath, CertificatePath)

    return render_template('checkReport.html', reportPath=ReportPath, certificatePath=CertificatePath, reportStatus=reportStatus)

@app.route('/reportPath')
def ReportPath():
    global noDbError
    global ReportPath

    #ReportPath = filedialog.askopenfilename(title=GlobalConstant.selectWaDatabase, filetypes=(("PDF", "*.pdf"), ("All files", "*.*")))
    #rootReportPath.destroy()

    if ReportPath == "":
        ReportPath= GlobalConstant.noReportSelected

    return redirect(url_for('CheckReport'))

@app.route('/certificatePath')
def CertificatePath():
    global noDbError
    global CertificatePath

    #CertificatePath = filedialog.askopenfilename(title=GlobalConstant.selectWaDatabase, filetypes=(("Certificate", "*.tsr"), ("All files", "*.*")))
    #rootCertrPath.destroy()

    if CertificatePath == "":
        CertificatePath= GlobalConstant.noCertificateSelected

    return redirect(url_for('CheckReport'))

@app.route('/calculateDbHash')
def CalculateDbHash():
    global noDbError

    if noDbError != 1:
        global InputPath
        GenerateReport.DbHash(InputPath, OutputPath, fileName)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/chatListReport')
def ChatListReport():
    global noDbError, OutputPath, fileName, extractedDataList

    if noDbError != 1:
        global InputPath
        GenerateReport.ChatListReport(OutputPath, fileName, extractedDataList)
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/availableBackups')
def AvailableBackups():
    global noOutPathError, backupPath, noOutPathError

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    backupList = Service.GetAvailableBackups()
    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=0, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/extractBackup/<deviceSn>/<udid>')
def ExtractBackup(deviceSn, udid):
    global noOutPathError, backupPath, OutputPath, noOutPathError

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if noOutPathError == 0:
        backupList = Service.GetAvailableBackups()
        ExtractInformation.ExtractFullBackup(backupPath, udid, OutputPath)
        Service.RemoveFileWithoutExtension()

    else:
        return redirect(url_for('AvailableBackups'))

    if sys.platform.startswith('win'):
        # Windows
        os.system("start " + OutputPath)
    elif sys.platform.startswith('darwin'):
        # macOS
        os.system("open " + OutputPath)
    # elif sys.platform.startswith('linux'):
        # Linux

    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=1, deviceSn=deviceSn, udid=udid, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/insertPassword/<deviceSn>/<udid>')
def InsertPassword(deviceSn, udid):
    global extractionDone
    extractionDone = 0
    return render_template('insertPassword.html', deviceSn=deviceSn, udid=udid)

@app.route('/extractEncryptedBackup/<deviceSn>/<udid>', methods=["POST"])
def ExtractEncryptedBackup(deviceSn, udid):
    global noOutPathError, backupPath, OutputPath, noOutPathError, extractionDone

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if noOutPathError == 0:
        backupList = Service.GetAvailableBackups()
        if request.method == "POST" and extractionDone == 0:
            backupPsw = request.form["password"]
            ExtractInformation.ExtractEncryptedFullBackup(backupPath, udid, OutputPath, backupPsw)
            Service.RemoveFileWithoutExtension()
            extractionDone = 1
        else:
            return redirect(url_for('AvailableBackups'))

    else:
        return redirect(url_for('AvailableBackups'))

    if sys.platform.startswith('win'):
        # Windows
        os.system("start " + OutputPath)
    elif sys.platform.startswith('darwin'):
        # macOS
        os.system("open " + OutputPath)
    # elif sys.platform.startswith('linux'):
        # Linux

    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=1, deviceSn=deviceSn, udid=udid, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/ExtractionOutPath')
def ExtractionOutPath():

    global InputPath, OutputPath, noOutPathError
    #session['outputPath'] = filedialog.askdirectory(title=GlobalConstant.selectOutputPath)

    if session['outputPath'] == "":
        session['outputPath'] = InputPath.rsplit('/', 1)[0] + '/'
    else:
        session['outputPath'] = session['outputPath'] + '/'

    noOutPathError = 0

    return redirect(url_for('AvailableBackups'))

@app.route('/generetePrivateChatReport/<phoneNumber>')
def GeneretePrivateChatReport(phoneNumber):
    global InputPath, OutputPath, fileName

    counters, messages = ExtractInformation.GetPrivateChat(InputPath, '0', phoneNumber)
    GenerateReport.PrivateChatReport(OutputPath, phoneNumber, messages)
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    GenerateReport.CalculateMediaSHA256(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)
    GenerateReport.CalculateMediaMD5(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)

    return redirect(url_for('PrivateChat', mediaType = 0, phoneNumber=phoneNumber))

@app.route('/genereteGroupChatReport/<groupName>')
def GenereteGroupChatReport(groupName):
    global InputPath, OutputPath, fileName

    counters, groupId, messages = ExtractInformation.GetGroupChat(InputPath, '0', groupName)
    GenerateReport.GroupChatReport(OutputPath, groupName, messages)
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    groupNameNoSpaces = groupName.replace(" ", "")
    groupId = groupId[0]['ZCONTACTJID']
    GenerateReport.CalculateMediaSHA256(basePath + "/assets/Media/" + groupId, OutputPath, groupNameNoSpaces)
    GenerateReport.CalculateMediaMD5(basePath + "/assets/Media/" + groupId, OutputPath, groupNameNoSpaces)

    return redirect(url_for('GroupChat', mediaType = 0, groupName=groupName))

@app.route('/about')
def About():
    return render_template('about.html')

def SetGlobalInOutVar(valueIn, valueOut):
    global InputPath, OutputPath
    InputPath = valueIn
    OutputPath = valueOut

def SetGlobalCheckReportVar(valueRep, valueCert):
    global ReportPath, CertificatePath
    ReportPath = valueRep
    CertificatePath = valueCert

@app.route('/exit')
def Exit():
    global fileName, fileSize, dbSha256, dbMd5, noDbError, noOutPathError, phoneNumber

    session['fileName'] = GlobalConstant.noDatabaseSelected
    session['fileSize'] = GlobalConstant.noDatabaseSelected
    session['dbSha256'] = GlobalConstant.noDatabaseSelected
    session['dbMd5']  = GlobalConstant.noDatabaseSelected
    noDbError = 1
    noOutPathError = 1

    SetGlobalInOutVar(GlobalConstant.selectDatabaseFile, GlobalConstant.selectOutputPath)
    SetGlobalCheckReportVar(GlobalConstant.noReportSelected, GlobalConstant.noCertificateSelected)

    phoneNumber = ""
    return redirect(url_for('Home'))

def main():
    SetGlobalInOutVar(GlobalConstant.selectDatabaseFile, GlobalConstant.selectOutputPath)
    SetGlobalCheckReportVar(GlobalConstant.noReportSelected, GlobalConstant.noCertificateSelected)
    
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    
    # webbrowser.open('http://localhost:5000') 
    # app.run(debug=True, use_reloader=True)     
    # app.run(use_reloader=True) 

if __name__ == '__main__':
    main()
