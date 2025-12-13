#!/usr/bin/env python3
"""
Script to improve the map initialization logic in poi_map_visualization.html
"""

def fix_map_init_logic():
    """Fix the map initialization logic to improve Google Maps fallback"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/poi_map_visualization.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the existing init method with improved fallback
    old_init = """    init() {
        // Prefer Google Maps; if not ready yet, wait briefly before fallback to Baidu
        if (typeof google !== 'undefined' && google.maps) {
            this.initGoogleMap();
        } else {
            setTimeout(() => {
                if (typeof google !== 'undefined' && google.maps) {
                    this.initGoogleMap();
                } else {
                    this.initBaiduMap();
                }
            }, 1200);
        }
    }"""
    
    new_init = """    init() {
        // Set a timeout to show Baidu map if Google Maps doesn't initialize in time
        setTimeout(() => {
            if (!this.googleMapReady && !this.baiduMapReady) {
                // If Google Maps still not ready after timeout, initialize Baidu if available
                if (typeof BMap !== 'undefined') {
                    // Switch to Baidu Map view first
                    document.getElementById('google-map').style.display = 'none';
                    document.getElementById('baidu-map').style.display = 'block';
                    this.initBaiduMap();
                }
            }
        }, 3000); // 3 seconds timeout for Google Maps initialization
        
        // Prefer Google Maps; if not ready yet, wait briefly before fallback to Baidu
        if (typeof google !== 'undefined' && google.maps) {
            this.initGoogleMap();
        } else {
            setTimeout(() => {
                if (typeof google !== 'undefined' && google.maps) {
                    this.initGoogleMap();
                } else {
                    // Google Maps still not available, initialize Baidu Maps
                    if (typeof BMap !== 'undefined') {
                        document.getElementById('google-map').style.display = 'none';
                        document.getElementById('baidu-map').style.display = 'block';
                        this.initBaiduMap();
                    } else {
                        // Neither map is available, show error message
                        console.error('Neither Google Maps nor Baidu Maps APIs are available');
                        const googleMapContainer = document.getElementById('google-map');
                        const baiduMapContainer = document.getElementById('baidu-map');
                        if (googleMapContainer) {
                            googleMapContainer.innerHTML = '<div class="text-center p-8 text-gray-600">地图服务暂不可用，请检查网络连接或API配置</div>';
                            googleMapContainer.style.display = 'block';
                        }
                        if (baiduMapContainer) {
                            baiduMapContainer.style.display = 'none';
                        }
                    }
                }
            }, 1200);
        }
    }"""
    
    # Replace the init method
    updated_content = content.replace(old_init, new_init)
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Updated the map initialization logic with improved fallback handling!")


if __name__ == "__main__":
    fix_map_init_logic()