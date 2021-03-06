# coding: utf-8

# usage:

# Get OCI consumption for the last 6 months (default)
# python3 ./oci-get-cost.py

# Get OCI consumption for a given period (using 2 arguments), date range must not be more than 365 days
# python3 ./oci-get-cost.py 2020-09-01 2020-10-01

# Get OCI consumption from a specific date (using 1 argument), until current day
# python3 ./oci-get-cost.py 2020-09-01

# This script records consumption logs into a bucket and/or sends it through email
# It creates both compartment & bucket if they don't exist

# It manages 3 authentication methods
# local_config_file, instance_principal, cloudshell

# Version 1.0 - October 29 2020

import os
import sys
import oci
from datetime import datetime
from modules._main import _main
from modules.identity_mod import login
from dateutil.relativedelta import relativedelta

#---------------------------{ Config Section Start }---------------------------#

# compartment to use or to create 
my_compartment = "XXXX"

# object bucket to use or to create in the above compartment
my_bucket = "Billing_data"

# if you want to authenticate through local config file
configfile = '/home/opc/.oci/config'
profile = "DEFAULT"

# if you want to authenticate through instance principal, set 'TRUE'
use_instance_principal = 'FALSE'

# if you want to authenticate through OCI CloudShell, set 'TRUE'
use_cloudshell_auth = 'TRUE'

# set tenancy_id if you use either instance_principal or cloudshell
tenancy_id = 'ocid1.tenancy.oc1..aaaaaaaalvbbkqilwful6cmkqag7ireyyx3cjwhbevh5wjlsl6zpzm4ibj4a'

#---------------------------{ Config Section End }---------------------------#


# use argument(s) if any
if len(sys.argv) > 1:
	start_date = sys.argv[1]
else:
	start_date = datetime.today() + relativedelta(months=-6)
	start_date = start_date.strftime("%Y-%m-%d")
if len(sys.argv) > 2:
	end_date = sys.argv[2]
else:
	end_date = datetime.today()
	end_date = end_date.strftime("%Y-%m-%d")

# call login function
print ("\n[ Login check ]\n")
connect = login(use_instance_principal, use_cloudshell_auth, configfile, profile, tenancy_id)

config = connect[0] 				# get config from value #0 in the tuple returned by login function
signer = connect[1] 				# get signer from value #1 in the tuple returned by login function
my_tenant = str.upper(connect[2]) 	# get tenant_name from value #2 in the tuple returned by login function
tenancy_id = connect[3]				# get tenancy_id from value #3 in the tuple returned by login function


# call main, manage compartment/bucket, log files, etc.
local_file = _main(config, signer, my_tenant, tenancy_id, my_compartment, my_bucket, start_date, end_date)


# remove local file
local_file_path = os.path.basename(local_file)
while os.path.exists(local_file_path):
	os.remove(local_file)