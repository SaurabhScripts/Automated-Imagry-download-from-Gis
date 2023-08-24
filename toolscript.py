import arcpy

def remove_layers_except_world_imagery(m, output_grid):
    """Function to remove all layers except 'World Imagery' and delete grid files."""
    for lyr in m.listLayers():
        if lyr.name != "World Imagery":
            if "tcrtelyqxgrid" in lyr.name.lower():
                arcpy.Delete_management(output_grid)
            m.removeLayer(lyr)

def ScriptTool(shapefile_path, create_grid_choice, output_folder, resolution, width_value, height_value, selected_unit):
    try:
        # Check the number of polygons in the shapefile
        feature_count = arcpy.GetCount_management(shapefile_path).getOutput(0)

        # If only one polygon, prompt to create grid index
        if int(feature_count) == 1 and create_grid_choice.lower() == 'yes':
            input_shapefile = shapefile_path
            output_grid = shapefile_path.replace(".shp", "_Altcrtelyqxgrid.shp")

            grid_width = f"{width_value} {selected_unit}"
            grid_height = f"{height_value} {selected_unit}"

            arcpy.cartography.GridIndexFeatures(output_grid, in_features=input_shapefile, polygon_width=grid_width, polygon_height=grid_height)

            shapefile_path = output_grid

        p = arcpy.mp.ArcGISProject('current')
        m = p.listMaps()[0]
        added_layer = m.addDataFromPath(shapefile_path)
        l_cim = added_layer.getDefinition('V2')
        lURI = l_cim.uRI
        lyt = p.listLayouts('Layout7')[0]
        lyt_cim = lyt.getDefinition('V2')
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
        lyt_cim.mapSeries = ms
        lyt.setDefinition(lyt_cim)
        lyt_cim = lyt.getDefinition('V2')
        lyt.setDefinition(lyt_cim)

        layout = lyt

        if create_grid_choice.lower() == 'yes':
            if layout.mapSeries is None:
                arcpy.AddMessage("The layout does not have a map series enabled.")
            else:
                ms = layout.mapSeries
                georef_mapframe_name = ms.mapFrame
                for pageNum in range(1, ms.pageCount + 1):
                    if pageNum > 4:
                        break
                    ms.currentPageNumber = pageNum
                    output_tiff_path = f"{output_folder}/polygon_" + str(pageNum) + ".tif"
                    layout.exportToTIFF(output_tiff_path, resolution=resolution, world_file=False, geoTIFF_tags=True, georef_mapframe=georef_mapframe_name)

                arcpy.AddMessage("GeoTIFFs created successfully for each polygon!")

    except Exception as e:
        arcpy.AddError(f"An error occurred: {e}")

    finally:
        remove_layers_except_world_imagery(m, output_grid)

if __name__ == '__main__':
    shapefile_path = arcpy.GetParameterAsText(0)
    create_grid_choice = arcpy.GetParameterAsText(1)
    output_folder = arcpy.GetParameterAsText(2)
    resolution = int(arcpy.GetParameterAsText(3))
    width_value = float(arcpy.GetParameterAsText(4))
    height_value = float(arcpy.GetParameterAsText(5))
    selected_unit = arcpy.GetParameterAsText(6)

    ScriptTool(shapefile_path, create_grid_choice, output_folder, resolution, width_value, height_value, selected_unit)
