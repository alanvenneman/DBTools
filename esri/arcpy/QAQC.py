# -*- coding: utf-8 -*-
r""""""
__all__ = ['ProjectIDTool']
__alias__ = 'QAQC'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('ProjectIDTool_QAQC', None)
def ProjectIDTool(utility_feature=None, subdivision_feature=None, database=None, path_sde_connection=None):
    """ProjectIDTool_QAQC(utility_feature, subdivision_feature, database, path_sde_connection)

     INPUTS:
      utility_feature (Feature Layer)
      subdivision_feature (Feature Layer)
      database (Workspace)
      path_sde_connection (ServerConnection)"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.ProjectIDTool_QAQC(*gp_fixargs((utility_feature, subdivision_feature, database, path_sde_connection), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject