import arcpy
import os
import sys
import shutil
import time
TEMP = "C:\\Temp"


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "QAQC"
        self.alias = "QAQC"
        # List of tool classes associated with this toolbox
        self.tools = [ProjectIDTool]


class ProjectIDTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Project Serial Number QA/QC Tool"
        self.description = "Creates a column in the feature class that suggests the Project Serial Number determined" \
                           "by the tool's algorithm."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Feature",
            name="utility_feature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Project Serial Number Source Feature",
            name="subdivision_feature",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Workspace",
            name="database",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="SDE Connection",
            name="path_sde_connection",
            datatype="DEServerConnection",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Output Joined Feature",
            name="output_feature",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output")
        param4.parameterDependencies = [param0.name]

        param5 = arcpy.Parameter(
            displayName="SDE Password",
            name="password",
            datatype="GPString",
            parameterType="Required",
            direction="Output")

        params = [param0, param1, param2, param3, param4, param5]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def copy_geodatabase(self, subdivision, utility, sde_path):
        """
        Copies the SDE geodatabase and the associated coded domain values.

        :param subdivision:
        :param utility:
        :param sde_path:
        :return:
        """
        arcpy.ClearEnvironment("workspace")
        gdb_name = "scratch.gdb"
        gdb_copy = arcpy.CreateFileGDB_management(TEMP, gdb_name)
        arcpy.env.workspace = os.path.join(TEMP, gdb_name)
        utility_list = []
        utility_fields = arcpy.ListFields(utility)
        for u_field in utility_fields:
            if u_field.domain != "":
                utility_list.append(u_field.domain)
                print(u_field.domain, ":", u_field.type)

        utility_copy = arcpy.CopyFeatures_management(utility, "utility_copy")
        subdivision_copy = arcpy.CopyFeatures_management(subdivision, "subdivision_copy")
        domains = arcpy.da.ListDomains(sde_path)
        for domain in domains:
            if domain.name in utility_list:  # TODO This needs to be a loop. Find u_field.type
                print(u_field.type)
                if domain.domainType == 'CodedValue':
                    coded_values = domain.codedValues
                    # create coded domain
                    arcpy.CreateDomain_management(gdb_copy, domain.name, "", "", "CODED", "DUPLICATE", "DEFAULT")
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

        return gdb_copy

    def join_utility_subdiv(self, path, gdb_name, subdivision, utility):
        """
        This function sets up and runs the Spatial Join tool in arcpy. I added a couple features that usese whatever
        path the user provides and assigns it to a variable so that I can clean it up later. Also, if the tool fails and
        leaves behind a spatial join feature, this tool will delete it before running the rest of the code.

        The purpose for the spatial join is to identify the polygon that each segment of the utility features lies
        within. This sets up the table which will be used to compare the Project Serial Number with the Suggested
        Project Serial Number.

        :param path:
        :param gdb_name:
        :param subdivision:
        :param utility:
        :return:
        """

        join_feature = os.path.join("{}\\{}", "spatial_joined").format(path, gdb_name)
        if arcpy.Exists(join_feature):
            arcpy.Delete_management(join_feature)
            print("feature deleted")
        else:
            print("feature not detected")

        arcpy.env.workspace = os.path.join(path, gdb_name)
        arcpy.SpatialJoin_analysis(utility,
                                   subdivision,
                                   "spatial_joined",
                                   "JOIN_ONE_TO_MANY",
                                   "KEEP_ALL",
                                   "",
                                   "HAVE_THEIR_CENTER_IN")
        return join_feature

    def compare_fields(self, database, join_table, utility):
        """
        This function uses two hard-coded lists of column names and runs a search cursor and an update cursor within an
        editing session. Right now there is either a logic or a connection issue with the edit session because I do not
        get predictable results. This code runs fine on a file geodatabase.

        The search cursor goes through the joined table (from the previous function) and assigns the target id (the OID
        of the target table) to a variable and assigns the suggested project serial number (called the PROJECT_SERIAL_
        NUMBER_1 in the table) to another variable. The Update cursor uses these to variables to find and replace the
        old PSN to the suggested PSN. Again, this operates beautifully in a FGB, just not in an SDE.

        :param database:
        :param join_table:
        :param utility:
        :return:
        """

        join_fields = ['Join_Count', 'TARGET_FID', 'Project_Serial_Number', 'PROJECT_SERIAL_NUMBER_1']
        utility_fields = ['OID@', 'Project_Serial_Number', 'SUGGESTED_PROJECT_SERIAL_NUMBER']

        try:
            edit = arcpy.da.Editor(database)
            edit.startEditing(False, True)
            edit.startOperation()
            with arcpy.da.SearchCursor(join_table, join_fields) as s_cursor:
                for s_row in s_cursor:
                    # 0 is Join Count
                    # 1 is Target FID
                    # 2 is Project Serial Number
                    # 3 is Project Serial Number 1
                    if s_row[3] != s_row[2] and s_row[0] == 1:
                        target_id = s_row[1]
                        suggested_psn = s_row[3]

                        with arcpy.da.UpdateCursor(utility, utility_fields) as u_cursor:
                            for row in u_cursor:
                                # 0 is OID
                                # 1 is Project Serial Number - no longer used in this iteration
                                # 2 is Suggested Project Serial Number
                                if row[0] == target_id:
                                    row[2] = suggested_psn
                                    u_cursor.updateRow(row)
                                    localtime = time.asctime(time.localtime(time.time()))
                                    arcpy.AddMessage("row updated for " + str(target_id) + " at " + localtime)
                                    # row = u_cursor.next() - apparently not needed in DA Update Cursor
                            del u_cursor
                    # s_row = s_cursor.next()
            del s_cursor
            edit.stopOperation()
            edit.stopEditing(True)
        except arcpy.ExecuteError:
            print(arcpy.GetMessage(2))
        except RuntimeError as r:
            print(r)

    def execute(self, parameters, messages):
        """The source code of the tool."""
        bane_of_my_existence = os.path.join(TEMP, "SDEConn.sde")
        if bane_of_my_existence:
            arcpy.Delete_management(bane_of_my_existence)

        xutility_features = parameters[0].valueAsText
        xsubdivision_feature = parameters[1].valueAsText
        xdatabase = parameters[2].valueAsText
        xpath_sde_connection = parameters[3].valueAsText
        xoutput_feature = parameters[4].valueAsText
        xpassword = parameters[5].valueAsText

        ## Hard-coded paths for testing only.
        path_sde_connection = "C:\\Users\\GISAdmin\\AppData\\Roaming\\ESRI\\ArcGISPro\\Favorites\\Default.sde"
        utility_features = os.path.join(path_sde_connection, "ArcSDE.SDE.Utilities_SANITARY\\ArcSDE.SDE.sGravityMain")
        database = "C:\\Users\\GISAdmin\\Documents\\ArcGIS\\Projects\\ProjectSerialNumberTool\\ProjectSerialNumberTool.gdb"
        output_feature = os.path.join(path_sde_connection, "ArcSDE.SDE.Utilities_SANITARY\\ArcSDE.SDE.sGravityMain")
        subdivision_feature = os.path.join(path_sde_connection, "Subdivisions_Res")
        password = input("Enter password: ")

        # path_sde_connection = "C:\\Users\\avenneman\\AppData\\Roaming\\ESRI\\Desktop10.5\\ArcCatalog\\Test VS607.sde"
        # utility_features = os.path.join(path_sde_connection, "arcsde.SDE.Utilities_DRAINAGE\\ArcSDE.SDE.dGravityMain")
        # database = "C:\\Users\\avenneman\\Documents\\Programming\\SelectWork\\Features.gdb"
        # output_feature = os.path.join(path_sde_connection, "arcsde.SDE.Utilities_DRAINAGE\\ArcSDE.SDE.dGravityMain")
        # subdivision_feature = os.path.join(path_sde_connection, "Subdivisions_Res")

        # temp = "C:\\Temp"
        if not os.path.exists(TEMP):
            os.makedirs(TEMP)
        else:
            shutil.rmtree("C:\\Temp")
            os.makedirs(TEMP)

        file = "SDEConn"
        serverName = "vs329"
        authType = "DATABASE_AUTH"
        username = "sde"
        password = password
        saveUserInfo = "SAVE_USERNAME"
        versionName = "SDE.DEFAULT"

        arcpy.CreateDatabaseConnection_management(TEMP,
                                                  file,
                                                  "SQL_SERVER",
                                                  serverName,
                                                  authType,
                                                  username,
                                                  password,
                                                  saveUserInfo,
                                                  versionName)
        # workspace = os.path.join(temp, file)
        # # Set the workspace environment
        # arcpy.env.workspace = workspace
        # arcpy.env.overwriteOutput = True

        # if int(arcpy.GetCount_management(utility_features)[0]) == 0:
        #     messages.addErrorMessage("{} has no features").format(utility_features)
        # else:
        #     arcpy.AddMessage("Checkpoint 1")
        #     arcpy.Delete_management(workspace)
        #     arcpy.AddMessage("workspace deleted")
        gdb_copy = ProjectIDTool.copy_geodatabase(self,
                                                  subdivision_feature,
                                                  utility_features,
                                                  path_sde_connection)
        joined_feature = r"C:\Users\avenneman\Desktop\Database Tools\Testing.gdb\UtilitySubdivisionJoin"
        # joined_feature = ProjectIDTool.join_utility_subdiv(self,
        #                                                   TEMP,
        #                                                   gdb_copy,
        #                                                   utility_copy,
        #                                                   subdivision_copy)
        arcpy.AddMessage("Checkpoint 2")

        ProjectIDTool.compare_fields(self, path_sde_connection, joined_feature, utility_features)
        arcpy.AddMessage("Checkpoint 3")
        arcpy.Delete_management(bane_of_my_existence)
        shutil.rmtree("C:\\Temp")
        arcpy.AddMessage("workspace deleted")
        endtime = time.asctime(time.localtime(time.time()))
        arcpy.AddMessage(endtime)

        return output_feature


"""
Ignore this below. It is only for testing within PyCharm.
"""


def main():
    tbx = Toolbox()
    tool = ProjectIDTool()
    tool.execute(tool.getParameterInfo(), None)


if __name__ == "__main__":
    main()
