# This script will process the transcripts
# 1. Download the transcripts from YouTube
# 2. Enrich the transcripts into 5 minute buckets
# 3. Enrich the transcripts with embeddings

# set the folder environment variable where the transcripts are located
$env:TRANSCRIPT_FOLDER = "transcripts"

# echo the TRANSCRIPT_FOLDER environment variable
Write-Output $env:TRANSCRIPT_FOLDER

# make directory for the transcripts
New-Item -ItemType Directory -Force -Path $env:TRANSCRIPT_FOLDER

python transcript_download.py -f $env:TRANSCRIPT_FOLDER
python transcript_enrich_bucket.py -f $env:TRANSCRIPT_FOLDER
python transcript_enrich_embeddings.py