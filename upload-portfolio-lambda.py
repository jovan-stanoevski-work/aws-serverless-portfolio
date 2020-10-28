import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')

    location = {
        "bucketName":'codebuild.jovan.stanoevski.work',
        "objectKey": 'codebuild-aws-serverless-portfolio.zip'
        }

    

    portfolio_bucket = s3.Bucket('jovan.stanoevski.work')
    build_bucket = s3.Bucket(location["bucketName"])

    portfolio_zip = StringIO.StringIO()

    build_bucket.download_fileobj(location["objectKey"],portfolio_zip)

    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(obj, nm,
            # Remember mimetypes guesses using file extension so make sure exists!
            ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')