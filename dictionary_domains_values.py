import arcpy
import os
import shutil
TEMP = "C:\\Temp"


if not os.path.exists(TEMP):
    os.makedirs(TEMP)
else:
    shutil.rmtree(TEMP)
    os.makedirs(TEMP)

path_sde_connection = "C:\\Users\\GISAdmin\\AppData\\Roaming\\ESRI\\ArcGISPro\\Favorites\\Test.sde"
utility_features = os.path.join(path_sde_connection, "ArcSDE.SDE.Utilities_SANITARY\\ArcSDE.SDE.sGravityMain")
database = "C:\\Users\\GISAdmin\\Documents\\ArcGIS\\Projects\\ProjectSerialNumberTool\\ProjectSerialNumberTool.gdb"
subdivision_feature = os.path.join(path_sde_connection, "Subdivisions_Res")

arcpy.ClearEnvironment("workspace")
gdb_name = "scratch.gdb"
gdb_copy = arcpy.CreateFileGDB_management(TEMP, gdb_name)
arcpy.env.workspace = os.path.join(TEMP, gdb_name)

utility_domains = []
utility_types = []
utility_fieldnames = []
utility_domainType = []
utility_rangeMinValues = []
utility_rangeMaxValues = []
utility_rangeNames = []
utility_codedNames = []

utility_fields = arcpy.ListFields(utility_features)

for u_field in utility_fields:
    if u_field.domain != "":
        utility_domains.append(u_field.domain)
        utility_types.append(u_field.type)
        utility_fieldnames.append(u_field.name)

utility_types[:] = ['TEXT' if x == 'String' else x for x in utility_types]
utility_types[:] = ['SHORT' if x == 'SmallInteger' else x for x in utility_types]
utility_types[:] = ['LONG' if x == 'Integer' else x for x in utility_types]
utility_types[:] = ['FLOAT' if x == 'Double' else x for x in utility_types]

domains = arcpy.da.ListDomains(path_sde_connection)
for domain in domains:
    if domain.name in utility_domains:
        utility_domainType.append(domain.domainType)
        if domain.domainType == 'CodedValue':
            print(domain.name, " ", domain.domainType)
            # print(domain.name, domain.description)
            utility_codedNames.append(domain.name)
            coded_values = domain.codedValues
        elif domain.domainType == 'Range':
            utility_rangeNames.append(domain.name)
            utility_rangeMinValues.append(domain.range[0])
            utility_rangeMaxValues.append(domain.range[1])

utility_dict = zip(utility_domains, utility_types, utility_fieldnames)
result_utility_dict = list(utility_dict)

domains = arcpy.da.ListDomains(path_sde_connection)
for domain in domains:
    if domain.name in utility_domains:
        if domain.domainType == 'CodedValue':
            print(domain.name, " ", domain.domainType)
            # print(domain.name, domain.description)
            coded_values = domain.codedValues
            # print(coded_values)

            arcpy.CreateDomain_management(gdb_copy,
                                          result_utility_dict[0][0],
                                          '',
                                          result_utility_dict[0][1],
                                          "CODED",
                                          "DUPLICATE",
                                          "DEFAULT")
            del result_utility_dict[0]  # This could be a problem if I accidentally delete a range valued object.
            # TODO find a better way to step through this list. Use an ordered dictionary or something.
            # print(result_utility_dict, " ", len(result_utility_dict))
            # check the domain of the new geodatabase
            new_domains = arcpy.da.ListDomains(gdb_copy)
            for new_domain in new_domains:
                print("Coded ", new_domain.name)
            for val, desc in coded_values.items():
                print('{0} : {1}'.format(val, desc))
                # Add each domain value
                arcpy.AddCodedValueToDomain_management(gdb_copy, domain.name, val, desc)
        elif domain.domainType == 'Range':
            arcpy.CreateDomain_management(gdb_copy,
                                          result_utility_dict[0][0],
                                          '',
                                          result_utility_dict[0][1],
                                          "RANGE",
                                          "DUPLICATE",
                                          "DEFAULT")
            del result_utility_dict[0]
            arcpy.SetValueForRangeDomain_management(gdb_copy, domain.name, domain.range[0], domain.range[1])
            arcpy.AssignDomainToField_management(gdb_copy, result_utility_dict[0][3], domain.name)
            new_range = arcpy.da.ListDomains(gdb_copy)
            for n_range in new_range:
                print("Range ", n_range.name)

utility_copy = arcpy.CopyFeatures_management(utility_features, "utility_copy")
subdivision_copy = arcpy.CopyFeatures_management(subdivision_feature, "subdivision_copy")
