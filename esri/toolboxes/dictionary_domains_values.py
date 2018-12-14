import arcpy
import os
import shutil
TEMP = "C:\\Temp"


if not os.path.exists(TEMP):
    os.makedirs(TEMP)
else:
    shutil.rmtree(TEMP)
    os.makedirs(TEMP)

path_sde_connection = "C:\\Users\\GISAdmin\\AppData\\Roaming\\ESRI\\ArcGISPro\\Favorites\\Default.sde"
utility_features = os.path.join(path_sde_connection, "ArcSDE.SDE.Utilities_SANITARY\\ArcSDE.SDE.sGravityMain")
database = "C:\\Users\\GISAdmin\\Documents\\ArcGIS\\Projects\\ProjectSerialNumberTool\\ProjectSerialNumberTool.gdb"
subdivision_feature = os.path.join(path_sde_connection, "Subdivisions_Res")

arcpy.ClearEnvironment("workspace")
gdb_name = "scratch.gdb"
gdb_copy = arcpy.CreateFileGDB_management(TEMP, gdb_name)
arcpy.env.workspace = os.path.join(TEMP, gdb_name)

utility_domains = []
utility_types = []

utility_fields = arcpy.ListFields(utility_features)

for u_field in utility_fields:
    if u_field.domain != "":
        utility_domains.append(u_field.domain)
        utility_types.append(u_field.type)
del utility_domains[0]
del utility_types[0]
utility_types[:] = ['TEXT' if x == 'String' else x for x in utility_types]
utility_types[:] = ['SHORT' if x == 'SmallInteger' else x for x in utility_types]
utility_types[:] = ['LONG' if x == 'Integer' else x for x in utility_types]
utility_types[:] = ['FLOAT' if x == 'Double' else x for x in utility_types]

# utility_dict = {}
# for d in utility_domains:
#     for t in utility_types:
#         utility_dict[d] = t
# print(utility_dict)

domains = arcpy.da.ListDomains(path_sde_connection)
for domain in domains:
    if domain.name in utility_domains:
        if domain.domainType == 'CodedValue':
            coded_values = domain.codedValues
            for d, t in zip(utility_domains, utility_types):
                # create coded domain
                arcpy.CreateDomain_management(gdb_copy, domain.name, domain.description, t, "CODED", "DUPLICATE", "DEFAULT")
                # check the domain of the new geodatabase
                new_domains = arcpy.da.ListDomains(gdb_copy)
                for new_domain in new_domains:
                    print(new_domain.name)
                for val, desc in coded_values.items():
                    print('{0} : {1}'.format(val, desc))
                    # Add each domain value
                    arcpy.AddCodedValueToDomain_management(gdb_copy, domain.name, val, desc)
        elif domain.domainType == 'Range':
            # TODO create range domain
            print('Min: {0}'.format(domain.range[0]))
            print('Max: {0}'.format(domain.range[1]))
            # TODO add domain range value
        # TODO Assign Domain To Field Tool

        # utility_copy = arcpy.CopyFeatures_management(utility_features, "utility_copy")
        # subdivision_copy = arcpy.CopyFeatures_management(subdivision_feature, "subdivision_copy")
