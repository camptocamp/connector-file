[![Build Status](https://travis-ci.org/camptocamp/connector-file.svg?branch=master)](https://travis-ci.org/camptocamp/connector-file)
[![Coverage Status](https://coveralls.io/repos/camptocamp/connector-file/badge.png?branch=master)](https://coveralls.io/r/camptocamp/connector-file?branch=master)

# Connector File Import

Asynchronous, fault-tolerant import of external files using the OpenERP
Connector.

This module uses many components of the OpenERP Connector (backends, jobs,
bindings, units, synchronizers).

At the moment it does a specific job, but its components are designed to be
very detached, and adapting that for other use cases should be reasonable.

The use case that is covered at the moment is the import of a large amount
of Journal Entries from CSV files published on a FTP server.

The focus in on the asynchronous, decoupled nature of the process. The actual
import of the file is performed by the standard load() method, the same used
by the built-in import feature of OpenERP.

At the moment, the process is split in three phases, each handled by its own
jobs, Synchronizers and Units:

* The loading of a file from a FTP server. Each file must come with its own
  hash file - at the moment, a MD5 in hex format, with the same file name as
  the CSV and with extension .md5. Each job handles a file.
* The parsing of the file into Chunks, one per Journal Entry. Each chunk
  contains the data serialized into a JSON string. A chunk also has a method
  to reconstruct the corresponding piece of the original file (that could
  be unwieldy). Here, each job handles a file.
* The loading of each chunk in a Journal Entry. Each job handles a Chunk.

# Limitations and future

* Although the three phases (download, parse/split and load) are kept
  intentionally separate, at the moment they are specific to downloading from
  FTP, splitting one move per chunk, and loading account moves only. Future
  versions should make that more generic and extensible. Your contributions and
  thoughts are welcome!
* I disabled a test because of a false positive with travis. See:
  - https://github.com/OCA/maintainer-quality-tools/issues/43#issuecomment-54127125
  - https://github.com/camptocamp/connector-file/issues/2
* I would like this to be included under the OCA umbrella, but that is a bit
  early since there are similar efforts around.

# Contributors

* Leonardo Pistone (@lepistone) is the main author of the code
* Nicolas Bessi (@nbessi) provided the initial design, and helped during
  development

# Changes

## v1.0

* This release represents the moment when the project was migrated from
  Launchpad to Github.
* Functionality is complete, but limited to move lines from CSV files over FTP.
* It deserves 1.0 because it has been in production.
