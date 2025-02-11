import geopandas as gpd
import ee
import os
import geemap

# 认证并初始化 Earth Engine
ee.Authenticate()
ee.Initialize(project="ee-gismaker6")

# 获取 Shapefile 每个要素的边界框
def get_feature_bounding_boxes(shapefile_path):
    grid = gpd.read_file(shapefile_path)
    bounding_boxes = []
    for _, row in grid.iterrows():
        geometry = row["geometry"]
        min_lon, min_lat, max_lon, max_lat = geometry.bounds
        bounding_boxes.append([[min_lon, min_lat], [max_lon, max_lat]])
    return bounding_boxes

# 下载 DEM 数据（FABDEM / ASTER GDEM / BOTH）
def download_dem(shapefile_path, output_folder, dem_type="BOTH", scale=30):
    """
    根据 Shapefile 下载 FABDEM 或 ASTER GDEM，并保存到本地。
    
    :param shapefile_path: Shapefile 文件路径
    :param output_folder: 保存栅格数据的本地文件夹路径
    :param dem_type: 选择要下载的 DEM 类型: "FABDEM", "ASTERDEM", "BOTH"
    :param scale: 栅格分辨率，默认 30m
    """
    # Earth Engine 数据集
    fabdem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM").mosaic()
    aster_dem = ee.Image("NASA/NASADEM_HGT/001").select("elevation")

    # 获取 Shapefile 每个要素的边界框
    bounding_boxes = get_feature_bounding_boxes(shapefile_path)

    # 创建存储目录
    if dem_type in ["FABDEM", "BOTH"]:
        fabdem_folder = os.path.join(output_folder, "FABDEM")
        os.makedirs(fabdem_folder, exist_ok=True)

    if dem_type in ["ASTERDEM", "BOTH"]:
        aster_folder = os.path.join(output_folder, "ASTERDEM")
        os.makedirs(aster_folder, exist_ok=True)

    # 遍历边界框并下载数据
    for i, extent in enumerate(bounding_boxes):
        if dem_type in ["FABDEM", "BOTH"]:
            fabdem_raster = os.path.join(fabdem_folder, f"FABDEM_{i}.tif")
            try:
                print(f"正在下载 FABDEM {i}...")
                geemap.download_ee_image(image=fabdem, filename=fabdem_raster, region=extent, crs="EPSG:4326", scale=scale)
                print(f"✅ FABDEM {i} 下载完成: {fabdem_raster}")
            except Exception as e:
                print(f"❌ FABDEM {i} 下载失败: {e}")

        if dem_type in ["ASTERDEM", "BOTH"]:
            aster_raster = os.path.join(aster_folder, f"ASTERDEM_{i}.tif")
            try:
                print(f"正在下载 ASTER GDEM {i}...")
                geemap.download_ee_image(image=aster_dem, filename=aster_raster, region=extent, crs="EPSG:4326", scale=scale)
                print(f"✅ ASTER GDEM {i} 下载完成: {aster_raster}")
            except Exception as e:
                print(f"❌ ASTER GDEM {i} 下载失败: {e}")

# === 运行代码 ===
shp_path = r"D:\青藏高原地形超分\青藏高原\范围\训练样区.shp"
output_folder = r"D:\青藏高原地形超分\青藏高原\范围\AsterDEM"

# 选择下载模式："FABDEM", "ASTERDEM", "BOTH"
download_dem(shp_path, output_folder, dem_type="ASTERDEM")  # 这里可以改为 "FABDEM" 或 "ASTERDEM"
