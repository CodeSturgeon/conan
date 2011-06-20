# Stories

## Actors

### Admin
System administrator. Not part of day to day operation. Admins setup and configure the system.

### Producer
File producer. This is a person who manages the production and distribution of sets of files.

### User
End consumer of distributed files.

### CouchDB
Combination data store web server. Acts as front end web server and process manager.

### Engine
The back end engine. Responcible for processing files, creating downloads and updating user maps. Engine code is stand alone and invoked only by the user.

### Dispatcher
Process (external) hosted by CouchDB that performs the logic checks and supplies or rejects the download.

### Notifier
Process (OS proc) hosted by CouchDB that sends notifications

## Admin stories

### Admin creates publication
Publications need to be created and configured before they can be used.

## Producer stories

### Producer publishes a set of files

1. Producer places files in an empty folder
1. Producer invokes engine with folder path and database
1. Engine scans folder to create file list
1. Engine queries CouchDB to find user<->file mappings
1. Engine calculates filebundles
1. Engine creates each download
    1. Engine compiles metadata
        - Contained files
        - Messages
        - Users targeted
        - Type (download or suppliment)
    1. Engine creates textfile
        - Messages
        - File list
    1. Engine zips published files with textfile
    1. Engine uploads to CouchDB
1. Producer marks download notifications as ready
    - Gives producer a little flexability
1. Notifier sends notifications
    - Using Postmarkapp.com
    1. Marks tokens as 'sending'
    1. Sends emails
    1. Marks tokens as 'sent'

### Producer restates one or more files
Published files can be found to have errors after they are published. The files containing errors need to be restated. Users who have already downloaded the files need to be notified and provided with the restated files.

1. Producer updates file in previously published folder
1. Producer invokes engine against the new files with a message
1. Engine queries CouchDB for the affected downloads
1. Engine recreates each downloads zip files
    - Obtains zip file from CouchDB
    - Updates textfile
    - Updates files
    - Recomiles zip files
    - Uploads zip file back to couchdb
1. Engine queries CouchDB for users who have already downloaded the files
1. Engine calculates supplimental bundles
1. Engine creates each supplimental download
    - Processed like a new download
1. Producer marks download notifications as ready
1. Notifier sends notifications

### Producer updates user map
Producer needs to update the mapping of what users are supposed to recive which files.

1. Producer invokes engine against CSV file
1. Engine validates file
1. Engine loads or rejects file

## User stories

### User downloads a file

1. User recives an email from the system about a newly avilable file
1. User clicks on link in email
1. Dispatcher validates embedded token in link
1. Dispatcher supplies download file
1. Dispatcher invalidates download token

### User re-downloads a file

1. User clicks on previously used link
1. Dispatcher finds used embedded token in link
1. Dispatcher redirects to error URL
1. User views an error page offering to send a new link
1. User clicks to have new link sent for this download
