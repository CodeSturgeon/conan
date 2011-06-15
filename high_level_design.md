# High level design of Conan

## Overview

### Outline
Files need to be securely distributed to a set of users. Files are created in large and small batches. Users should be able to access select files in the batches.

### Background
Currently we produce large numbers of files that need to be distributed to users. In a single batch, a user generally needs to recive several files. These files are often too large to be sent via email.

### Naming
The name 'Conan' is taken from the charecter 'Conan the Librarian' who appeared in [UHF](http://www.imdb.com/title/tt0098546/). It is a working name that is subject to change when something more apropreate comes to mind.

## System Requirements

### User interface must be easy to use
The end users of the system should not be considered to be techincally literate. The system must be intuitive for it's basic tasks.

### Users should not need credentials
In order to not add to the overhead of the users, we should not require credentials to recive files from the generated batches.

### Users should be notified of newly available files
When a new batch of files is generated, all users who have access to the files generated should be notified of the avilabilty of the files.

### System must be secure
Users should only be able download the files that they have been given access too.

### Fine grained control over which files a user can access
Users should be granted access to specific patterns of files.

### Producers should be able to re-state files after distribution
The file producer should have an easy way of distributing updated files to the people associated with that file.

## Initial Vision

### System description
A simple http file download service. Downloads are pre-generated for users by the system. Once downloads are avilable a single use download link is sent to the user the download was produced for. After a file is downloaded the link cannot be used a second time. If the link is used a second time, the user is told that it has already been used and given the option to have a new link generated and sent to them.

Security is enforced by the limited use of the generated URLs (more specifically the embedded token) and the distribution of the URLs via preconfigured email addresses.

### Example experiances

#### User is notified of a new download
User recives an email with a description of the download that has been produced listing it's contents and linking to a helpdesk where help can be found.

#### User downloads file
User clicks on the link supplied. The user may be shown and interstatial page where they need to click a link to continue. The file is downloaded via usual http protocol.

#### User tries to re-use download link
User clicks on the link supplied after it has been used. The user is shown a page that tells them this link has already been used. The user is given the option to generate a new download token and have it sent to their email address.

### Example producer experiance

#### Producer creates a new set of files
Producer generates a new set of files to be sent out to users. They are placed in a specific location on the file system.

#### Producer generates single download for QA user
Producer kicks off the generation of a download for a single user that needs to QA the files.

#### Producer restates files and regenerates download
The QA process found files that are wrong in some way. The producer regenerates the files in question and overwrites them in the filesystem.

#### Producer generates all remaining downloads
With all files QAed the producer generates all the avilable downloads for this filegroup. When the downloads are generated, notifications are sent to the users they were prepaired for.
