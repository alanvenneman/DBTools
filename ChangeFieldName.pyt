# -*- coding: utf-8 -*-

import arcpy
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Change Field Name"
        self.alias = "Field name"

        # List of tool classes associated with this toolbox
        self.tools = [FieldName]


class FieldName(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Change Field Name"
        self.description = "Uses Alter Field to change the field name. Can select one field at a time " + \
            "or enter a string that will be deleted from all fields in the feature if that string is in the " + \
            "field name."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # feature class with the fields to be renamed
        in_features = arcpy.Parameter(
            displayName="Input Features",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        # String containing characters to be removed from field name
        delete_string = arcpy.Parameter(
            displayName="String to Delete",
            name="delete_string",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )

        params = [in_features, delete_string]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # if parameters[0].altered:
        #     parameters[1].value = arcpy.ValidateFieldName(parameters[1].value,
        #                                                   parameters[0].value)
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def field_type_converter(self, old_type):
        """Python reads the data types of Esri tables as 'String', 'Integer', 'Float', 'Date', 'Guid',
        'OID' and 'Geometry'. All the Field geoprocessing tools use different nomenclature that is not a 1:1
        replacement. So I will need to use a try/except block to handle 'Long' and 'Short' types which are both
        Python integers. Text is String, Double is Float, and I think the rest can remain the same."""

        if old_type == 'String':
            new_type = 'Text'
        elif old_type == 'Integer':
            new_type = 'Short'
        elif old_type == 'Date':
            new_type = 'Date'
        elif old_type == 'GlobalID':
            new_type = 'GUID'
        else:
            new_type = 'Double'
        return new_type

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # # Parameters for ArcGIS Pro
        # in_features = parameters[0].valueAsText
        # delete_string = parameters[1].valueAsText

        # Hard coded parameters
        feature_name = "GWTP_AIR_COMRESSOR_HYDROTANK"
        in_features = os.path.join("Default.gdb", feature_name)
        delete_string = "USER"

        all_fields = arcpy.ListFields(in_features)
        arcpy.AddMessage(f"All fields in {in_features}")
        field_names = []

        for a in all_fields:
            field_names.append(a)
            fn = a.name
            ty = a.type
            # run method to set field type. Try block below will switch from Short Integer to Long Integer if the 'alter
            # populated field error' runs.
            new_type = self.field_type_converter(ty)
            arcpy.AddMessage(f"{fn}: {ty}")
            split_name = fn.split('_')
            new_fields = []
            if split_name[0] == delete_string:
                del split_name[0]
                new_fields.append(split_name)
                # Pycharm has an issue with my new_fields saying it is referenced too early. I'm not sure how to
                # resolve this as I have assigned it to an empty list on line 106.
                for n in new_fields:
                    new = "_".join(n)
                    arcpy.AddMessage(new)
                    try:
                        arcpy.AlterField_management(in_features, fn, new, new, new_type)
                        print(f"{fn} Changed to {new}")
                        del new_fields
                        continue
                    except Exception as e:
                        print(f"{e} Trying long integer")
                        new_type = 'Long'
                        arcpy.AlterField_management(in_features, fn, new, new, new_type)
                        print(f"{fn} Changed to {new}")
                        del new_fields
                        continue
                    # except Exception as y:
                    #     print(f"{y} Trying GUID")
                    #     new_type = 'GUID'
                    #     arcpy.AlterField_management(in_features, fn, new, new, new_type)
                    #     print(f"{fn} Changed to {new}")
                    #     del new_fields
                    #     continue


def main():
    """Run this inside PyCharm. Comment out to run in ArcGIS Pro"""
    tbx = Toolbox()
    tool = FieldName()
    tool.execute(tool.getParameterInfo(), None)


if __name__ == "__main__":
    main()
