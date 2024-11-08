# file

"""
For our scripts to work, we need to download the Netflix prize data. As this file is ~500 MB and the licensing terms are dubious, we decided early on not to include it as part of the repo. It is however available on the Internet Archive here: https://archive.org/details/nf_prize_dataset.tar

We should write a script that downloads this tarfile, decompresses it, and puts the contents in /data/.

Specifically, everything that is in the download directory that the tarfile produces should be in the /data/ directory. So if there is download/movie_titles.txt it should be /data/movie_titles.txt.

In general, this would be a good candidate for a bash script that does wget -> tar -xzf -> rename directory. But it would be better to do it in Python for portability reasons (some team members use Windows).

We can definitely download the file with requests, but it might not be the perfect fit. We should research if there is a wget type library for Python that we could use.

We can use the tarfile library to extract the files: https://docs.python.org/3/library/tarfile.html

Finally, renaming can be done with os or shutil: https://docs.python.org/3/library/os.html#os.rename
"""
