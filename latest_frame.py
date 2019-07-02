# import the simple module from the paraview
from paraview.simple import *

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()


def create_field(
    fpath,
    name,
    opacity_setting=1,
    colorbar_range=[0.0, 1.0],
    colorbar_map="Reds",
    show_celldata=True,
    pointdata_filter=False,
    opacity_mapping=True,
):

    range_lower = colorbar_range[0]
    range_upper = colorbar_range[1]

    # create a new 'XDMF Reader'
    xdmf = XDMFReader(FileNames=[fpath])
    xdmf.PointArrayStatus = [name]

    # get active view
    renderView = GetActiveViewOrCreate("RenderView")
    renderView.InteractionMode = "2D"

    # get color transfer function/color map for 'Concentration_A'
    LUT = GetColorTransferFunction(name)

    # update the view to ensure updated data information
    renderView.Update()

    # Properties modified on LUT

    LUT.EnableOpacityMapping = opacity_mapping

    # Apply a preset using its name. Note this may not work as expected when presets have duplicate names.
    LUT.ApplyPreset(colorbar_map, True)

    # invert the transfer function
    LUT.InvertTransferFunction()

    # Rescale transfer function
    LUT.RescaleTransferFunction(range_lower, range_upper)

    # get opacity transfer function/opacity map for 'Concentration_A'
    PWF = GetOpacityTransferFunction(name)

    # Rescale transfer function
    PWF.RescaleTransferFunction(range_lower, range_upper)

    if show_celldata:
        # get display properties
        xdmfDisplay = GetDisplayProperties(xdmf, view=renderView)

        # hide color bar/color legend
        xdmfDisplay.SetScalarBarVisibility(renderView, False)

    if pointdata_filter:
        cellDatatoPointData = CellDatatoPointData(Input=xdmf)

        # show data in view
        cellDatatoPointDataDisplay = Show(cellDatatoPointData, renderView)

    # create dictionary ready for metadata
    component_dict = {
        name: {
            "colorbar": {"min": range_lower, "max": range_upper, "map": colorbar_map},
            "pointdata_filter": pointdata_filter,
            "opacity_mapping": opacity_mapping,
        }
    }
    return component_dict


meta_A = create_field(
    fpath="./Concentration_A/Concentration_A.xdmf",
    name="Concentration_A",
    colorbar_map="Blues",
)
meta_B = create_field(
    fpath="./Concentration_B/Concentration_B.xdmf",
    name="Concentration_B",
    colorbar_map="Greens",
)
meta_C = create_field(
    fpath="./Concentration_C/Concentration_C.xdmf",
    name="Concentration_C",
    colorbar_map="Reds",
    pointdata_filter=True,
    show_celldata=False,
)


animationScene = GetAnimationScene()
animationScene.UpdateAnimationUsingDataTimeSteps()
animationScene.GoToLast()
ResetCamera()

# save screenshot
renderView = GetActiveViewOrCreate("RenderView")
# Hide orientation axes
renderView.OrientationAxesVisibility = 0
SaveScreenshot("output.png", renderView, ImageResolution=[3552, 2732])
