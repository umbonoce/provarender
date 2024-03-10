from io import BytesIO
import webbrowser
import ExtractInformation    # Uncomment this to develop on local. Add to create package to download and install pip
import os
import sys
import GenerateReport    # Uncomment this to develop on local. Add to create package to download and install pip
import Service    # Uncomment this to develop on local. Add to create package to download and install pip
import flask
import GlobalConstant    # Uncomment this to develop on local. Add to create package to download and install pip

from flask import Flask, flash, render_template, send_file, send_from_directory, session, redirect, url_for, request
from datetime import timedelta
from zipfile import ZipFile
import werkzeug

app = Flask(__name__ , static_folder='assets')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

backupPath = GlobalConstant.backupDefaultPath

phoneNumber = ""

UPLOAD_FOLDER = os.path.join(sys.path[0], 'data')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, formato):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in formato

@app.route('/')
def Home():

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    
    if 'fileName' not in session:
        session['inputPath'] = GlobalConstant.noDatabaseSelected
        session['outputPath'] = GlobalConstant.noDatabaseSelected
        session['fileName'] = GlobalConstant.noDatabaseSelected
        session['fileSize'] = GlobalConstant.noDatabaseSelected
        session['dbSha256'] = GlobalConstant.noDatabaseSelected
        session['dbMd5']  = GlobalConstant.noDatabaseSelected     
        session['reportPath'] = GlobalConstant.noReportSelected
        session['certificatePath']  = GlobalConstant.noCertificateSelected
        session['reportStatus']  = 0
        session['noDbError']  = 1  
        session['noOutPathError']  = 1
        session['extractedDataList']  = None

    return render_template('index.html', inputPath=session['inputPath'], outputPath=session['outputPath'], fileName=session['fileName'], fileSize=session['fileSize'], dbSha256=session['dbSha256'], dbMd5=session['dbMd5'], noDbError=session['noDbError'], noOutPathError=session['noOutPathError'])

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
        if f and allowed_file(f.filename, {'sqlite'}):
            filename = werkzeug.utils.secure_filename(f.filename)
            if filename == "":
                session['inputPath'] = GlobalConstant.noDatabaseSelected
            else:
                session['inputPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(session['inputPath'])
                session['outputPath'] = UPLOAD_FOLDER
                session['fileName'] = session['inputPath'].split('\\')[-1]
                session['fileSize'] = str(round(Service.GetFileSize(session['inputPath']), 1)) + " MB"
                session['dbSha256'] = Service.CalculateSHA256(session['inputPath'])
                session['dbMd5']  = Service.CalculateMD5(session['inputPath'])
                session['noDbError']  = 0
                session['noOutPathError']  = 0

    return redirect(url_for('Home'))

@app.route('/outputPath', methods = ['GET', 'POST'])
def OutputPath():

    if session['outputPath'] == "":
        session['outputPath'] = session['inputPath'] .rsplit('/', 1)[0] + '/'
    else:
        session['outputPath'] = session['outputPath'] + '/'

    session['noOutPathError']  = 0

    return redirect(url_for('Home'))

@app.route('/blockedContact')
def BlockedContact():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetBlockedContacts(session['inputPath'])
        return render_template('blockedContact.html', blockedContactsData=session['extractedDataList'], formatPhoneNumber=Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/blockedContactReport', methods = ['GET', 'POST'])
def BlockedContactReport():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetBlockedContacts(session['inputPath'])
        outputFile, certificateFile = GenerateReport.BlockedContactReport(UPLOAD_FOLDER, session['fileName'], session['extractedDataList'])
        return send_file([outputFile, certificateFile], as_attachment=True)
    else:
        return redirect(url_for('Home'))

@app.route('/groupList')
def GroupList():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetGroupList(session['inputPath'])
        return render_template('groupList.html', chatListData = session['extractedDataList'])
    else:
        return redirect(url_for('Home'))

@app.route('/selectGroup')
def SelectGroup():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetGroupList(session['inputPath'])
        return render_template('selectGroup.html', chatListData = session['extractedDataList'])
    else:
        return redirect(url_for('Home'))

@app.route('/groupListReport', methods = ['GET', 'POST'])
def GroupListReport():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetGroupList(session['inputPath'])
        outputFile, certificateFile = GenerateReport.GroupListReport(UPLOAD_FOLDER, session['fileName'], session['extractedDataList'])
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile)
            newzip.write(certificateFile)
        
        memory_file.seek(0)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, attachment_filename="groupListReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/chatList')
def ChatList():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetChatList(session['inputPath'])
        return render_template('chatList.html', chatListData = session['extractedDataList'], formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocation')
def GpsLocation():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetGpsData(session['inputPath'])
        return render_template('gpsLocation.html', gpsData = session['extractedDataList'], formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocationReport')
def GpsLocationReport():

    if session['noDbError']  != 1:
        session['extractedDataList']  = ExtractInformation.GetGpsData(session['inputPath'])
        outputFile, certificateFile = GenerateReport.GpsLocations(UPLOAD_FOLDER, session['fileName'], session['extractedDataList'])
        return send_file([outputFile, certificateFile], as_attachment=True)
    else:
        return redirect(url_for('Home'))

@app.route("/insertPhoneNumber", methods=["GET", "POST"])
def InsertPhoneNumber():
    global phoneNumber

    if session['noDbError']  != 1:

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

    if session['noDbError']  != 1:
        counters, messages = ExtractInformation.GetPrivateChat(session['inputPath'], mediaType, phoneNumber)
        return render_template('privateChat.html', phoneNumber=Service.FormatPhoneNumber(phoneNumber), nonFormattedNumber = phoneNumber, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, originalPhoneNumber = phoneNumber, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/groupChat/<mediaType>/<groupName>')
def GroupChat(mediaType, groupName):

    if session['noDbError']  != 1:
        counters, groupId, messages = ExtractInformation.GetGroupChat(session['inputPath'], mediaType, groupName)

        return render_template('groupChat.html', groupName=groupName, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, FormatPhoneNumber=Service.FormatPhoneNumber, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/checkReport')
def CheckReport():
    global CertificatePath

    if (session['reportPath'] != GlobalConstant.noReportSelected and session['certificatePath']  != GlobalConstant.noCertificateSelected):
        session['reportStatus']  = Service.ReportCheckAuth(session['reportPath'], session['certificatePath'])

    return render_template('checkReport.html', reportPath=session['reportPath'], certificatePath=session['certificatePath'], reportStatus=session['reportStatus'])

@app.route('/reportPath', methods = ['GET', 'POST'])
def ReportPath():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']
        
        if f and allowed_file(f.filename, {'pdf'}):
            filename = werkzeug.utils.secure_filename(f.filename)
            if filename == "":
                session['reportPath'] = GlobalConstant.noDatabaseSelected
            else:
                session['reportPath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(session['reportPath'])       


    return redirect(url_for('CheckReport'))

@app.route('/certificatePath', methods = ['GET', 'POST'])
def CertificatePath():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']
        
        if f and allowed_file(f.filename, {'tsr'}):
            filename = werkzeug.utils.secure_filename(f.filename)
            if filename == "":
                session['certificatePath'] = GlobalConstant.noDatabaseSelected
            else:
                session['certificatePath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(session['certificatePath'])

    return redirect(url_for('CheckReport'))

@app.route('/calculateDbHash')
def CalculateDbHash():

    if session['noDbError']  != 1:
        global InputPath
        GenerateReport.DbHash(session['inputPath'], session['outputPath'], session['fileName'])
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/chatListReport')
def ChatListReport():

    if session['noDbError']  != 1:
        GenerateReport.ChatListReport(session['outputPath'], session['fileName'], session['extractedDataList'])
        return redirect(url_for('Home'))
    else:
        return redirect(url_for('Home'))

@app.route('/availableBackups')
def AvailableBackups():

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    backupList = Service.GetAvailableBackups()
    return render_template('availableBackup.html', backupList=backupList, backupPath=backupPath, extractionStatus=0, outputPath=OutputPath, noOutPathError=noOutPathError)

@app.route('/extractBackup/<deviceSn>/<udid>')
def ExtractBackup(deviceSn, udid):

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if session['noOutPathError']  == 0:
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
    session['extractionDone '] = 0
    return render_template('insertPassword.html', deviceSn=deviceSn, udid=udid)

@app.route('/extractEncryptedBackup/<deviceSn>/<udid>', methods=["POST"])
def ExtractEncryptedBackup(deviceSn, udid):

    backupPath = os.path.expandvars(GlobalConstant.backupDefaultPath)
    backupPath = backupPath.replace("\\", "/")

    if session['noOutPathError']  == 0:
        backupList = Service.GetAvailableBackups()
        if request.method == "POST" and session['extractionDone '] == 0:
            backupPsw = request.form["password"]
            ExtractInformation.ExtractEncryptedFullBackup(backupPath, udid, OutputPath, backupPsw)
            Service.RemoveFileWithoutExtension()
            session['extractionDone '] = 1
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

    #session['outputPath'] = filedialog.askdirectory(title=GlobalConstant.selectOutputPath)

    if session['outputPath'] == "":
        session['outputPath'] = InputPath.rsplit('/', 1)[0] + '/'
    else:
        session['outputPath'] = session['outputPath'] + '/'

    session['noOutPathError']  = 0

    return redirect(url_for('AvailableBackups'))

@app.route('/generetePrivateChatReport/<phoneNumber>')
def GeneretePrivateChatReport(phoneNumber):

    counters, messages = ExtractInformation.GetPrivateChat(InputPath, '0', phoneNumber)
    GenerateReport.PrivateChatReport(OutputPath, phoneNumber, messages)
    basePath = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
    GenerateReport.CalculateMediaSHA256(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)
    GenerateReport.CalculateMediaMD5(basePath + "/assets/Media/" + phoneNumber + "@s.whatsapp.net", OutputPath, phoneNumber)

    return redirect(url_for('PrivateChat', mediaType = 0, phoneNumber=phoneNumber))

@app.route('/genereteGroupChatReport/<groupName>')
def GenereteGroupChatReport(groupName):
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
    CertificatePath  = valueCert

@app.route('/exit')
def Exit():
    
    session['inputPath'] = GlobalConstant.noDatabaseSelected
    session['outputPath'] = GlobalConstant.noDatabaseSelected
    session['fileName'] = GlobalConstant.noDatabaseSelected
    session['fileSize'] = GlobalConstant.noDatabaseSelected
    session['dbSha256'] = GlobalConstant.noDatabaseSelected
    session['dbMd5']  = GlobalConstant.noDatabaseSelected
    session['noDbError']  = 1
    session['noOutPathError']  = 1

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

if __name__ == '__main__':
    main()
