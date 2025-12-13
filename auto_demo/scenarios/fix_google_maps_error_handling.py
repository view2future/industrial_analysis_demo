#!/usr/bin/env python3
"""
Script to add Google Maps error handling for API loading
"""

def fix_google_maps_api_loading():
    """Add error handling to Google Maps API loading"""
    template_path = "/Users/wangyu94/regional-industrial-dashboard/templates/poi_map_visualization.html"
    
    # Read the current content
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the Google Maps script loading section and add error handling
    # Look for the Google Maps API script tag
    old_script_tag = """<!-- Google Maps API -->
<script async defer
        id="google-maps-script"
        src="https://maps.googleapis.com/maps/api/js?key={{ google_map_key|default('') }}&libraries=visualization,marker&callback=initGoogleMapLoader">
</script>"""
    
    new_script_tag = """<!-- Google Maps API -->
<script async defer
        id="google-maps-script"
        src="https://maps.googleapis.com/maps/api/js?key={{ google_map_key|default('') }}&libraries=visualization,marker&callback=initGoogleMapLoader"
        onerror="handleGoogleMapsError()">
</script>"""
    
    # Also add the error handling function
    new_script_with_handler = new_script_tag + """

<script>
function handleGoogleMapsError() {
    console.error('Google Maps API failed to load, switching to Baidu Maps');
    // Try to initialize Baidu Maps if available
    if (typeof BMap !== 'undefined') {
        if (typeof visualizer !== 'undefined') {
            document.getElementById('google-map').style.display = 'none';
            document.getElementById('baidu-map').style.display = 'block';
            visualizer.initBaiduMap();
        } else {
            // If visualizer isn't defined yet, set a timeout to try again
            setTimeout(() => {
                if (typeof visualizer !== 'undefined') {
                    document.getElementById('google-map').style.display = 'none';
                    document.getElementById('baidu-map').style.display = 'block';
                    visualizer.initBaiduMap();
                }
            }, 1000);
        }
    }
}

// Also add a timeout to handle cases where the callback doesn't fire for other reasons
setTimeout(() => {
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
        // Google Maps API didn't load properly within timeout
        handleGoogleMapsError();
    }
}, 5000);  // 5 second timeout
</script>"""
    
    # Replace the script tag
    updated_content = content.replace(old_script_tag, new_script_with_handler)
    
    # Write back the updated content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("Added Google Maps API error handling and fallback to Baidu Maps!")


if __name__ == "__main__":
    fix_google_maps_api_loading()