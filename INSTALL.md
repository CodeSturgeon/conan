
## Configuring CouchDB

### Installing dispatcher

Edit you ini file and add the following config lines, and if they are not already there, the section titles.

    [external]
    tokened_download = /usr/bin/python -mconan.tokened_download

    [httpd_db_handlers]
    _tokened_download = {couch_httpd_external, handle_external_req, <<"tokened_download">>}

