import arcpy
import tkinter as tk
from tkinter import filedialog

def remove_layers_except_world_imagery():
    """Function to remove all layers except 'World Imagery' and delete grid files."""
    for lyr in m.listLayers():
        if lyr.name != "World Imagery":
            if "Altcrtelyqxgrid" in lyr.name.lower():  # Check if the layer name contains the word "grid"
                grid_path = lyr.dataSource  # Get the data source path of the grid layer
                arcpy.Delete_management(output_grid)  # Delete the grid shapefile from the disk
            m.removeLayer(lyr)

try:
    # ... [Your existing code to load the shapefile]

    root = tk.Tk()
    root.withdraw()  # Hide the main window
    shapefile_path = filedialog.askopenfilename(title="Please select a shapefile", filetypes=[("Shapefiles", "*.shp")])

    # Check the number of polygons in the shapefile
    feature_count = arcpy.GetCount_management(shapefile_path).getOutput(0)

    # If only one polygon, prompt to create grid index
    if int(feature_count) == 1:
        create_grid = input("The shapefile contains only one polygon. Do you want to create a grid index? (yes/no): ")

        if create_grid.lower() == 'yes':
            input_shapefile = shapefile_path

            # Output grid feature class
            #output_grid = "D:\Wind turbine detection\Tiles\shpfile\output.shp"
            output_grid = shapefile_path.replace(".shp", "_Altcrtelyqxgrid.shp")
            # Ask the user for dimensions and unit
            width_value = input("Enter the desired width of the grid cells: ")
            height_value = input("Enter the desired height of the grid cells: ")

            # Ask the user for the unit
            print("Select a dimension unit:")
            print("1. METERS")
            print("2. KILOMETERS")
            print("3. FEET")
            print("4. MILES")
            unit_choice = input("Enter the number corresponding to your choice: ")

            # Convert the user's choice to the appropriate unit
            unit_dict = {
                "1": "Meters",
                "2": "Kilometers",
                "3": "Feet",
                "4": "Miles"
            }
            selected_unit = unit_dict.get(unit_choice, "Kilometers")

            grid_width = f"{width_value} {selected_unit}"
            grid_height = f"{height_value} {selected_unit}"

            # Use the GridIndexFeatures tool to create the grid
            arcpy.cartography.GridIndexFeatures(output_grid, in_features=input_shapefile, polygon_width=grid_width, polygon_height=grid_height)
            for lyr in m.listLayers():
                if lyr.name == 'output':
                    lyr.visible = False
                    break
            print("Grid created successfully!")
            shapefile_path = output_grid  # Update the shapefile path to the new grid index
            #shapefile_path = grid_output_path  # Update the shapefile path to the new grid index




    # ... [Continue with your existing code]
    # Get the current project and map
    p = arcpy.mp.ArcGISProject('current')
    m = p.listMaps()[0]

    # Add the shapefile to the map
    added_layer = m.addDataFromPath(shapefile_path)

    # Get the added layer's CIM definition and URI
    l_cim = added_layer.getDefinition('V2')
    lURI = l_cim.uRI

    # Get the desired layout and its CIM definition
    lyt = p.listLayouts('Layout7')[0]
    lyt_cim = lyt.getDefinition('V2')

    # Create a new CIM Spatial Map Series object and set its properties
    ms = arcpy.cim.CreateCIMObjectFromClassName('CIMSpatialMapSeries', 'V2')
    ms.enabled = True
    ms.mapFrameName = "Map Frame"
    ms.startingPageNumber = 1
    ms.currentPageID = 2
    ms.indexLayerURI = lURI
    ms.nameField = "PageName"
    ms.sortField = "PageName"
    ms.sortAscending = True
    ms.scaleRounding = 100
    ms.extentOptions = "BestFit"
    ms.marginType = "Percent"
    ms.margin = 1

    # Set the new map series to the layout
    lyt_cim.mapSeries = ms
    lyt.setDefinition(lyt_cim)

    # Refresh the layout
    lyt_cim = lyt.getDefinition('V2')
    lyt.setDefinition(lyt_cim)

    # Remove the added layer from the map
    # m.removeLayer(added_layer)

    print("Map series set up successfully!")
    # After processing, delete the grid index shapefile
    # if 'grid_output_path' in locals():  # Check if grid_output_path is defined
    #     arcpy.Delete_management(grid_output_path)
    #     print(f"Grid index shapefile {grid_output_path} deleted.")
    layout=lyt

    # After processing, delete the grid index shapefile
    # if 'grid_output_path' in locals():  # Check if grid_output_path is defined
    #     arcpy.Delete_management(grid_output_path)
    #     print(f"Grid index shapefile {grid_output_path} deleted.")

#     layout = lyt
    create_grid = input("Do you want proceed with download imagery for polygons? (yes/no): ")

    if create_grid.lower() == 'yes':
        if layout.mapSeries is None:
            print("The layout does not have a map series enabled.")
        else:
            ms = layout.mapSeries
            georef_mapframe_name = ms.mapFrame

            for pageNum in range(1, ms.pageCount + 1):
                if pageNum > 4:
                    break
                ms.currentPageNumber = pageNum
                print(f"Exporting page {pageNum}/{ms.pageCount} to GeoTIFF...")
                output_tiff_path = f"E:/Wind_Turbine_Saurabh/TestingTile_download/polygon_" + str(pageNum) + ".tif"
                layout.exportToTIFF(output_tiff_path, resolution=400, world_file=False, geoTIFF_tags=True, georef_mapframe=georef_mapframe_name)

        print("GeoTIFFs created successfully for each polygon!")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    remove_layers_except_world_imagery()
