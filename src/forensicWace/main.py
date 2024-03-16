from io import BytesIO
import webbrowser

from werkzeug.utils import secure_filename
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
        session['fileName'] = GlobalConstant.noDatabaseSelected
        session['fileSize'] = GlobalConstant.noDatabaseSelected
        session['dbSha256'] = GlobalConstant.noDatabaseSelected
        session['dbMd5']  = GlobalConstant.noDatabaseSelected     
        session['reportPath'] = GlobalConstant.noReportSelected
        session['certificatePath']  = GlobalConstant.noCertificateSelected
        session['reportStatus']  = 0
        session['noDbError']  = 1  
        session['noOutPathError']  = 1
        extractedDataList  = None

    return render_template('index.html', inputPath=session['inputPath'], outputPath=app.config['UPLOAD_FOLDER'], fileName=session['fileName'], fileSize=session['fileSize'], dbSha256=session['dbSha256'], dbMd5=session['dbMd5'], noDbError=session['noDbError'], noOutPathError=session['noOutPathError'])

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
                session['fileName'] = os.path.basename(session['inputPath'])
                session['fileSize'] = str(round(Service.GetFileSize(session['inputPath']), 1)) + " MB"
                session['dbSha256'] = Service.CalculateSHA256(session['inputPath'])
                session['dbMd5']  = Service.CalculateMD5(session['inputPath'])
                session['noDbError']  = 0
                session['noOutPathError']  = 0

    return redirect(url_for('Home'))

# @app.route('/outputPath', methods = ['GET', 'POST'])
# def OutputPath():

#     if app.config['UPLOAD_FOLDER'] == "":
#         app.config['UPLOAD_FOLDER'] = session['inputPath'].rsplit('/', 1)[0] + '/'
#     else:
#         app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] + '/'

#     session['noOutPathError']  = 0

#     return redirect(url_for('Home'))

@app.route('/data/<path:path>')
def ServeMedia(path):
    return send_from_directory('data', path)

@app.route('/blockedContact')
def BlockedContact():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']
        extractedDataList = ExtractInformation.GetBlockedContacts(inputPath)
        return render_template('blockedContact.html', blockedContactsData=extractedDataList , formatPhoneNumber=Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/blockedContactReport', methods = ['GET', 'POST'])
def BlockedContactReport():

    if session['noDbError']  != 1:
        extractedDataList  = ExtractInformation.GetBlockedContacts(session['inputPath'])
        outputFile, certificateFile = GenerateReport.BlockedContactReport(app.config['UPLOAD_FOLDER'], session['fileName'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="blockedContacReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/groupList')
def GroupList():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']
        extractedDataList = ExtractInformation.GetGroupList(inputPath)
        return render_template('groupList.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/selectGroup')
def SelectGroup():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']
        extractedDataList  = ExtractInformation.GetGroupList(inputPath)
        return render_template('selectGroup.html', chatListData = extractedDataList)
    else:
        return redirect(url_for('Home'))

@app.route('/groupListReport', methods = ['GET', 'POST'])
def GroupListReport():

    if session['noDbError']  != 1:
        extractedDataList  = ExtractInformation.GetGroupList(session['inputPath'])
        outputFile, certificateFile = GenerateReport.GroupListReport(app.config['UPLOAD_FOLDER'], session['fileName'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="groupListReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/chatList')
def ChatList():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        extractedDataList = ExtractInformation.GetChatList(inputPath)
        return render_template('chatList.html', chatListData = extractedDataList , formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocation')
def GpsLocation():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        extractedDataList = ExtractInformation.GetGpsData(inputPath)
        return render_template('gpsLocation.html', gpsData = extractedDataList , formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocationReport')
def GpsLocationReport():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        extractedDataList  = ExtractInformation.GetGpsData(inputPath)
        outputFile, certificateFile = GenerateReport.GpsLocations(app.config['UPLOAD_FOLDER'], session['fileName'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="gpsLocationReportExtraction.zip")
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

@app.route('/privateChat/<mediaType>/<phoneNumber>' , methods = ['GET', 'POST'])
def PrivateChat(mediaType, phoneNumber):

    if session['noDbError']  != 1:
        inputPath = session['inputPath']               
        counters, messages = ExtractInformation.GetPrivateChat(inputPath, mediaType, phoneNumber)
        return render_template('privateChat.html', phoneNumber=Service.FormatPhoneNumber(phoneNumber), nonFormattedNumber = phoneNumber, counters = counters, messages = messages, str=str, vcardTelExtractor = Service.VcardTelExtractor, originalPhoneNumber = phoneNumber, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, GetUserProfilePicImage = Service.GetUserProfilePicImage)
    else:
        return redirect(url_for('Home'))

@app.route('/groupChat/<mediaType>/<groupName>', methods = ['GET', 'POST'])
def GroupChat(mediaType, groupName):

    if request.method =='POST':
        files = request.files.getlist("file")
        
        for file in files:
            path = os.path.dirname(file.filename)
            basePath = os.path.join(app.config['UPLOAD_FOLDER'], "Media")
            basePath = os.path.join(app.config['UPLOAD_FOLDER'], path)
            if not os.path.exists(basePath):
                os.makedirs(basePath, exist_ok=True)          
            file.save(os.path.join(basePath,secure_filename(file.filename)))

    if session['noDbError']  != 1:
        inputPath = session['inputPath']               
        counters, groupId, messages = ExtractInformation.GetGroupChat(inputPath, mediaType, groupName)
        groupId = groupId[0]['ZCONTACTJID']

        return render_template('groupChat.html', groupName=groupName, counters = counters, messages = messages, groupId = groupId, str=str, vcardTelExtractor = Service.VcardTelExtractor, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, FormatPhoneNumber=Service.FormatPhoneNumber, GetUserProfilePicImage = Service.GetUserProfilePicImage)
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
        outputFile, certificateFile = GenerateReport.DbHash(session['inputPath'], app.config['UPLOAD_FOLDER'], session['fileName'])
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name= session['inputPath'] + "-DbHash.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/chatListReport')
def ChatListReport():

    if session['noDbError']  != 1:
        extractedDataList = ExtractInformation.GetChatList(session['inputPath'])
        outputFile, certificateFile = GenerateReport.ChatListReport(app.config['UPLOAD_FOLDER'], session['fileName'], extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name="chatListReportExtraction.zip")
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

# @app.route('/ExtractionOutPath')
# def ExtractionOutPath():
#     if app.config['UPLOAD_FOLDER'] == "":
#         app.config['UPLOAD_FOLDER'] = InputPath.rsplit('/', 1)[0] + '/'
#     else:
#         app.config['UPLOAD_FOLDER'] = app.config['UPLOAD_FOLDER'] + '/'

#     session['noOutPathError']  = 0

#     return redirect(url_for('AvailableBackups'))

@app.route('/generetePrivateChatReport/<phoneNumber>')
def GeneretePrivateChatReport(phoneNumber):

    counters, messages = ExtractInformation.GetPrivateChat(session['inputPath'], '0', phoneNumber)
    GenerateReport.PrivateChatReport(app.config['UPLOAD_FOLDER'], phoneNumber, messages)
    
    basePath = app.config['UPLOAD_FOLDER']
    GenerateReport.CalculateMediaSHA256(os.path.join( basePath, phoneNumber + "@s.whatsapp.net"), os.path.join(basePath, phoneNumber), phoneNumber)
    GenerateReport.CalculateMediaMD5(os.path.join( basePath, phoneNumber + "@s.whatsapp.net"), os.path.join(basePath, phoneNumber), phoneNumber)

    return redirect(url_for('PrivateChat', mediaType = 0, phoneNumber=phoneNumber))

@app.route('/genereteGroupChatReport/<groupName>')
def GenereteGroupChatReport(groupName):

    groupNameNoSpaces = groupName.replace(" ", "")

    counters, groupId, messages = ExtractInformation.GetGroupChat(session['inputPath'], '0', groupName)
    report, certificate = GenerateReport.GroupChatReport(os.path.join(app.config['UPLOAD_FOLDER'], groupNameNoSpaces), groupName, messages)
    
    basePath = app.config['UPLOAD_FOLDER']
    groupId = groupId[0]['ZCONTACTJID']
    sha = GenerateReport.CalculateMediaSHA256(os.path.join(basePath, groupId), os.path.join(basePath, groupNameNoSpaces), groupNameNoSpaces)
    md5 = GenerateReport.CalculateMediaMD5(os.path.join(basePath, groupId), os.path.join(basePath, groupNameNoSpaces), groupNameNoSpaces)

    memory_file = BytesIO()

    with ZipFile(memory_file, "w") as newzip:
        newzip.write(report, os.path.basename(report))
        newzip.write(certificate, os.path.basename(certificate))
        newzip.write(sha, os.path.basename(sha))
        newzip.write(md5, os.path.basename(md5))
        mediaPath = os.path.join(basePath, groupId)
        if os.path.exists(mediaPath):  
            for dirpath, dirnames, medias in os.walk(mediaPath):  
                for media in medias:
                    path= os.path.join(dirpath, media)
                    newzip.write(path, os.path.join('Media', os.path.basename(media)))
                    
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name= groupNameNoSpaces + ".zip")


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
    # app.run(debug=True, use_reloader=False)     

if __name__ == '__main__':
    main()
