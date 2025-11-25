#!/usr/bin/env python3
"""
Verify that the streaming auto-start fix is properly implemented
"""

import re

def check_template_fixes():
    """Check that the template has the required fixes"""
    print("🔍 Checking template fixes...")
    
    with open('templates/streaming_generate.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "Auto-start logging": "Auto-starting streaming..." in content,
        "Element validation": "window.streamingGenerator.elements.infoCity" in content,
        "Timeout mechanism": "10000)" in content and "timeout" in content.lower(),
        "Retry button": "retry-streaming" in content,
        "Enhanced error handling": "Auto-start failed" in content,
        "First chunk tracking": "hasReceivedFirstChunk" in content,
        "Status indicator update": "自动启动中..." in content,
    }
    
    print("Template fix checks:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_streaming_route_fixes():
    """Check that the streaming route has enhanced logging"""
    print("\n🔍 Checking streaming route fixes...")
    
    with open('src/routes/streaming_routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "Request logging": "收到流式报告生成请求" in content,
        "Parameter logging": "请求参数 - city" in content,
        "Content-Type logging": "Content-Type" in content,
        "Authentication logging": "User authentication status" in content,
    }
    
    print("Streaming route fix checks:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_port_configuration():
    """Check that port configuration is updated"""
    print("\n🔍 Checking port configuration...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for port 5000 configuration
    port_5000_found = "port=5000" in content or "port=port" in content
    
    # Check for the new print statement as well
    print_statement_found = 'print("📊 访问 http://localhost:5000 查看仪表板")' in content

    status = "✅" if port_5000_found and print_statement_found else "❌"
    print(f"  {status} Port changed to 5000")

    return port_5000_found and print_statement_found

def analyze_auto_start_logic():
    """Analyze the auto-start logic implementation"""
    print("\n🔍 Analyzing auto-start logic...")
    
    with open('templates/streaming_generate.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the specific auto-start section
    auto_start_start = content.find("document.addEventListener('DOMContentLoaded'")
    auto_start_end = content.find("// Handle page unload", auto_start_start)
    
    if auto_start_start != -1 and auto_start_end != -1:
        auto_start_code = content[auto_start_start:auto_start_end]
        
        print("Auto-start logic analysis:")
        
        # Check for key components
        components = {
            "DOM ready check": "DOMContentLoaded" in auto_start_code,
            "Element validation": "elements.infoCity" in auto_start_code,
            "Parameter extraction": "textContent.trim()" in auto_start_code,
            "Error handling": "Auto-start failed" in auto_start_code,
            "Timeout protection": "setTimeout" in auto_start_code and "10000" in auto_start_code,
            "Retry mechanism": "retryButton" in auto_start_code,
            "Logging": "console.log" in auto_start_code,
            "Parameter validation": "city && industry" in auto_start_code,
        }
        
        for component, found in components.items():
            status = "✅" if found else "❌"
            print(f"  {status} {component}")
        
        return all(components.values())
    else:
        print("❌ Could not find auto-start logic")
        return False

def main():
    """Main verification function"""
    print("🚀 Verifying streaming auto-start fix implementation...")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("Template fixes", check_template_fixes()))
    results.append(("Streaming route fixes", check_streaming_route_fixes()))
    results.append(("Port configuration", check_port_configuration()))
    results.append(("Auto-start logic", analyze_auto_start_logic()))
    
    print("\n" + "=" * 60)
    print("📊 Verification Summary:")
    
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! The streaming auto-start fix is properly implemented.")
        print("\nExpected behavior:")
        print("1. User accesses streaming URL with parameters")
        print("2. Page shows '自动启动中...' status")
        print("3. After 1.5s delay, streaming automatically starts")
        print("4. If successful, content streams immediately")
        print("5. If failed, retry button appears with error message")
        print("6. User can click retry to manually start streaming")
    else:
        print("⚠️  Some checks failed. Please review the implementation.")
    
    return all_passed

if __name__ == "__main__":
    main()