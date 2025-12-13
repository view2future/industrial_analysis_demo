#!/usr/bin/env python3
"""
Script to improve the map fallback logic in poi_map_visualization.html
This will ensure that if Google Maps fails to load, Baidu Maps is shown as a fallback
"""

def fix_map_fallback():
    """Fix the map fallback logic in the POI visualization template"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/poi_map_visualization.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the part where Google Maps is initialized and ensure proper fallback
    # Look for the init function within the PoiMapVisualizer class
    # We need to update the initialization logic to ensure fallback
    old_init_logic = """    init() {
        // Request user's location for initial centering
        this.getCurrentLocation().catch(err => {
            console.warn('Could not get user location, using default center');
        });
        
        // Determine map type based on API availability
        if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
            this.initGoogleMap();
        } else if (typeof BMap !== 'undefined') {
            this.initBaiduMap();
        } else {
            // Both APIs failed, try to load Google Maps first, then fallback
            this.initGoogleMap();
        }
    }"""
    
    # Updated logic with better fallback handling
    new_init_logic = """    init() {
        // Request user's location for initial centering
        this.getCurrentLocation().catch(err => {
            console.warn('Could not get user location, using default center');
        });
        
        // Set a timeout to show Baidu map if Google Maps doesn't initialize in time
        setTimeout(() => {
            if (!this.googleMapReady && !this.baiduMapReady) {
                // If neither map has initialized, try Baidu if available
                if (typeof BMap !== 'undefined') {
                    this.initBaiduMap();
                    // Switch to Baidu Map view
                    document.getElementById('google-map').style.display = 'none';
                    document.getElementById('baidu-map').style.display = 'block';
                }
            }
        }, 5000); // 5 seconds timeout
        
        // Try to initialize Google Maps first (if API is available)
        if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
            this.initGoogleMap();
        } else {
            // If Google Maps API isn't available, try Baidu
            if (typeof BMap !== 'undefined') {
                this.initBaiduMap();
            } else {
                // If neither is available in global scope, wait for initialization
                // and try again after a short delay
                setTimeout(() => {
                    if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
                        this.initGoogleMap();
                    } else if (typeof BMap !== 'undefined') {
                        this.initBaiduMap();
                    } else {
                        // Last resort: show a message to the user
                        console.error('Both Google Maps and Baidu Maps APIs are unavailable');
                        // Show an error or info message to the user
                        const mapContainer = document.getElementById('google-map');
                        if (mapContainer) {
                            mapContainer.innerHTML = '<div class="text-center p-8 text-gray-600">地图服务暂不可用，请检查网络连接或API配置</div>';
                        }
                    }
                }, 2000);
            }
        }
    }"""
    
    # Replace the initialization logic
    if old_init_logic in content:
        updated_content = content.replace(old_init_logic, new_init_logic)
    else:
        # If the exact old logic isn't found, try a more general replacement
        # Find the init() method and replace the core logic part
        start_marker = "init() {"
        end_marker = "        }\n    }"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            # Find the end of the init method
            method_start = content.find("{", content.find("{", start_pos) + 1)  # First inner brace
            brace_count = 1
            pos = method_start + 1
            
            while brace_count > 0 and pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                pos += 1
            
            if brace_count == 0:
                full_method = content[start_pos:pos]
                
                # Better targeted replacement - just update the core logic part
                if "Determine map type based on API availability" in full_method:
                    updated_method = """    init() {
        // Request user's location for initial centering
        this.getCurrentLocation().catch(err => {
            console.warn('Could not get user location, using default center');
        });
        
        // Set a timeout to show Baidu map if Google Maps doesn't initialize in time
        setTimeout(() => {
            if (!this.googleMapReady && !this.baiduMapReady) {
                // If neither map has initialized, try Baidu if available
                if (typeof BMap !== 'undefined') {
                    this.initBaiduMap();
                    // Switch to Baidu Map view
                    document.getElementById('google-map').style.display = 'none';
                    document.getElementById('baidu-map').style.display = 'block';
                }
            }
        }, 5000); // 5 seconds timeout
        
        // Try to initialize Google Maps first (if API is available)
        if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
            this.initGoogleMap();
        } else {
            // If Google Maps API isn't available, try Baidu
            if (typeof BMap !== 'undefined') {
                this.initBaiduMap();
            } else {
                // If neither is available in global scope, wait for initialization
                // and try again after a short delay
                setTimeout(() => {
                    if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
                        this.initGoogleMap();
                    } else if (typeof BMap !== 'undefined') {
                        this.initBaiduMap();
                    } else {
                        // Last resort: show a message to the user
                        console.error('Both Google Maps and Baidu Maps APIs are unavailable');
                        // Show an error or info message to the user
                        const mapContainer = document.getElementById('google-map');
                        if (mapContainer) {
                            mapContainer.innerHTML = '<div class="text-center p-8 text-gray-600">地图服务暂不可用，请检查网络连接或API配置</div>';
                        }
                    }
                }, 2000);
            }
        }
    }"""
                
                updated_content = content.replace(full_method, updated_method)
            else:
                print("Could not find complete method body, using alternative approach")
                # Fallback: just update the core if-else block
                updated_content = content.replace(
                    '        // Determine map type based on API availability\n        if (typeof google !== \'undefined\' && typeof google.maps !== \'undefined\') {',
                    '        // Try to initialize Google Maps first (if API is available)\n        if (typeof google !== \'undefined\' && typeof google.maps !== \'undefined\') {'
                )
        else:
            print("Could not find init() method, not making changes")
            return

    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Updated the map initialization logic with better fallback handling!")


if __name__ == "__main__":
    fix_map_fallback()