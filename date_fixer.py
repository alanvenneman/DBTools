import arcpy
import os
from datetime import datetime


path_sde_connection = "C:\\Users\\%\\Default.sde"
utility_features = os.path.join(path_sde_connection, "ArcSDE.%sGravityMain")

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

# TODO put the year_slice inside an Update or Insert Cursor loop


def year_slice(install, year):
    if install != 'check year' and install != "#":
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


year_slice("", "")
