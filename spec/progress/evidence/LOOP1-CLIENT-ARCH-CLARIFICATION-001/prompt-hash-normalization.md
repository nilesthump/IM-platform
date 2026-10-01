# Prompt hash normalization correction

Coordinator approval-and-recovery initialization and supplemental dispatch conflated Recorder normalized text SHA with raw file SHA. Original copies and Recorder files are unchanged. Files below are byte-preserved CRLF; Recorder register-prompt decodes text and normalizes CRLF/CR to LF before hashing its prompt copy. These are different representations of the same exact visible content.

| File | Raw byte SHA256 | LF-normalized prompt SHA256 |
| --- | --- | --- |
| human-approved-request.txt | fea55bbe8f428cd02337f7ea48481778ab1749c9e1ff29eabe2b783016ab9dea | 1eaf0f7960056f8bb9b860d2591d17d872e33de56e41d0a41a3f2b50acfb1cc5 |
| human-desktop-sqlx-mobile-emulator-decision.txt | 91033f339f337105bc70f45b20c312b8ed2490d01c0b1607e197cda6e09c770b | 78aa2191a4f3614185781a17ebd5204c949312d3a8eb159435af469d0d1929b5 |

The implementation asserted the supplied supplemental normalized hash against raw bytes and honestly FAILED before editing authority. Both raw and normalized hashes were then independently verified; assertions PASS and exact bytes copied. This correction supersedes mislabeled initialization hash discovery only, never Human content, approval, Recorder data or old historical evidence.
