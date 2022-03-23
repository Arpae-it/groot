import pickle
import sys,glob
import os.path
import mimetypes
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
totfiles=0


def main():
    if(len(sys.argv)!=3):
        print("usage: groot source_google_folder_id dest_google_folder_id")
        print("")
        print("Copy configuration files (credentials.json, token.pickle) in:")
        print(getBasepath())
        sys.exit(-1)
  
    creds=getCreds()
    service = getDriveService(creds)
    tempotot=datetime.datetime.now()
    print("[groot]")
    groot(service,sys.argv[1],sys.argv[2])
    print()
    delta=(tempotot-datetime.datetime.now()).seconds
    print(f'Processati {totfiles} in {delta} secondi'  )

def groot(service,sourceId,targetId,tab=""):
    global totfiles
    
    
    files,folders=getFolderContent(service,sourceId)
    
    totfiles=totfiles+len(files)
    for file in files:
        
        tempo=datetime.datetime.now()
        print(f'{tab}· {file.get("name")} - {file.get("mimeType")}',end="")
        
        moveFile(service,file.get("id"),sourceId,targetId)
        print(' '+str((tempo-datetime.datetime.now()).microseconds/1000))

    for folder in folders:
        foldName=folder.get("name")
        print(f'{tab}[{foldName}]')
        newId = create_folder_in_folder(service,foldName,targetId)
        groot(service,folder.get("id"),newId.get("id"),tab+"   ")


def moveFile(service,id,sourceId,targetId):    
    #file = service.files().get(fileId=fileId,
    #                             fields='parents').execute()

    #previous_parents = ",".join(file.get('parents'))
    # Move the file to the new folder
    try:
        #print(f'{id} {sourceId} {targetId}')
        #print(targetId)
        file = service.files().update(fileId=id,
                                    addParents=targetId,
                                    removeParents=sourceId,
                                    fields='id, parents').execute()
 
    except Exception as e:
        print("Errore "+str(e))

def create_folder_in_folder(service,folder_name,parent_folder_id):    
    file_metadata = {
    'name' : folder_name,
    'parents' : [parent_folder_id],
    'mimeType' : 'application/vnd.google-apps.folder'
    }

    fold = service.files().create(body=file_metadata,
                                    fields='id').execute()
    return fold;    
    
    print ('Folder ID: %s' % file.get('id'))


def getFolderContent(service, folderId):
    page_token = None

    files = []
    folders = []

    q = f"'{folderId}' in parents"
    while True:

        response = service.files().list(q=q,
                                            spaces='drive',
                                            #fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()

        for itm in response.get('files', []):
            # Process change
            if(itm.get('mimeType') == 'application/vnd.google-apps.folder'):
                folders.append(itm)
            else:
                files.append(itm)

            #print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)

        if page_token is None:
            return files,folders

SCOPES = ['https://www.googleapis.com/auth/drive']
def getBasepath():
    
    if getattr(sys, 'frozen', False):
        x=sys.executable        
    else:
        # we are running in a normal Python environment
        x=os.path.abspath(sys.argv[0])

    return os.path.dirname(x)+"\\"

def getCreds():
    creds = None

    basePath = getBasepath()

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(basePath+'token.pickle'):
        with open(basePath+'token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(basePath+'credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    basePath+'credentials.json', SCOPES)
                creds = flow.run_local_server()
            else:
                print("file di configurazione non trovato in "+basePath)
                sys.exit(-1)
        # Save the credentials for the next run
        with open(basePath+'token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def getDriveService(creds):
    
    return build('drive', 'v3', credentials=creds)

if __name__ == "__main__":
    main()