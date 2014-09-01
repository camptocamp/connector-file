Connector File Import
=====================

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
