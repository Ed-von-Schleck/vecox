VeCoX
=====

vecox is an xml and html revision control system. While it can be used as a standalone application (comparable to *git* or *mercurial*), it's main use is that of a library (although we are not quite there yet).

Possible use cases include: Word- or graphic-processing applications that want to preserve the whole history of documents (provided the store xml files, which many of them do today), web applications saving every iteration of user-editable webpages to roll back possible vandalism etc.

## How It Works ##

vecox differs from git or mercurial in that it tracks *document* revisions and has no concept of a project-wide revision. For an instance, every *save* operation on a document is comparable to a *commit* in git, except that it targets only one document (however, one can conveniently save many documents in one go).

vecox has no equivalent of `git add`, since no files are tracked.

vecox stores documents efficiently, especially large documents with many, mostly small changes between saves. Similar to git, it tracks content, not files, so if two documents have a number of identical nodes, vecox save those nodes only once.

## Command Line Usage ##

### vecox ###

    usage: vecox [-h] {init,save,history,revision} ...

    vecox is an xml and html revision control software.

    positional arguments:
      {init,save,history,revision}
        init                initialize vecox for this directory and subdirectories
        save                Save current revision of file(s)
        history             show history of files
        revision            set a file to a given revision

    optional arguments:
      -h, --help            show this help message and exit

### vecox init ###

    usage: vecox init [-h] [--backend BACKEND]

    optional arguments:
      -h, --help         show this help message and exit
      --backend BACKEND  The storage backend, default: file

### vecox save ###

    usage: vecox save [-h] [--backend BACKEND] [--filetype {auto,xml,hmtl}]
                      [--message MESSAGE]
                      file [file ...]

    positional arguments:
      file                  the file(s) to save

    optional arguments:
      -h, --help            show this help message and exit
      --backend BACKEND     the storage backend, default: file
      --filetype {auto,xml,hmtl}
                            the parsing method, default: auto
      --message MESSAGE, -m MESSAGE
                            the commit message

### vecox history ###

    usage: vecox history [-h] [--backend BACKEND] file [file ...]

    positional arguments:
      file               the file(s) to inspect history

    optional arguments:
      -h, --help         show this help message and exit
      --backend BACKEND  the storage backend, default: file

### vecox revision ###

    usage: vecox revision [-h] [--backend BACKEND] [--force] file hash

    positional arguments:
      file               the file to change revision
      hash               the revision hash

    optional arguments:
      -h, --help         show this help message and exit
      --backend BACKEND  the storage backend, default:
