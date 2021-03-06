import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns', region_name='us-east-1')
    topic = sns.Topic('arn:aws:sns:us-east-1:597217841698:jovan-stanoevski-work-deploy-serverless-portfolio')
   
    location = {
        "bucketName":'codebuild.jovan.stanoevski.work',
        "objectKey": 'codebuild-aws-serverless-portfolio.zip'
        }
    try:
        job = event.get("CodePipeline.job")
        if job:
            print "Lambda triggered from codepipeline event"
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "jovan-stanoevski-work-deploy-serverless-portfolio":
                    location = artifact["location"]["s3Location"]
        print "Building portfolio from " + str(location)
        s3 = boto3.resource('s3')
        
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
        topic.publish(Subject="Serverless Portfolio jovan.stanoevski.work Deployed Successfully", Message="Serverless Portfolio jovan.stanoevski.work Deployed Successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        topic.publish(Subject="Serverless Portfolio", Message="Serverless Portfolio Deployed Successfully")
        print "Job Complete."
    except:
        topic.publish(Subject="Serverless Portfolio jovan.stanoevski.work Deployment Failed", Message="Serverless Portfolio jovan.stanoevski.work Not Deployed Successfully")
        raise
        print "Job not successful."