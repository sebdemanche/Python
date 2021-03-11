import oci

resource_name = 'autonomous databases'

red = lambda text: '\033[0;31m' + text + '\033[0m'
green = lambda text: '\033[0;32m' + text + '\033[0m'

def stop_autonomous_dbs(config, signer, compartments ,tagdata):
    target_resources = []

    print("\nListing all {}... (* is marked for stop)".format(resource_name))
    for compartment in compartments:
        # print("  compartment: {}".format(compartment.name))
        resources = _get_resource_list(config, signer, compartment.id)
        for resource in resources:
            go = 0
            if (resource.lifecycle_state == 'AVAILABLE'):
                if ('Night_Stop' in resource.defined_tags) and (tagdata['TagKey'] in resource.defined_tags['Night_Stop']): 
                    
                    if (resource.defined_tags['Night_Stop'][tagdata['TagKey']] == tagdata['TagValue']):
                        go = 1
                    else:
                        go = 0
                else:
                    go = 0

            if (go == 1):
                #print("    * {} ({}) in {}".format(resource.display_name, resource.lifecycle_state, compartment.name))
                print(red("    * {} ({}) in {}".format(resource.display_name, resource.lifecycle_state, compartment.name)))
                target_resources.append(resource)
            else:
                print(green("      {} ({}) in {}".format(resource.display_name, resource.lifecycle_state, compartment.name)))

    print('\nStopping * marked {}...'.format(resource_name))
    for resource in target_resources:
        try:
            response = _resource_action(config, signer, resource.id)
        except oci.exceptions.ServiceError as e:
            print("---------> error. status: {}".format(e))
            pass
        else:
            if response.lifecycle_state == 'STOPPING':
                print("    stop requested: {} ({})".format(response.display_name, response.lifecycle_state))
            else:
                print("---------> error stopping {} ({})".format(response.display_name, response.lifecycle_state))

    print("\nAll {} stopped!".format(resource_name))

def _get_resource_list(config, signer, compartment_id):
    object = oci.database.DatabaseClient(config=config, signer=signer)
    resources = oci.pagination.list_call_get_all_results(
        object.list_autonomous_databases,
        compartment_id=compartment_id
    )
    return resources.data

def _resource_action(config, signer, resource_id):
    object = oci.database.DatabaseClient(config=config, signer=signer)
    response = object.stop_autonomous_database(
        resource_id
    )
    return response.data
