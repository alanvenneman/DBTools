import arcpy
import os
from datetime import datetime


path_sde_connection = "C:\\Users\\GISAdmin\\AppData\\Roaming\\ESRI\\ArcGISPro\\Favorites\\Default.sde"
utility_features = os.path.join(path_sde_connection, "ArcSDE.SDE.Utilities_SANITARY\\ArcSDE.SDE.sGravityMain")

date_to_string = []
rows = arcpy.da.SearchCursor(utility_features, "InstallDate")
for row in rows:
    datetimeVal = row[0]
    if datetimeVal is not None:
        formattedTime = datetime.strftime(datetimeVal, '%Y')
        date_to_string.append(formattedTime)
    else:
        date_to_string.append('check year')
        print('null year')


def year_slice(install, year):
    if install != '' and install != "#":
        if install[-4:-2] == '20' or install[-4:-2] == '19':
            if year != install[-4:]:
                if year == '' or year == '#':
                    print(install[-4:])
                else:
                    print("check {}".format(year))
            elif len(year) == 4:
                print(year)
            else:
                print("check {}".format(year))
        elif len(year) == 4:
            print(year)
        else:
            print("check {}".format(year))
    elif len(year) == 4:
        print(year)
    else:
        print("check {}".format(year))

    # if year != install[-4:-2]:
    # else:
    #     print(f"check {year}")


year_slice("", "")
# print("check {}".format(year))

# def year_slice2(install, year):
#     if year != install[-4:]:
#         if year == '' or year == '#':
#             print(install[-4:])
#         else:
#             print(f"check {year}")
#     else:
#         print(year)
#
#
# year_slice2("2010", "2010")
