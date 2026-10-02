# Archive inventory

**EMPIRICALLY VERIFIED IN THIS AUDIT.** 41,251 ZIP members, 26,963,187,161 member bytes. Outer ZIP entries use stored compression; many TSV members already contain gzip data. A complete second extracted tree would add approximately 25.11 GiB.

| archive | members | member_bytes | local_bytes |
| --- | --- | --- | --- |
| experiment1.zip | 3690 | 892366871 | 893268919 |
| experiment2.zip | 8994 | 5599789317 | 5601886507 |
| experiment3.zip | 9872 | 7964570671 | 7966970285 |
| experiment4.zip | 8788 | 5463994648 | 5466148546 |
| experiment5.zip | 9907 | 7042465654 | 7044836344 |


[archive_members.parquet](evidence/archive_members.parquet) retains member path, bytes, compressed bytes, CRC32, method, directory indicator and offset. `CRC32` is an official member-integrity field, not a cryptographic identity. Archive cryptographic verification is in [download audit](download_and_version_audit.md). Archive roots are separate datasets; never flatten them into a shared `sub-XX` tree.
