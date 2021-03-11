# coding: utf-8

# OCI - Stop
# This script will stop compute, Autonomous and DbSys instances, using a specific Tag
# Version 1.0 - January 20 2021

import sys
import oci
from oci.signer import Signer
from modules.identity import *
from modules.compute import *
from modules.autonomous_db import *
from modules.db_system import *

########## Configuration ####################

# Authenticate through an instance principal (TRUE/FALSE)
use_instance_principal = 'FALSE'

# Authenticate through CloudShell (TRUE/FALSE) + tenant OCID
use_cloudshell = 'TRUE'
tenancy_id = 'ocid1.tenancy.oc1..XXXXXX'

# You can target a specific compartment OCID. Tenancy OCID will be set if null.
top_level_compartment_id = ''

# List compartment names to exclude
excluded_compartments = ['']

# List target regions. All regions will be counted if null.
target_region_names = ['eu-frankfurt-1']
#target_region_names = []

# Tag Namespace, Tag Key & Tag Value (case sensitive)
tagnamespace = 'Night_Stop'
tagkey = 'stop'
tagvalue = 'True'

#############################################

if use_instance_principal == 'TRUE':
    auth_mode = 'instance_principal'    
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    config = {}
    
if use_cloudshell == 'TRUE':
    auth_mode = 'cloud_shell'
    # get the cloud shell delegated authentication token
    delegation_token = open('/etc/oci/delegation_token', 'r').read()
    print("delegation_token")
    print(delegation_token)
    print()
    print()
    # create the api request signer
    signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(delegation_token=delegation_token)
    config = {}

else:
    auth_mode = 'config_file'
    # Default config file and profile
    config = oci.config.from_file(configfile, profile)
    tenancy_id = config['tenancy']
    signer = Signer(
        tenancy = config['tenancy'],
        user = config['user'],
        fingerprint = config['fingerprint'],
        private_key_file_location = config['key_file'],
        pass_phrase = config['pass_phrase']
    )

tagdata = {}
tagdata.update( {'TagNamespace' : tagnamespace})
tagdata.update( {'TagKey' : tagkey})
tagdata.update( {'TagValue' : tagvalue})

print ("\n===========================[ Login check ]=============================")
login(config, signer, auth_mode)

print ("\n==========================[ Target regions ]===========================")
all_regions = get_region_subscription_list(config, signer, tenancy_id)
target_regions=[]
for region in all_regions:
    if (not target_region_names) or (region.region_name in target_region_names):
        target_regions.append(region)
        print (region.region_name)

print ("\n========================[ Target compartments ]========================")
if not top_level_compartment_id:
    top_level_compartment_id = tenancy_id
compartments = get_compartment_list(config, signer, top_level_compartment_id)
target_compartments=[]
for compartment in compartments:
    if compartment.name not in excluded_compartments:
        target_compartments.append(compartment)
        print (compartment.name)

for region in target_regions:
    print ("\n============[ {} ]================".format(region.region_name))

    config["region"] = region.region_name

    stop_compute_instances(config, signer, target_compartments, tagdata)
    stop_autonomous_dbs(config, signer, target_compartments, tagdata)
    stop_database_systems(config, signer, target_compartments, tagdata)
