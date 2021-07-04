
from google.cloud import storage
import io
import log
BUCKET = 'consulting-2718'
  
def uploadFile(filename, name):
  gcs = storage.Client()
  bucket = gcs.get_bucket(BUCKET)
  blob = bucket.blob(name)
  blob.upload_from_filename(filename)
  #blob.upload_from_string(open(filename).read(), content_type='application/octet-stream')
  log.log(blob.public_url)
  return blob.public_url

def downloadFile(filename, name):
  gcs = storage.Client()
  bucket = gcs.get_bucket(BUCKET)
  blob = bucket.blob(name)
  blob.download_to_filename(filename)
  import os
  os.system('cat ' + filename)