def get_feature_bounding_boxes(shapefile_path):
    """
    从本地 Shapefile 获取每个要素的范围 (bounds)。
    
    :param shapefile_path: Shapefile 文件路径
    :return: 每个要素的 bounding box 列表 (GeoJSON 格式)
    """
    # 使用 GeoPandas 读取 Shapefile
    grid = gpd.read_file(shapefile_path)

    # 保存每个要素的边界范围
    bounding_boxes = []

    for _, row in grid.iterrows():
        # 获取当前要素的几何信息
        geometry = row["geometry"]
        # 获取要素的边界框 (min_lon, min_lat, max_lon, max_lat)
        min_lon, min_lat, max_lon, max_lat = geometry.bounds
        # 保存为 GeoJSON 的区域坐标格式
        bounding_boxes.append([[min_lon, min_lat], [max_lon, max_lat]])

    return bounding_boxes

def download_fabdem(shapefile_path, output_folder, scale=30):
    """
    根据 Shapefile 的范围下载 FABDEM 数据并保存到本地。
    
    :param shapefile_path: Shapefile 文件路径
    :param output_folder: 保存栅格数据的本地文件夹路径
    :param scale: 栅格分辨率，默认为 30 米
    """
    # 加载 FABDEM 数据集
    fabdem = ee.ImageCollection("projects/sat-io/open-datasets/FABDEM").mosaic()

    # 获取 Shapefile 中每个要素的边界框
    bounding_boxes = get_feature_bounding_boxes(shapefile_path)

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历每个边界框并下载数据
    for i, extent in enumerate(bounding_boxes):
        # 定义输出文件名
        output_raster = os.path.join(output_folder, f"FABDEM_{i}.tif")
        
        try:
            # 使用 geemap 下载数据
            print(f"正在下载 FABDEM 数据 {i}...")
            geemap.download_ee_image(
                image=fabdem,
                filename=output_raster,
                region=extent,
                crs="EPSG:4326",
                scale=scale,
            )
            print(f"FABDEM 文件 {i} 已保存到: {output_raster}")
        except Exception as e:
            print(f"下载 FABDEM 数据 {i} 时出错: {e}")
            
shp_path = r"D:\元迁移学习\实验\Data\矢量范围\喀斯特.shp"  # 替换为你的 Shapefile 文件路径
output_folder = r"D:\元迁移学习\实验\Data\附加DEM\喀斯特"       
download_fabdem(shp_path, output_folder)