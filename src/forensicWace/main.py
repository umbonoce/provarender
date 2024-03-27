from io import BytesIO
import shutil
import time
import uuid
import webbrowser
import hashlib
import ExtractInformation, GenerateReport, GlobalConstant, Service
import os
import sys
from flask import Flask, flash, render_template, send_file, send_from_directory, session, redirect, url_for, request
from datetime import timedelta
from zipfile import ZipFile
from werkzeug import utils
from cryptography.fernet import Fernet

app = Flask(__name__ , static_folder='assets')
app.secret_key = os.getenv('SECRET_KEY', b'_5#y2L"F4Q8z\n\xec]/') 

phoneNumber, dateBegin, dateEnd, searchKey = "", "null", "null", "null"

UPLOAD_FOLDER = os.path.join(sys.path[0], 'data')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, formato):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in formato

def encrypt_database(file):
    file.seek(0)
    with open(session['inputPath'], 'wb') as encrypted_file:
        while True:
            original = file.read(GlobalConstant.BLOCKSIZE)
            if not original:
                break
            fernet = Fernet(session['session_key'])
            encrypted = fernet.encrypt(original)
            l = len(encrypted)
            l_bytes = l.to_bytes(GlobalConstant.ENCRYPTED_HEADER_LENGTH, 'big')
            encrypted_file.write(l_bytes)
            encrypted_file.write(encrypted)
            
@app.route('/')
def Home():

    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    
    if 'fileName' not in session:
        session['session_key'] = Fernet.generate_key()
        session['inputPath'] = GlobalConstant.noDatabaseSelected
        session['serialDb'] = GlobalConstant.noDatabaseSelected
        session['fileName'] = GlobalConstant.noDatabaseSelected
        session['fileSize'] = GlobalConstant.noDatabaseSelected
        session['dbSha256'] = GlobalConstant.noDatabaseSelected
        session['dbMd5']  = GlobalConstant.noDatabaseSelected     
        session['reportPath'] = GlobalConstant.noReportSelected
        session['certificatePath']  = GlobalConstant.noCertificateSelected
        session['dateBegin'] = "null"
        session['dateEnd'] = "null"
        session['searchKey'] = "null"
        session['messages'] = "null"
        session['reportStatus']  = 0
        session['noDbError']  = 1  
        session['noOutPathError']  = 1
        session['extractedDataList'] = None
        
        for i in os.listdir(app.config['UPLOAD_FOLDER']): 
            # get the location of the file 
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], i) 
            # file_time is the time when the file is modified
            file_time = os.stat(file_location).st_mtime 
  
            if(file_time < time.time() - 1800): 
                print(f" Delete : {i}")
                if os.path.isfile(file_location):
                    os.remove(file_location) 

    return render_template('index.html', inputPath=session['serialDb'], outputPath=app.config['UPLOAD_FOLDER'], fileName=session['fileName'], fileSize=session['fileSize'], dbSha256=session['dbSha256'], dbMd5=session['dbMd5'], noDbError=session['noDbError'], noOutPathError=session['noOutPathError'])

@app.route('/loading-<nomePagina>')
def Loading(nomePagina):
    return render_template("loading.html", NomePagina = nomePagina)

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
            filename = utils.secure_filename(f.filename)
            if filename == "":
                session['inputPath'] = GlobalConstant.noDatabaseSelected
            else:
                
                original = f.read()                
                session['dbMd5'] = hashlib.md5(original).hexdigest()
                session['dbSha256'] = hashlib.sha256(original).hexdigest()         
                session['fileSize'] = str(round( len(original) / (1024 * 1024) , 2 )) + ' MB'
                session['serialDb'] = str(uuid.uuid4())
                session['inputPath'] = os.path.join(app.config['UPLOAD_FOLDER'], session['serialDb'])                      
                encrypt_database(f)
                f.save(session['inputPath'] + '.sqlite')
                session['fileName'] = filename
                session['noDbError']  = 0
                session['noOutPathError']  = 0

    return redirect(url_for('Home'))

@app.route('/data/<path:path>')
def ServeMedia(path):
    return send_from_directory('data', path)

@app.route('/blockedContact')
def BlockedContact():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']
        session['extractedDataList'] = ExtractInformation.GetBlockedContacts(inputPath)
        return render_template('blockedContact.html', blockedContactsData = session['extractedDataList'], formatPhoneNumber=Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/blockedContactReport', methods = ['GET', 'POST'])
def BlockedContactReport():

    if session['noDbError']  != 1:
        extractedDataList  = ExtractInformation.GetBlockedContacts(session['inputPath'])
        outputFile, certificateFile = GenerateReport.BlockedContactReport(app.config['UPLOAD_FOLDER'], session['serialDb'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        
        if os.path.exists(outputFile):
            os.remove(outputFile)
        if os.path.exists(certificateFile):
            os.remove(certificateFile)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=session['serialDb'] + "-blockedContacReportExtraction.zip")
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
        outputFile, certificateFile = GenerateReport.GroupListReport(app.config['UPLOAD_FOLDER'], session['serialDb'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        
        if os.path.exists(outputFile):
            os.remove(outputFile)
        if os.path.exists(certificateFile):
            os.remove(certificateFile)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=session['serialDb'] + "-groupListReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/chatList')
def ChatList():
    
    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        extractedDataList = ExtractInformation.GetChatList(inputPath)
        return render_template('chatList.html', chatListData = extractedDataList, formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocation')
def GpsLocation():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        session['extractedDataList'] = ExtractInformation.GetGpsData(inputPath)
        return render_template('gpsLocation.html', gpsData = session['extractedDataList'] , formatPhoneNumber = Service.FormatPhoneNumber)
    else:
        return redirect(url_for('Home'))

@app.route('/gpsLocationReport')
def GpsLocationReport():

    if session['noDbError']  != 1:
        inputPath = session['inputPath']        
        extractedDataList  = ExtractInformation.GetGpsData(inputPath)
        outputFile, certificateFile = GenerateReport.GpsLocations(app.config['UPLOAD_FOLDER'], session['serialDb'],extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        
        if os.path.exists(outputFile):
            os.remove(outputFile)
        if os.path.exists(certificateFile):
            os.remove(certificateFile)

        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=session['serialDb'] + "-gpsLocationReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route("/insertPhoneNumber", methods=["GET", "POST"])
def InsertPhoneNumber():
    global phoneNumber, dateBegin, dateEnd, searchKey 
    
    if session['noDbError']  != 1:

        if request.method == "POST":
            if "phoneNumber" in request.form:
                phoneNumber = request.form["phoneNumber"] 
                
            if "dateBegin" in request.form:
                dateBegin = request.form["dateBegin"] 
               
            if "dateEnd" in request.form:
                dateEnd = request.form["dateEnd"] 
                       
            if "searchKey" in request.form:
                searchKey = request.form["searchKey"] 

            if "button" in request.form:            
                if request.form["button"] == "del":
                    phoneNumber = phoneNumber[:-1]
                else:
                    phoneNumber += request.form["button"]


        return render_template("inputPhoneNumber.html", phoneNumber=phoneNumber, dateBegin=dateBegin, dateEnd = dateEnd, searchKey=searchKey)
    else:
        return redirect(url_for('Home'))

@app.route('/resetFilters')
def ResetFilters():
                
    session['dateBegin'] = "null"
               
    session['dateEnd']  = "null"
                       
    session['searchKey'] = "null"
    
    return redirect("/".join(request.referrer.split("/")[:6]))

@app.route('/privateChat/<mediaType>/<phoneNumber>' , methods = ['GET', 'POST'])
def PrivateChat(mediaType, phoneNumber):
        
    if request.method =='POST':
        
        if "dateBegin" in request.form:
            session['dateBegin'] = request.form["dateBegin"] 
               
        if "dateEnd" in request.form:
            session['dateEnd']  = request.form["dateEnd"] 
                       
        if "searchKey" in request.form:
            session['searchKey'] = request.form["searchKey"]
            
        if "file" in request.files:

            files = request.files.getlist("file")
        
            for file in files:
                path = os.path.dirname(file.filename)
                filename = os.path.basename(file.filename)
                basePath = os.path.join(app.config['UPLOAD_FOLDER'], "Media")
                basePath = os.path.join(basePath, path)
                if not os.path.exists(basePath):
                    os.makedirs(basePath, exist_ok=True)          
                file.save(os.path.join(basePath, utils.secure_filename(filename) ))
            
    if session['noDbError']  != 1:
        return redirect(url_for('PrivateChatFilters', mediaType=mediaType, phoneNumber=phoneNumber, dateBegin=session['dateBegin'], dateEnd=session['dateEnd'], searchKey=session['searchKey']))
    else:
        return redirect(url_for('Home'))

@app.route('/privateChat/<mediaType>/<phoneNumber>/<dateBegin>_<dateEnd>_<searchKey>')
def PrivateChatFilters(mediaType, phoneNumber, dateBegin, dateEnd, searchKey):
            
    if session['noDbError']  != 1:
        session['dateBegin'] = dateBegin           
        session['dateEnd']  = dateEnd                      
        session['searchKey'] = searchKey       

        inputPath = session['inputPath']               
        counters, session['messages'] = ExtractInformation.GetPrivateChat(inputPath, mediaType, phoneNumber, dateBegin, dateEnd, searchKey)
        
        if session['searchKey'] == 'null':
            searchKey = ''

        return render_template('privateChat.html', phoneNumber=Service.FormatPhoneNumber(phoneNumber), nonFormattedNumber = phoneNumber, counters = counters, messages = session['messages'], str=str, vcardTelExtractor = Service.VcardTelExtractor, originalPhoneNumber = phoneNumber, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, GetUserProfilePicImage = Service.GetUserProfilePicImage, dateBegin=dateBegin, dateEnd=dateEnd, searchKey=searchKey)
    else:
        return redirect(url_for('Home'))


@app.route('/groupChat/<mediaType>/<groupName>/<dateBegin>_<dateEnd>_<searchKey>', methods = ['GET', 'POST'])
def GroupChatFilters(mediaType, groupName, dateBegin, dateEnd, searchKey):
        
    if session['noDbError']  != 1:
        session['dateBegin'] = dateBegin           
        session['dateEnd']  = dateEnd                      
        session['searchKey'] = searchKey  
        inputPath = session['inputPath']               
        counters, groupId, session['messages'] = ExtractInformation.GetGroupChat(inputPath, mediaType, groupName, dateBegin, dateEnd, searchKey)
        groupId = groupId[0]['ZCONTACTJID']

        return render_template('groupChat.html', groupName=groupName, counters = counters, messages = session['messages'], groupId = groupId, str=str, vcardTelExtractor = Service.VcardTelExtractor, GetSentDateTime=Service.GetSentDateTime, GetReadDateTime=Service.GetReadDateTime, FormatPhoneNumber=Service.FormatPhoneNumber, GetUserProfilePicImage = Service.GetUserProfilePicImage, dateBegin=dateBegin, dateEnd=dateEnd, searchKey=searchKey)
    else:
        return redirect(url_for('Home'))


@app.route('/groupChat/<mediaType>/<groupName>', methods = ['GET', 'POST'])
def GroupChat(mediaType, groupName):

    if request.method =='POST':
        
        if "file" in request.files:

            files = request.files.getlist("file")
        
            for file in files:
                path = os.path.dirname(file.filename)
                filename = os.path.basename(file.filename)
                basePath = os.path.join(app.config['UPLOAD_FOLDER'], "Media")
                basePath = os.path.join(basePath, path)
                if not os.path.exists(basePath):
                    os.makedirs(basePath, exist_ok=True)          
                file.save(os.path.join(basePath, utils.secure_filename(filename) ))
        
        if "dateBegin" in request.form:
            session['dateBegin'] = request.form["dateBegin"] 
               
        if "dateEnd" in request.form:
            session['dateEnd']  = request.form["dateEnd"] 
                       
        if "searchKey" in request.form:
            session['searchKey'] = request.form["searchKey"]
            
    if session['noDbError']  != 1:
        return redirect(url_for('GroupChatFilters', mediaType=mediaType, groupName=groupName, dateBegin=session['dateBegin'], dateEnd=session['dateEnd'], searchKey=session['searchKey']))
    else:
        return redirect(url_for('Home'))

@app.route('/checkReport')
def CheckReport():
    global CertificatePath

    if (session['reportPath'] != GlobalConstant.noReportSelected and session['certificatePath']  != GlobalConstant.noCertificateSelected):
        session['reportStatus']  = Service.ReportCheckAuth(session['reportPath'], session['certificatePath'])

    return render_template('checkReport.html', reportPath=os.path.basename(session['reportPath']), certificatePath=os.path.basename(session['certificatePath']), reportStatus=session['reportStatus'])

@app.route('/reportPath', methods = ['GET', 'POST'])
def ReportPath():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        f = request.files['file']
        
        if f and allowed_file(f.filename, {'pdf'}):
            filename = utils.secure_filename(f.filename)
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
            filename = utils.secure_filename(f.filename)
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
        outputFile, certificateFile = GenerateReport.DbHash(session['inputPath'], app.config['UPLOAD_FOLDER'], session['serialDb'])
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        
        if os.path.exists(outputFile):
            os.remove(outputFile)
        if os.path.exists(certificateFile):
            os.remove(certificateFile)
            
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name = session['serialDb'] + "-DbHash.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/chatListReport')
def ChatListReport():

    if session['noDbError']  != 1:
        extractedDataList = ExtractInformation.GetChatList(session['inputPath'])
        outputFile, certificateFile = GenerateReport.ChatListReport(app.config['UPLOAD_FOLDER'], session['serialDb'], extractedDataList)
        memory_file = BytesIO()

        with ZipFile(memory_file, "w") as newzip:
            newzip.write(outputFile, os.path.basename(outputFile))
            newzip.write(certificateFile, os.path.basename(certificateFile))
        
        memory_file.seek(0)
        
        if os.path.exists(outputFile):
            os.remove(outputFile)
        if os.path.exists(certificateFile):
            os.remove(certificateFile)
            
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=session['serialDb'] + "-chatListReportExtraction.zip")
    else:
        return redirect(url_for('Home'))

@app.route('/generatePrivateChatReport/<phoneNumber>')
def generatePrivateChatReport(phoneNumber):

    report, certificate = GenerateReport.PrivateChatReport(app.config['UPLOAD_FOLDER'], phoneNumber, session['messages'])
    
    basePath = os.path.join(app.config['UPLOAD_FOLDER'], 'Media')
    sha, certSha = GenerateReport.CalculateMediaSHA256(os.path.join( basePath, phoneNumber + "@s.whatsapp.net"), app.config['UPLOAD_FOLDER'], phoneNumber)
    md5, certMd5 = GenerateReport.CalculateMediaMD5(os.path.join( basePath, phoneNumber + "@s.whatsapp.net"), app.config['UPLOAD_FOLDER'], phoneNumber)
    
    memory_file = BytesIO()

    with ZipFile(memory_file, "w") as newzip:
        newzip.write(report, os.path.basename(report))
        newzip.write(certificate, os.path.basename(certificate))
        newzip.write(sha, os.path.basename(sha))
        newzip.write(certSha, os.path.basename(certSha))
        newzip.write(md5, os.path.basename(md5))
        newzip.write(certMd5, os.path.basename(certMd5))
        mediaPath = os.path.join(basePath, phoneNumber + '@s.whatsapp.net')
        if os.path.exists(mediaPath):  
            for dirpath, dirnames, medias in os.walk(mediaPath):  
                for media in medias:
                    path= os.path.join(dirpath, media)
                    newzip.write(path, os.path.join('Media', os.path.basename(media)))
                    
    memory_file.seek(0)
    
    if os.path.exists(report):
        os.remove(report)
    if os.path.exists(certificate):
        os.remove(certificate)
    if os.path.exists(certSha):
        os.remove(certSha)
    if os.path.exists(certMd5):
        os.remove(certMd5)
    if os.path.exists(sha):
        os.remove(sha)
    if os.path.exists(md5):
        os.remove(md5)
    if os.path.exists(mediaPath):
        shutil.rmtree(mediaPath)
        
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name= phoneNumber + '-' + session['serialDb'] + ".zip")

@app.route('/generateGroupChatReport/<groupName>-<groupId>')
def generateGroupChatReport(groupName, groupId):

    groupNameNoSpaces = groupName.replace(" ", "")

    report, certificate = GenerateReport.GroupChatReport(app.config['UPLOAD_FOLDER'], groupName, session['messages'])
    
    basePath = os.path.join(app.config['UPLOAD_FOLDER'], 'Media')
    sha, certSha = GenerateReport.CalculateMediaSHA256(os.path.join(basePath, groupId), app.config['UPLOAD_FOLDER'], groupNameNoSpaces)
    md5, certMd5 = GenerateReport.CalculateMediaMD5(os.path.join(basePath, groupId), app.config['UPLOAD_FOLDER'], groupNameNoSpaces)

    memory_file = BytesIO()

    with ZipFile(memory_file, "w") as newzip:
        newzip.write(report, os.path.basename(report))
        newzip.write(certificate, os.path.basename(certificate))
        newzip.write(sha, os.path.basename(sha))
        newzip.write(certSha, os.path.basename(certSha))
        newzip.write(md5, os.path.basename(md5))
        newzip.write(certMd5, os.path.basename(certMd5))
        mediaPath = os.path.join(basePath, groupId)
        if os.path.exists(mediaPath):  
            for dirpath, dirnames, medias in os.walk(mediaPath):  
                for media in medias:
                    path= os.path.join(dirpath, media)
                    newzip.write(path, os.path.join('Media', os.path.basename(media)))
                    
    memory_file.seek(0)
    
    if os.path.exists(report):
        os.remove(report)
    if os.path.exists(certificate):
        os.remove(certificate)
    if os.path.exists(certSha):
        os.remove(certSha)
    if os.path.exists(certMd5):
        os.remove(certMd5)
    if os.path.exists(sha):
        os.remove(sha)
    if os.path.exists(md5):
        os.remove(md5)
    if os.path.exists(mediaPath):
        shutil.rmtree(mediaPath)
        
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name= groupNameNoSpaces  + '-' + session['serialDb'] +  ".zip")

@app.route('/about')
def About():
    return render_template('about.html')

@app.route('/exit')
def Exit():
    session['serialDb'] = GlobalConstant.noDatabaseSelected
    session['inputPath'] = GlobalConstant.noDatabaseSelected
    session['fileName'] = GlobalConstant.noDatabaseSelected
    session['fileSize'] = GlobalConstant.noDatabaseSelected
    session['dbSha256'] = GlobalConstant.noDatabaseSelected
    session['dbMd5']  = GlobalConstant.noDatabaseSelected
    session['noDbError']  = 1
    session['noOutPathError']  = 1

    return redirect(url_for('Home'))

def main():
    #RELEASE
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    #DEBUG
    # webbrowser.open('http://localhost:5000') 
    # app.run(debug=True, use_reloader=False)     

if __name__ == '__main__':
    main()
