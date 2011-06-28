# Stories

## Actors

### Producer
File producer. This is a person who manages the production and distribution of sets of files.

### User
End consumer of distributed files.

### CouchDB
Combination data store web server. Acts as datastore, front end web server and process manager.

### Publisher
Responsible for creating and updating publication documents from source files. Publisher code is stand alone and invoked only by the producer.

### Distributor
Used to create downloads tokens for users based on publication documents previously created by the publisher.

### Dispatcher
Process (external) hosted by CouchDB that performs the logic checks and supplies or rejects the download.

## Producer stories

### Producer publishes a set of files

1. Producer places files in an empty folder
1. Producer invokes publisher with folder path
1. Publisher scans folder to create file list
1. Publisher assembles metadata
    - Current time
    - Args used to create the publication
1. Publisher uploads new publication document to CouchDB

1. Producer arranges user<->file mapping data
    - TBD
        - SQL Table
        - CSV File
        - Couch Doc
1. Producer invokes Distributor on mapping data
1. Distributor creates distribution document
    - Tokens are created
    - Document is stored in CouchDB
1. Distributor sends email notifying users of the new downloads

### Producer restates one or more files
Published files can be found to have errors after they are published. The files containing errors need to be restated. Users who have already downloaded the files need to be notified and provided with the restated files.

1. Producer updates files previously published
1. Producer invokes Publisher against the new files with a message
1. Publisher queries CouchDB for the affected files
    - All matches must come from a single publication
    - Uses published_files view
    - publication document is retrieved from view
1. Publisher updates publication document
    - Message is added to publication document
    - Version metadata is updated
    - File attachments are replaced
    - publication document is updated
1. Publisher queries CouchDB for users who have already downloaded the files
    - Uses downloaded_files view
1. Publisher creates new distribution document for supplements
    - Tokens are created
    - Document is stored in CouchDB
1. Publisher sends email notifying users of the supplements

## User stories

### User downloads a file

1. User receives an email from the system about a newly available file
1. User clicks on link in email
    - Link points to dispatcher
1. Dispatcher validates embedded token in link
    - Tokens view is queried in CouchDB
    - Token's distribution doc is retrieved from the view
1. Dispatcher supplies download file
    - Token is queried for the files to be included
    - Files are retrieved from publication document
    - Files are zipped in memory
    - Zipfile is dispatched to the user
1. Dispatcher invalidates download token
    - Token's distribution doc it updated
    - Token's distribution doc is written back to CouchDB

### User re-downloads a file

1. User clicks on previously used link
1. Dispatcher finds used embedded token in link
    - Tokens view is queried in CouchDB
    - Token is found to have a used_time set
1. Dispatcher serves an error page
1. User views error page offering to send a new link
    - Link leads back to dispatcher with a query argument
1. User clicks to have new link sent for this download
    - New token is generated using old token's specs
    - Token is added to the distribution document
    - Email is sent to the user
    - Mail sent page is returned
