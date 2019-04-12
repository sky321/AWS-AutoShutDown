import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    global ec2
    e_tag = event.get('tag','project')
    e_value = event.get('value','')
    e_subject = ''
    e_arn = ''
    # Retrieve SNS subject and topic-arn
    if event.get('Records') and event.get('Records')[0] and event.get('Records')[0].get('Sns'):
        e_subject = event.get('Records')[0].get('Sns').get('Subject')
        e_arn = event.get('Records')[0].get('Sns').get('TopicArn')
    if not e_subject.startswith("AutoShutDownTrigger"):
		print "Unknown notification \"%s\", ignoring" % e_subject
	# to test without looking for special event to trigger -> comment the return
		return
    if e_arn:
        e_value = e_arn.split(':')[-1].split('-')[0]
    # not all region are in scope only ireland
	#e_regions = ec2.describe_regions().get('Regions',[])
    # Instance filter: select only running instances with selected tag
    filters = [{
            'Name': 'instance-state-name', 
            'Values': ['running']
        },
        {
            'Name': 'tag:'+e_tag,
            'Values': [e_value]
        }
    ]
	# don't loop through the array because we only need one region
	#for e_region in e_regions:
	# connect to new region
	# only ireland in scope
    e_region = 'eu-west-1'
	# don't use array
    #print "Processing region %s " % e_region['RegionName']
    #ec2 = boto3.resource('ec2', region_name=e_region['RegionName'])
    print "Processing region %s " % e_region
    ec2 = boto3.resource('ec2', region_name=e_region)
    # search for matching instances
    e_instances = ec2.instances.filter(Filters=filters)
    e_instanceids = [instance.id for instance in e_instances]
    # shutdown instances
    if len(e_instanceids) > 0:
        print ec2.instances.filter(InstanceIds=e_instanceids).stop()