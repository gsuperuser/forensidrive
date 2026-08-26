# Supported Tools Documentation

## Recovery Tools
- **photorec**: File data recovery software designed to recover lost files including video, documents and archives. ForensiDrive uses it for signature-based carving.
- **testdisk**: Powerful free data recovery software. Primarily designed to help recover lost partitions.
- **ddrescue**: Data recovery tool that copies data from one file or block device to another, hard to rescue in case of read errors.
- **foremost**: Console program to recover files based on their headers, footers, and internal data structures.
- **scalpel**: Fast file carver that reads a database of header and footer definitions.

## Erasure Tools
- **shred**: Overwrites the specified FILE(s) repeatedly, in order to make it harder for even very expensive hardware probing to recover the data. ForensiDrive uses this for multi-pass secure wipes.
- **wipefs**: Utility to wipe filesystem, raid, or partition table signatures. Used for quick logical wipes.
- **blkdiscard**: Used to discard device sectors. Useful for SSDs (TRIM).
- **dd**: Used for zeroing out a drive (`dd if=/dev/zero of=/dev/sdX`).

## System Tools
- **lsblk**: Lists information about all available or the specified block devices. Used to populate the Inspection UI.
- **blkid**: Used to locate/print block device attributes.
- **mount** / **umount**: Used to mount partitions for logical inspection.
- **fsck**: Used to check and optionally repair Linux file systems.
